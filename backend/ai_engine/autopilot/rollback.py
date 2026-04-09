# ai_engine/autopilot/rollback.py

import logging
from actions.models import ActionExecution
from monitoring.health import health_failed

logger = logging.getLogger(__name__)


def rollback_if_needed(organization):
    if not health_failed(organization):
        return False

    executions = ActionExecution.objects.filter(
        action_plan__resource__cloud_account__organization=organization,
        status="success",
    ).order_by("-executed_at")[:5]

    logger.warning(f"[ROLLBACK] Triggered for org={organization.id}")

    for execution in executions:
        try:
            rollback_action(execution)
        except Exception:
            logger.exception(f"[ROLLBACK] Failed execution={execution.id}")

    return True


def rollback_action(execution):
    plan = execution.action_plan
    resource = plan.resource

    if plan.action_type == "stop_instance":
        from cloud.aws.ec2 import start_instance
        start_instance(resource.external_id)

    elif plan.action_type == "resize_volume":
        from cloud.aws.ebs import resize_volume
        previous = resource.metadata.get("previous_size_gb")
        if previous:
            resize_volume(resource.external_id, previous)

    execution.status = "rolled_back"
    execution.save()