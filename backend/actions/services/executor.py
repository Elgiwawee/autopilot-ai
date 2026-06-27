# actions/services/executor.py

import logging

from django.db import transaction

from actions.models import (
    ActionExecution,
    ExecutionPlan,
)

from audit.services.writer import write_audit_log

from ai_engine.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _resource_label(plan: ExecutionPlan) -> str:
    resource_name = (
        getattr(plan.resource, "name", None)
        if plan.resource
        else None
    )

    return (
        plan.target_name
        or plan.provider_resource_id
        or resource_name
        or str(plan.id)
    )


@transaction.atomic
def execute_plan(
    plan: ExecutionPlan,
    actor="AUTOPILOT",
):
    """
    Enterprise execution orchestrator.

    Responsibilities

    • call ApprovalEngine
    • create ActionExecution
    • queue Celery worker

    No policy decisions happen here.
    """

    ########################################################
    # Approval Engine
    ########################################################

    decision = ApprovalEngine.process(plan)

    ########################################################
    # Blocked
    ########################################################

    if not decision.allowed:

        write_audit_log(
            organization=plan.cloud_account.organization,
            actor=actor,
            action="POLICY_BLOCKED",
            resource_id=_resource_label(plan),
            status="BLOCKED",
            metadata={
                "reason": decision.reason,
                "risk_level": decision.risk_level,
            },
        )

        return None

    ########################################################
    # Waiting for manual approval
    ########################################################

    if decision.requires_approval:

        write_audit_log(
            organization=plan.cloud_account.organization,
            actor=actor,
            action="WAITING_APPROVAL",
            resource_id=_resource_label(plan),
            status="PENDING_APPROVAL",
            metadata={
                "reason": decision.reason,
                "risk_level": decision.risk_level,
            },
        )

        return None

    ########################################################
    # Queue execution
    ########################################################

    execution = ActionExecution.objects.create(
        plan=plan,
        status="pending",
    )

    write_audit_log(
        organization=plan.cloud_account.organization,
        actor=actor,
        action=plan.action,
        resource_id=_resource_label(plan),
        status="QUEUED",
        metadata={
            "plan_id": str(plan.id),
            "confidence": plan.confidence,
            "risk_score": plan.risk_score,
            "estimated_monthly_savings": float(
                plan.estimated_monthly_savings
            ),
        },
    )

    transaction.on_commit(
        lambda: __queue_execution(execution)
    )

    return execution


def __queue_execution(execution):

    from actions.tasks import execute_action

    execute_action.delay(str(execution.id))