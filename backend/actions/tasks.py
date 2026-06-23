import logging

from celery import shared_task
from django.utils.timezone import now

from accounts.models import GlobalSafety
from actions.models import ActionExecution
from ai_engine.reinforcement.trainer import RLTrainer
from audit.services.writer import write_audit_log
from billing.services.trigger import trigger_savings_computation
from cloud.executors.factory import get_cloud_executor
from control_plane.services.billing_guard import assert_billing_in_good_standing

logger = logging.getLogger(__name__)


# ----------------------------------------------------
# Optimizer Scan
# ----------------------------------------------------

@shared_task
def run_optimizer_scan():
    """
    Kick off inventory sync for every active cloud account.
    Inventory collectors are responsible for triggering the
    opportunity scan after their sync completes.
    """
    from cloud.models import CloudAccount
    from cloud.tasks.collect_inventory import collect_all_cloud_resources

    accounts = (
        CloudAccount.objects
        .select_related("provider")
        .filter(is_active=True)
    )

    for account in accounts:
        collect_all_cloud_resources.delay(str(account.id))


def _plan_resource_label(plan, resource=None):
    resource_name = getattr(resource, "name", None) if resource else None

    return (
        plan.target_name
        or plan.provider_resource_id
        or resource_name
        or str(plan.id)
    )


def _build_execution_parameters(plan, resource=None):
    parameters = dict(plan.parameters or {})

    provider_resource_id = (
        plan.provider_resource_id
        or getattr(resource, "external_id", None)
    )

    if provider_resource_id:
        parameters.setdefault("provider_resource_id", provider_resource_id)
        parameters.setdefault("resource_id", provider_resource_id)
        parameters.setdefault("instance_id", provider_resource_id)
        parameters.setdefault("vm_id", provider_resource_id)

    if plan.namespace:
        parameters.setdefault("namespace", plan.namespace)

    if resource:
        metadata = getattr(resource, "metadata", {}) or {}
        if isinstance(metadata, dict):
            zone = metadata.get("zone")
            availability_zone = metadata.get("availability_zone")
            region = getattr(resource, "region", None)
            resource_group = (
                metadata.get("resource_group")
                or metadata.get("resourceGroup")
            )

            if zone:
                parameters.setdefault("zone", zone)
            if availability_zone:
                parameters.setdefault("availability_zone", availability_zone)
            if region:
                parameters.setdefault("region", region)
            if resource_group:
                parameters.setdefault("resource_group", resource_group)

        resource_name = getattr(resource, "name", None)
        if resource_name:
            parameters.setdefault("name", resource_name)
            parameters.setdefault("instance_name", resource_name)
            parameters.setdefault("vm_name", resource_name)

    return parameters


# ----------------------------------------------------
# Execute Optimization / ExecutionPlan
# ----------------------------------------------------

@shared_task(bind=True, max_retries=3)
def execute_action(self, action_execution_id):
    """
    Execute a queued ActionExecution against the appropriate cloud provider.
    """
    try:
        execution = (
            ActionExecution.objects
            .select_related(
                "plan",
                "plan__resource",
                "plan__cloud_account",
                "plan__cloud_account__provider",
                "plan__cloud_account__organization",
            )
            .get(id=action_execution_id)
        )
    except ActionExecution.DoesNotExist:
        return

    plan = execution.plan
    if plan is None:
        raise RuntimeError("ActionExecution has no ExecutionPlan.")

    cloud_account = plan.cloud_account
    resource = plan.resource

    resource_id = _plan_resource_label(plan, resource)
    parameters = _build_execution_parameters(plan, resource)
    action_type = plan.action
    estimated_savings = plan.estimated_monthly_savings

    # ----------------------------------
    # GLOBAL SAFETY SWITCH
    # ----------------------------------
    safety = GlobalSafety.objects.first()

    if not safety or not safety.autopilot_enabled:
        write_audit_log(
            organization=cloud_account.organization,
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

    plan.status = "executing"
    plan.save(update_fields=["status"])

    write_audit_log(
        organization=cloud_account.organization,
        actor="AUTOPILOT",
        action=action_type,
        resource_id=resource_id,
        status="STARTED",
        metadata={
            "cloud": cloud_account.provider.code,
            "plan_id": str(plan.id),
            "confidence": plan.confidence,
            "risk_score": plan.risk_score,
            "estimated_savings": float(estimated_savings),
        },
    )

    result = None

    try:
        # ----------------------------------
        # INFORMATIONAL ONLY
        # ----------------------------------
        if action_type == "RECOMMEND":
            logger.info(
                "Recommendation acknowledged: %s",
                plan.id,
            )
            result = {
                "status": "recommendation_acknowledged",
                "plan_id": str(plan.id),
            }

        # ----------------------------------
        # REAL EXECUTION
        # ----------------------------------
        else:
            executor = get_cloud_executor(cloud_account)

            result = executor.execute(
                target_type=plan.resource_type,
                namespace=plan.namespace,
                target_name=(
                    plan.target_name
                    or getattr(resource, "name", None)
                    or plan.provider_resource_id
                    or str(plan.id)
                ),
                action=action_type,
                parameters=parameters,
            )

        # ----------------------------------
        # SUCCESS
        # ----------------------------------
        execution.status = "success"
        execution.executed_at = now()
        execution.error_message = None
        execution.save(
            update_fields=[
                "status",
                "executed_at",
                "error_message",
            ]
        )

        plan.status = "committed"
        plan.save(update_fields=["status"])

        write_audit_log(
            organization=cloud_account.organization,
            actor="AUTOPILOT",
            action=action_type,
            resource_id=resource_id,
            status="SUCCESS",
            metadata={
                "cloud": cloud_account.provider.code,
                "plan_id": str(plan.id),
                "result": result or {},
            },
        )

        if action_type != "RECOMMEND":
            try:
                trigger_savings_computation(execution)
            except Exception:
                logger.exception(
                    "Failed to trigger savings computation for %s",
                    execution.id,
                )

            try:
                RLTrainer().update(action_type)
            except Exception:
                logger.exception("RL training failed.")

        assert_billing_in_good_standing(cloud_account.organization)

        return result

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

        plan.status = "failed"
        plan.save(update_fields=["status"])

        write_audit_log(
            organization=cloud_account.organization,
            actor="AUTOPILOT",
            action=action_type,
            resource_id=resource_id,
            status="FAILED",
            metadata={
                "cloud": cloud_account.provider.code,
                "plan_id": str(plan.id),
                "error": str(exc),
            },
        )

        raise