# control_plane/services/apply_optimizer.py

from __future__ import annotations

from actions.models import ExecutionPlan
from cloud.executors.factory import get_cloud_executor


def apply_optimization(plan: ExecutionPlan):
    """
    Dispatch an ExecutionPlan to the correct cloud executor.
    """

    if plan is None:
        raise ValueError("plan is required")

    provider = getattr(plan.cloud_account.provider, "code", "").strip().lower()
    if not provider:
        raise ValueError("Provider code is missing on the cloud account")

    if plan.action == "RECOMMEND":
        return {
            "status": "skipped",
            "reason": "recommendation_only",
            "plan_id": str(plan.id),
        }

    executor = get_cloud_executor(plan.cloud_account)

    resource = getattr(plan, "resource", None)
    target_name = (
        plan.target_name
        or getattr(resource, "name", None)
        or plan.provider_resource_id
        or str(plan.id)
    )

    return executor.execute(
        target_type=plan.resource_type,
        namespace=plan.namespace,
        target_name=target_name,
        action=plan.action,
        parameters=plan.parameters or {},
    )