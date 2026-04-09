# cloud/kubernetes_engine/tasks/evaluate.py

from celery import shared_task
from django.utils import timezone

from kubernetes_engine.observer import observe_canary_metrics
from kubernetes_engine.rollback import rollback_execution
from kubernetes_engine.client import KubernetesClient
from actions.models import CanaryWindow, ExecutionRecord
from kubernetes_engine.models import CanaryWindow
from kubernetes_engine.tasks.commit import commit_execution

@shared_task(bind=True)
def evaluate_canary(self, execution_record_id):
    execution = ExecutionRecord.objects.select_related(
        "decision",
        "decision__executionplan"
    ).get(id=execution_record_id)

    plan = execution.decision.executionplan
    window = CanaryWindow.objects.get(execution_plan=plan)

    metrics = observe_canary_metrics(execution_plan=plan)

    # Persist observations (AUDITABLE)
    window.observed_error_rate = metrics["error_rate"]
    window.observed_latency_ms = metrics["latency_ms"]
    window.save(update_fields=[
        "observed_error_rate",
        "observed_latency_ms",
    ])

    # --- DECISION LOGIC ---
    error_regression = (
        metrics["error_rate"]
        > window.baseline_error_rate * 1.1
    )

    latency_regression = (
        metrics["latency_ms"]
        > window.baseline_latency_ms * 1.2
    )

    if error_regression or latency_regression:
        # 🔴 FAIL → ROLLBACK
        k8s = KubernetesClient()

        rollback_execution(
            k8s=k8s,
            deployment_name=plan.resource_id,
            namespace=plan.namespace,
            previous_spec=execution.rollback_payload,
            reason="Canary regression detected",
            policy=execution.decision.policy,
        )

        execution.state = "ROLLED_BACK"
        execution.error = "Canary regression"
        execution.finished_at = timezone.now()
        execution.save(update_fields=[
            "state",
            "error",
            "finished_at",
        ])
        return

    # 🟢 PASS → VERIFIED
    execution.state = "VERIFIED"
    execution.save(update_fields=["state"])

    commit_execution.apply_async(args=[execution.id], countdown=60)  # commit after 1 min to allow metrics to stabilize