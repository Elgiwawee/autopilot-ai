# cloud/kubernetes_engine/tasks/execution.py

from celery import shared_task
from kubernetes_engine.client import KubernetesClient
from kubernetes_engine.canary import canary_patch
from kubernetes_engine.observer import observe_canary
from kubernetes_engine.rollback import rollback_execution
from kubernetes_engine.models import Policy
from audit.services.receipt import generate_execution_receipt
from cloud.kubernetes_engine.policies import enforce_policies, PolicyViolation
from actions.models import ExecutionRecord
from django.utils import timezone
from kubernetes_engine.tasks.evaluate import evaluate_canary

@shared_task(bind=True)
def execute_k8s_rightsizing(self, execution_record_id):
    execution = ExecutionRecord.objects.select_related(
        "decision",
        "decision__executionplan"
    ).get(id=execution_record_id)

    plan = execution.decision.executionplan

    execution.state = "EXECUTING"
    execution.started_at = timezone.now()
    execution.save(update_fields=["state", "started_at"])

    k8s = KubernetesClient()

    # Apply canary
    canary_patch(
        k8s=k8s,
        deployment_name=plan.resource_id,
        namespace=plan.namespace,
        patch=plan.patch,
    )

    # Schedule evaluation AFTER canary window
    evaluate_canary.apply_async(
        args=[execution.id],
        countdown=execution.decision.canary_duration_minutes * 60,
    )



def start_execution(plan):
    try:
        enforce_policies(plan)
    except PolicyViolation:
        plan.status = "failed"
        plan.save()
        raise

    # execution continues only if policies pass
    plan.status = "running"
    plan.save()
