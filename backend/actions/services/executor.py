# actions/services/executor.py

import logging

from django.db import transaction

from accounts.models import GlobalSafety
from actions.models import ActionExecution, ExecutionPlan
from ai_engine.reinforcement.policy import OptimizationPolicy
from audit.services.writer import write_audit_log
from control_plane.services.autopilot_guard import AutopilotGuard

logger = logging.getLogger(__name__)


def _plan_resource_label(plan: ExecutionPlan) -> str:
    resource_name = getattr(plan.resource, "name", None) if plan.resource else None
    return (
        plan.target_name
        or plan.provider_resource_id
        or resource_name
        or str(plan.id)
    )


@transaction.atomic
def execute_plan(plan: ExecutionPlan, actor="autopilot"):
    """
    Execute a single execution plan with full safety, audit, and rollback awareness.
    """

    resource_label = _plan_resource_label(plan)

    # 1️⃣ GLOBAL SAFETY (HARD KILL SWITCH)
    safety = GlobalSafety.objects.first()
    if not safety or not safety.autopilot_enabled:
        write_audit_log(
            organization=plan.cloud_account.organization,
            actor="AUTOPILOT",
            action=plan.action,
            resource_id=resource_label,
            status="BLOCKED",
            metadata={
                "cloud": plan.cloud_account.provider.code,
                "risk_score": plan.risk_score,
                "savings": float(plan.estimated_monthly_savings),
            },
        )
        raise RuntimeError("Execution blocked by Global Safety switch")

    # 2️⃣ STATE VALIDATION
    if plan.status not in ["planned", "canary"]:
        raise RuntimeError(f"Invalid execution state: {plan.status}")

    # 3️⃣ ORGANIZATION / ACCOUNT SAFETY POLICY
    AutopilotGuard.validate_account_access(
        cloud_account=plan.cloud_account,
        risk_score=plan.risk_score,
        action=plan.action,
    )

    # 4️⃣ RL POLICY DECISION
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
            resource_id=resource_label,
            status="SKIPPED",
            metadata={
                "risk_score": plan.risk_score,
                "estimated_savings": float(plan.estimated_monthly_savings),
            },
        )

        plan.status = "skipped_policy"
        plan.save(update_fields=["status"])

        return plan

    # 5️⃣ QUEUE EXECUTION
    plan.status = "queued"
    plan.save(update_fields=["status"])

    execution = ActionExecution.objects.create(
        plan=plan,
        status="pending",
    )

    write_audit_log(
        organization=plan.cloud_account.organization,
        actor=actor,
        action=plan.action,
        resource_id=resource_label,
        status="QUEUED",
        metadata={
            "confidence": plan.confidence,
            "risk_score": plan.risk_score,
            "estimated_savings": float(plan.estimated_monthly_savings),
        },
    )

    from actions.tasks import execute_action

    transaction.on_commit(lambda: execute_action.delay(str(execution.id)))

    return execution