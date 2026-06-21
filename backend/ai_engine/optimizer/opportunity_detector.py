# ai_engine/optimizer/opportunity_detector.py
from decimal import Decimal
from monitoring.services.metrics_collector import collect_metrics
from ai_engine.optimizer.opportunity_rules import OpportunityRules
from ai_engine.models.opportunity import OptimizationOpportunity
from actions.services.plan_builder import PlanBuilder
from ai_engine.storage.gp3_rules import gp2_to_gp3_candidate
from ai_engine.storage.planner import generate_gp3_plan
from ai_engine.storage.zombie import is_zombie, generate_delete_plan
from ai_engine.storage.snapshots import analyze_snapshots
from cloud.models import CloudResource
from actions.models import ExecutionPlan
from ai_engine.gpu.models import GPUMetric
from ai_engine.gpu.features import extract_features
from ai_engine.gpu.infer import gpu_decision

class OpportunityDetector:
    """
    Uses real monitoring metrics to detect optimization opportunities.
    """

    def run(self, cloud_account):

        rules = OpportunityRules()
        builder = PlanBuilder()

        # -----------------------------
        # 1️⃣ METRICS-BASED DETECTION (EXISTING)
        # -----------------------------
        metrics = collect_metrics(cloud_account)

        opportunities = rules.detect_compute_opportunities(metrics)

        created_plans = []

        for opp in opportunities:

            opportunity = OptimizationOpportunity.objects.create(
                cloud_account_id=cloud_account.id,
                resource_type=opp["resource_type"],
                resource_id=opp["resource_id"],
                action_type=opp["action_type"],
                estimated_savings=opp["estimated_savings"],
            )

            plan = builder.build_plan(
                cloud_account=cloud_account,
                resource_type=opp["resource_type"],
                resource_id=opp["resource_id"],
                action_type=opp["action_type"],
            )

            if plan:
                opportunity.converted_to_plan = True
                opportunity.save(update_fields=["converted_to_plan"])
                created_plans.append(plan)

        # -----------------------------
        # 2️⃣ STORAGE DETECTION (EXISTING)
        # -----------------------------
        volumes = CloudResource.objects.filter(
            cloud_account=cloud_account,
            resource_type="volume"
        )

        snapshots = CloudResource.objects.filter(
            cloud_account=cloud_account,
            resource_type="snapshot"
        )

        storage_plans = self.detect_storage_opportunities(
            volumes=volumes,
            snapshots=snapshots
        )

        created_plans.extend(storage_plans)

        # -----------------------------
        # GPU AI DETECTION
        # -----------------------------

        self.detect_gpu_opportunities(
            cloud_account
        )

        # -----------------------------
        # 3️⃣ 🔥 FALLBACK EC2 DETECTION (NEW)
        # -----------------------------
        self.detect_ec2_fallback(cloud_account)

        return created_plans
    
    def detect_storage_opportunities(self, volumes, snapshots):

        plans = []

        # GP2 → GP3
        for volume in volumes:
            if gp2_to_gp3_candidate(volume):
                plans.append(generate_gp3_plan(volume))

        # Zombie volumes
        for volume in volumes:
            if is_zombie(volume):
                plans.append(generate_delete_plan(volume))

        # Snapshot cleanup
        snapshot_plans = analyze_snapshots(snapshots)
        plans.extend(snapshot_plans)

        return plans
    
    def detect_ec2_fallback(self, cloud_account):
        """
        Fallback detection when metrics are missing
        Uses CloudResource directly
        """
        generated = set()
        resources = CloudResource.objects.filter(
            cloud_account=cloud_account,
            resource_type__in=["vm", "ec2"],
        )

        for res in resources:

            monthly_cost = (res.cost_per_hour or 0) * 24 * 30

            print(
                f"Processing {res.external_id} "
                f"state={res.state} "
                f"cost={res.cost_per_hour}"
            )

            if res.state == "stopped":
                print(f"Creating TERMINATE plan for {res.external_id}")

                self.create_plan(
                    res,
                    "TERMINATE",
                    monthly_cost,
                    0.95
                )

                generated.add(
                    (
                        res.external_id,
                        "TERMINATE",
                    )
                )

            elif res.cost_per_hour and res.cost_per_hour > Decimal("0.08"):
                print(f"Creating RIGHTSIZE plan for {res.external_id}")

                self.create_plan(
                    res,
                    "RIGHTSIZE",
                    monthly_cost * Decimal("0.4"),
                    0.8
                )

                generated.add(
                    (
                        res.external_id,
                        "RIGHTSIZE",
                    )
                )

            else:
                print(f"Creating RECOMMEND plan for {res.external_id}")

                self.create_plan(
                    res,
                    "RECOMMEND",
                    monthly_cost * Decimal("0.1"),
                    0.6
                )

                generated.add(
                    (
                        res.external_id,
                        "RECOMMEND",
                    )
                )

        for plan in ExecutionPlan.objects.filter(
            cloud_account=cloud_account,
            status__in=[
                "PLANNED",
                "APPROVED",
            ],
        ):
            key = (
                plan.resource_id,
                plan.action_type,
            )

            if key not in generated:
                plan.status = "SUPERSEDED"
                plan.save(update_fields=["status"])

    def create_plan(self, resource, action, savings, confidence):
        """
        Create an OptimizationPlan from a discovered CloudResource.
        Avoid duplicate ACTIVE plans while allowing future recommendations.
        """

        print(
            f"create_plan called: "
            f"{resource.external_id} "
            f"{action}"
        )


        current_state = {
            "state": resource.state,
            "resource_type": resource.resource_type,
            "region": resource.region,
            "cost_per_hour": float(resource.cost_per_hour or 0),
        }

        if action == "TERMINATE":
            proposed_state = {
                "state": "terminated",
            }

        elif action == "RIGHTSIZE":
            proposed_state = {
                "state": resource.state,
                "action": "resize_to_smaller_instance",
            }

        elif action == "SPOT":
            proposed_state = {
                "state": resource.state,
                "action": "migrate_to_spot",
            }

        else:
            proposed_state = {
                "state": resource.state,
                "action": "review",
            }

        # ------------------------------------
        # Prevent duplicate ACTIVE plans only
        # ------------------------------------

        existing = (
            ExecutionPlan.objects.filter(
                cloud_account=resource.cloud_account,
                provider_resource_id=resource.external_id,
                action=action,
            )
            .exclude(
                status__in=[
                    "committed",
                    "rolled_back",
                    "failed",
                ]
            )
            .order_by("-created_at")
            .first()
        )

        if existing:
            existing.current_state = current_state
            existing.proposed_state = proposed_state
            existing.estimated_monthly_savings = savings
            existing.confidence = confidence

            existing.save(
                update_fields=[
                    "current_state",
                    "proposed_state",
                    "estimated_monthly_savings",
                    "confidence",
                ]
            )

            print(
                f"Updated existing optimization plan {existing.id}"
            )

            return existing

        
        plan = ExecutionPlan.objects.create(
            cloud_account=resource.cloud_account,
            resource=resource,
            resource_type=resource.resource_type.upper(),
            provider_resource_id=resource.external_id,
            target_name=resource.name or "",
            action=action,
            parameters={},
            current_state=current_state,
            proposed_state=proposed_state,
            estimated_monthly_savings=savings,
            confidence=confidence,
            risk_score=0,
            status="planned",
        )

        print(f"Created new optimization plan {plan.id}")

        return plan
    
    def detect_gpu_opportunities(
        self,
        cloud_account,
    ):
        """
        Uses ML model to detect underutilized GPUs.
        """

        gpu_resources = CloudResource.objects.filter(
            cloud_account=cloud_account,
            resource_type="gpu",
        )

        for gpu in gpu_resources:

            metrics = GPUMetric.objects.filter(
                workload_id=gpu.external_id,
            ).order_by("-timestamp")[:100]

            if metrics.count() < 5:
                continue

            features = extract_features(metrics)

            p95 = features[1]

            decision = gpu_decision(
                features,
                p95,
            )

            if decision != "DOWNGRADE_GPU":
                continue

            monthly_cost = (
                gpu.cost_per_hour or 0
            ) * 24 * 30

            self.create_plan(
                resource=gpu,
                action="RIGHTSIZE",
                savings=monthly_cost * Decimal("0.35"),
                confidence=0.88,
            )