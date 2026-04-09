# ai_engine/optimizer/opportunity_detector.py

from monitoring.services.metrics_collector import collect_metrics
from ai_engine.optimizer.opportunity_rules import OpportunityRules
from ai_engine.models.opportunity import OptimizationOpportunity
from actions.services.plan_builder import PlanBuilder
from ai_engine.storage.gp3_rules import gp2_to_gp3_candidate
from ai_engine.storage.planner import generate_gp3_plan
from ai_engine.storage.zombie import is_zombie, generate_delete_plan
from ai_engine.storage.snapshots import analyze_snapshots
from cloud.models import CloudResource
from actions.models import OptimizationPlan

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
        storage_plans = self.detect_storage_opportunities(
            volumes=cloud_account.get_volumes(),
            snapshots=cloud_account.get_snapshots()
        )
        created_plans.extend(storage_plans)

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

        resources = CloudResource.objects.filter(
            cloud_account=cloud_account,
            resource_type="ec2"
        )

        for res in resources:

            monthly_cost = (res.cost_per_hour or 0) * 24 * 30

            # -----------------------------
            # STOPPED INSTANCE
            # -----------------------------
            if res.state == "stopped":
                self.create_plan(
                    res,
                    "TERMINATE",
                    monthly_cost,
                    0.95
                )

            # -----------------------------
            # EXPENSIVE INSTANCE
            # -----------------------------
            elif res.cost_per_hour and res.cost_per_hour > 0.08:
                self.create_plan(
                    res,
                    "RIGHTSIZE",
                    monthly_cost * 0.4,
                    0.8
                )

            # -----------------------------
            # LOW IMPACT
            # -----------------------------
            else:
                self.create_plan(
                    res,
                    "RECOMMEND",
                    monthly_cost * 0.1,
                    0.6
                )

    def create_plan(self, resource, action, savings, confidence):
        OptimizationPlan.objects.get_or_create(
            cloud_account=resource.cloud_account,
            resource_id=resource.external_id,
            resource_type="EC2",
            action_type=action,
            defaults={
                "estimated_monthly_savings": savings,
                "confidence": confidence,
                "status": "PLANNED",
            }
        )