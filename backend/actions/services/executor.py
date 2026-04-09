# actions/services/executor.py

import logging
from django.db import transaction
from actions.models import ActionExecution
from accounts.models import GlobalSafety
from actions.models import ExecutionPlan
from audit.services.writer import write_audit_log
from cloud.executors.factory import get_cloud_executor
from billing.services.trigger import trigger_savings_computation
from control_plane.services.safety import assert_autopilot_allowed
from ai_engine.reinforcement.policy import OptimizationPolicy
from ai_engine.reinforcement.trainer import RLTrainer
from control_plane.services.billing_guard import (
    assert_billing_in_good_standing
)

logger = logging.getLogger(__name__)


@transaction.atomic
def execute_plan(plan: ExecutionPlan, actor="autopilot"):
    """
    Execute a single execution plan with full safety, audit, and rollback awareness.
    """

    # 1️⃣ GLOBAL SAFETY (HARD KILL SWITCH)
    safety = GlobalSafety.objects.first()
    if not safety or not safety.autopilot_enabled:
        write_audit_log(
            organization=plan.organization,
            actor="AUTOPILOT",
            action=plan.action_type,
            resource_id=str(plan.resource.id),
            status=execution.status, #status="BLOCKED"
            metadata={
                "cloud": plan.resource.cloud_account.provider.slug,
                "risk_score": execution.decision.risk_score,
                "savings": plan.estimated_savings,
            }
        )
        raise RuntimeError("Execution blocked by Global Safety switch")

    # 2️⃣ STATE VALIDATION
    if plan.status not in ["planned", "canary"]:
        raise RuntimeError(f"Invalid execution state: {plan.status}")

    # 3️⃣ ORGANIZATION / ACCOUNT SAFETY POLICY
    assert_autopilot_allowed(
        cloud_account=plan.cloud_account,
        risk_score=plan.risk_score,
        action=plan.action,
    )

    # 4️⃣ RL POLICY DECISION (AI decides if execution is worth it)
    policy = OptimizationPolicy()

    should_execute = policy.should_execute(
        action=plan.action,
        risk_score=plan.risk_score,
        estimated_savings=plan.estimated_monthly_savings,
    )

    if not should_execute:
        write_audit_log(
            organization=plan.cloud_account.organization,
            actor=actor,
            action="EXECUTION_SKIPPED_BY_POLICY",
            resource_id=str(plan.id),
            status="SKIPPED",
            metadata={
                "risk_score": plan.risk_score,
                "estimated_savings": float(plan.estimated_monthly_savings),
            },
        )

        plan.status = "skipped_policy"
        plan.save(update_fields=["status"])

        return plan

    # 5️⃣ RESOLVE CLOUD EXECUTOR (AWS / GCP / AZURE)
    executor = get_cloud_executor(plan.cloud_account)

    # 6️⃣ EXECUTION
    try:
        executor.execute(
            target_type=plan.resource.resource_type,
            namespace=getattr(plan.resource, "namespace", None),
            target_name=plan.resource.external_id,
            action=plan.action,
            parameters=plan.parameters,
        )
    except Exception as exc:
        plan.status = "failed"
        plan.save(update_fields=["status"])

        write_audit_log(
            organization=plan.cloud_account.organization,
            actor=actor,
            action=plan.action,
            resource_id=plan.target_name,
            status="FAILED",
            metadata={
                "cloud": plan.cloud_account.provider,
                "error": str(exc),
            },
        )

        logger.exception("Execution failed")
        raise

    # 7️⃣ COMMIT STATE
    plan.status = "committed"
    plan.save(update_fields=["status"])

    # 8️⃣ IMMUTABLE AUDIT LOG (NON-NEGOTIABLE)
    write_audit_log(
        organization=plan.cloud_account.organization,
        actor=actor,
        action=plan.action,
        resource_id=plan.target_name,
        status="SUCCESS",
        metadata={
            "cloud": plan.cloud_account.provider,
            "confidence": plan.confidence,
            "risk_score": plan.risk_score,
        },
    )

    # 9️⃣ BILLING SAFETY CHECK
    assert_billing_in_good_standing(
        plan.cloud_account.organization
    )

    execution = ActionExecution.objects.create(
        action_plan=plan,
        status="success",
    )

    trigger_savings_computation(execution) 

    # =============================
    # 🔥 RL TRAINING HOOK
    # =============================
    try:
        RLTrainer().update(plan.action_type)
    except Exception:
        pass

    return plan, execution