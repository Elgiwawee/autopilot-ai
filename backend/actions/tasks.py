
# actions/tasks.py

from celery import shared_task
from django.utils.timezone import now
import logging

from cloud.models import CloudAccount
from actions.models import ActionExecution

from ai_engine.tasks.detector_tasks import (
    scan_cloud_for_opportunities,
)

from cloud.tasks.collect_inventory import (
    collect_all_cloud_resources,
)

from actions.executors.aws_ec2 import (
    stop_ec2_instance,
)

from billing.services.trigger import (
    trigger_savings_computation,
)

from audit.services.writer import (
    write_audit_log,
)

from accounts.models import (
    GlobalSafety,
)

from control_plane.services.billing_guard import (
    assert_billing_in_good_standing,
)

from ai_engine.reinforcement.trainer import (
    RLTrainer,
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------
# Optimizer Scan
# ----------------------------------------------------

@shared_task
def run_optimizer_scan():
    accounts = CloudAccount.objects.filter(is_active=True)

    for account in accounts:

        if account.provider.code == "aws":
            collect_all_cloud_resources.delay(account.id)

        scan_cloud_for_opportunities.delay(account.id)


# ----------------------------------------------------
# Execute Optimization
# ----------------------------------------------------

@shared_task(bind=True, max_retries=3)
def execute_action(self, action_execution_id):

    execution = ActionExecution.objects.get(
        id=action_execution_id
    )

    plan = execution.plan or execution.optimization

    if plan is None:
        raise RuntimeError(
            "ActionExecution is not linked to any plan."
        )

    action_type = getattr(plan, "action_type", None) or getattr(plan, "action", None)

    resource_id = getattr(plan, "resource_id", None) or getattr(
        plan,
        "target_name",
        None,
    )

    estimated_savings = getattr(
        plan,
        "estimated_monthly_savings",
        None,
    )

    if estimated_savings is None:
        estimated_savings = getattr(
            plan,
            "estimated_savings",
            0,
        )

    # ----------------------------------
    # GLOBAL SAFETY SWITCH
    # ----------------------------------

    safety = GlobalSafety.objects.first()

    if not safety or not safety.autopilot_enabled:

        write_audit_log(
            organization=plan.cloud_account.organization,
            actor="AUTOPILOT",
            action=action_type,
            resource_id=resource_id,
            status="BLOCKED",
            metadata={
                "reason": "Global safety disabled",
            },
        )

        return

    execution.status = "executing"
    execution.save(update_fields=["status"])

    write_audit_log(
        organization=plan.cloud_account.organization,
        actor="AUTOPILOT",
        action=action_type,
        resource_id=resource_id,
        status="STARTED",
        metadata={
            "confidence": plan.confidence,
            "estimated_savings": float(
                estimated_savings
            ),
        },
    )

    try:

        # ----------------------------------
        # INFORMATIONAL ONLY
        # ----------------------------------

        if action_type == "RECOMMEND":

            logger.info(
                "Recommendation acknowledged: %s",
                plan.id,
            )

        # ----------------------------------
        # TERMINATE
        # ----------------------------------

        elif action_type == "TERMINATE":

            stop_ec2_instance(
                instance_id=resource_id,
                cloud_account=plan.cloud_account,
                region=plan.current_state.get("region"),
            )

        # ----------------------------------
        # RIGHTSIZE
        # ----------------------------------

        elif action_type == "RIGHTSIZE":

            raise NotImplementedError(
                "RIGHTSIZE executor not implemented."
            )

        # ----------------------------------
        # SPOT
        # ----------------------------------

        elif action_type == "SPOT":

            raise NotImplementedError(
                "SPOT executor not implemented."
            )

        else:

            raise ValueError(
                f"Unknown action type: "
                f"{action_type}"
            )

        # ----------------------------------
        # SUCCESS
        # ----------------------------------

        execution.status = "success"
        execution.executed_at = now()

        execution.save(
            update_fields=[
                "status",
                "executed_at",
            ]
        )

        plan.status = "COMPLETED"

        plan.save(
            update_fields=[
                "status",
            ]
        )

        write_audit_log(
            organization=plan.cloud_account.organization,
            actor="AUTOPILOT",
            action=action_type,
            resource_id=resource_id,
            status="SUCCESS",
            metadata={
                "confidence": plan.confidence,
                "estimated_savings": float(estimated_savings),
            },
        )

        # Only executable actions should
        # create savings attribution.

        if action_type != "RECOMMEND":

            trigger_savings_computation(
                execution
            )

            try:

                RLTrainer().update(
                    action_type
                )

            except Exception:

                logger.exception(
                    "RL training failed."
                )
           
        assert_billing_in_good_standing(
            plan.cloud_account.organization
        )

    except Exception as exc:

        logger.exception(
            "Execution failed for optimization %s",
            plan.id,
        )

        execution.status = "failed"
        execution.error_message = str(exc)

        execution.save(
            update_fields=[
                "status",
                "error_message",
            ]
        )

        plan.status = "PLANNED"

        plan.save(
            update_fields=[
                "status",
            ]
        )


        write_audit_log(
            organization=plan.cloud_account.organization,
            actor="AUTOPILOT",
            action=action_type,
            resource_id=resource_id,
            status="FAILED",
            metadata={
                "error": str(exc),
            },
        )

        raise

