
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

from billing.services.savings_attribution import (
    SavingsAttributionService,
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

    optimization = execution.optimization

    execution.status = "executing"
    execution.save(update_fields=["status"])

    try:

        # ----------------------------------
        # INFORMATIONAL ONLY
        # ----------------------------------

        if optimization.action_type == "RECOMMEND":

            logger.info(
                "Recommendation acknowledged: %s",
                optimization.id,
            )

        # ----------------------------------
        # TERMINATE
        # ----------------------------------

        elif optimization.action_type == "TERMINATE":

            stop_ec2_instance(
                instance_id=optimization.resource_id,
                cloud_account=optimization.cloud_account,
                region=optimization.current_state.get("region"),
            )

        # ----------------------------------
        # RIGHTSIZE
        # ----------------------------------

        elif optimization.action_type == "RIGHTSIZE":

            raise NotImplementedError(
                "RIGHTSIZE executor not implemented."
            )

        # ----------------------------------
        # SPOT
        # ----------------------------------

        elif optimization.action_type == "SPOT":

            raise NotImplementedError(
                "SPOT executor not implemented."
            )

        else:

            raise ValueError(
                f"Unknown action type: "
                f"{optimization.action_type}"
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

        optimization.status = "COMPLETED"

        optimization.save(
            update_fields=[
                "status",
            ]
        )

        # Only executable actions should
        # create savings attribution.

        if optimization.action_type != "RECOMMEND":

            SavingsAttributionService.record(
                execution
            )

    except Exception as exc:

        logger.exception(
            "Execution failed for optimization %s",
            optimization.id,
        )

        execution.status = "failed"
        execution.error_message = str(exc)

        execution.save(
            update_fields=[
                "status",
                "error_message",
            ]
        )

        optimization.status = "FAILED"

        optimization.save(
            update_fields=[
                "status",
            ]
        )

        raise

