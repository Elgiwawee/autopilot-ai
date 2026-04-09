# ai_engine/autopilot_engine.py

import logging
from django.utils import timezone
from django.db import transaction

from ai_engine.models.autopilot_run import AutopilotRun
from ai_engine.autopilot.learning import learn_from_outcome
from cloud.services.infra import sync_cloud_account_resources
from cloud.models import CloudResource
from cloud.services import accounts
from cloud.services.accounts import get_active_cloud_accounts
from monitoring.services.metrics_collector import collect_metrics
from cloud.providers.factory import get_provider
from cloud.services.gpu_metrics import get_gpu_utilization
from ai_engine.services.recommendation_service import generate_recommendations
from actions.services.decision_service import make_decision
from actions.services.executor import execute_plan
from accounts.services.autopilot_service import AutopilotService
from ai_engine.autopilot.safety import can_act
from ai_engine.autopilot.rollback import rollback_if_needed
from ai_engine.time_gate import within_maintenance_window
from ai_engine.utilization import utilization_profile
from ai_engine.policy_engine import evaluate_policy
from ai_engine.policies import autopilot_policy_check
from cloud.control_planes.factory import get_control_plane
from control_plane.services.billing_guard import assert_billing_in_good_standing

logger = logging.getLogger(__name__)


class AutopilotEngine:
    """
    Enterprise-grade autonomous cloud optimization engine.
    Features:
    - Organization-level policy enforcement
    - Fault isolation per account
    - Transaction-safe execution
    - Observability (logs + metrics)
    - Safe execution with rollback support
    """

    def run_for_organization(self, organization):

        run = AutopilotRun.objects.create(
            organization=organization,
            status="running",
            started_at=timezone.now(),
        )

        plans_generated = 0
        plans_executed = 0
        plans_failed = 0

        try:

            # =============================
            # 1️⃣ GLOBAL SAFETY GATE
            # =============================
            if not can_act(organization):
                return self._stop_run(run, "blocked")

            # =============================
            # 2️⃣ MAINTENANCE WINDOW CHECK
            # =============================
            if not within_maintenance_window(organization):
                return self._stop_run(run, "outside_window")

            accounts = get_active_cloud_accounts(organization)

            # =============================
            # 3️⃣ LOOP THROUGH ACCOUNTS
            # =============================
            for account in accounts:

                logger.info(f"[AUTOPILOT] Processing account {account.id}")

                try:
                    self._process_account(
                        account,
                        organization,
                        run,
                        stats={
                            "generated": plans_generated,
                            "executed": plans_executed,
                            "failed": plans_failed,
                        }
                    )

                except Exception:
                    logger.exception(f"[AUTOPILOT] Account failure {account.id}")
                    continue  # isolate failure per account

            # =============================
            # 4️⃣ POST-EXECUTION SAFETY
            # =============================
            rollback_if_needed(organization)

            # =============================
            # 5️⃣ FINALIZE RUN
            # =============================
            run.plans_generated = plans_generated
            run.plans_executed = plans_executed
            run.plans_failed = plans_failed
            run.status = "completed"
            run.finished_at = timezone.now()
            run.save()

        except Exception:
            logger.exception(f"[AUTOPILOT] CRASH org={organization.id}")
            return self._stop_run(run, "failed")

    # =========================================================
    # 🔹 ACCOUNT PROCESSING (ISOLATED UNIT)
    # ========================================================
    def _process_account(self, account, organization, run, stats):
        
        assert_billing_in_good_standing(organization)
        provider = get_provider(account)

        # sync first to ensure we have the latest resource data before generating plans
        sync_cloud_account_resources(account)

        # 1️⃣ REAL INFRA (SOURCE OF TRUTH)
        resources = CloudResource.objects.filter(
            cloud_account=account
        )

        resource_ids = [r["resource_id"] for r in resources]

        # 2️⃣ METRICS (existing system)
        metrics = collect_metrics(account)

        # 3️⃣ GPU SIGNAL (NEW $$$ FEATURE)
        gpu_usage = get_gpu_utilization(account, resource_ids)

        # 4️⃣ PASS EVERYTHING INTO AI
        plans = generate_recommendations(
            account=account,
            metrics=metrics,
            resources=resources,          
            gpu_usage=gpu_usage           
        )
        for plan in plans:
            try:
                self._process_plan(plan, stats)
                stats["generated"] += 1
            except Exception:
                stats["failed"] += 1
                logger.exception(f"[AUTOPILOT] Plan failed {plan.id}")

    # =========================================================
    # 🔹 PLAN PROCESSING PIPELINE
    # =========================================================
    def _process_plan(self, plan, stats):

        # =============================
        # 1️⃣ DECISION ENGINE
        # =============================
        utilization = utilization_profile(plan.resource)
        decision = make_decision(plan)

        if not decision.auto_execute_allowed:
            logger.info(f"Plan {plan.id} blocked by decision engine")
            return

        # =============================
        # 2️⃣ ORG POLICY CHECK
        # =============================
        allowed, reason = evaluate_policy(
            plan.resource,
            plan.action_type
        )

        if not allowed:
            logger.warning(f"Plan {plan.id} blocked (ORG): {reason}")
            return

        # =============================
        # 3️⃣ GLOBAL POLICY CHECK
        # =============================
        allowed, reason = autopilot_policy_check(
            plan.resource,
            plan.action_type
        )

        if not allowed:
            logger.warning(f"Plan {plan.id} blocked (GLOBAL): {reason}")
            return
        
        # =============================
        # 4️⃣ SAFE EXECUTION (TRANSACTION)
        # =============================
        with transaction.atomic():

            status = AutopilotService.get_effective_status(
                organization=plan.organization,
                cloud=plan.resource.cloud_account.provider.slug
            )

            if status["effective_status"] != "ACTIVE":
                return

            if (
                status["max_risk_allowed"] is not None and
                decision.risk_score > status["max_risk_allowed"]
            ):
                logger.warning(f"Plan {plan.id} skipped due to risk threshold")
                return

            # 🔥 EXECUTION ONLY HAPPENS HERE
            control_plane = get_control_plane(plan.resource)

            if control_plane:
                execution = control_plane.execute_action(plan.action)
            else:
                execution = execute_plan(plan)

            stats["executed"] += 1


            # =============================
            # 5️⃣ LEARNING FEEDBACK LOOP
            # =============================
            learn_from_outcome(
                plan,
                execution,
                utilization,
                decision,
            )

    # =========================================================
    # 🔹 STOP HANDLER
    # =========================================================
    def _stop_run(self, run, status):
        run.status = status
        run.finished_at = timezone.now()
        run.save()
        return run