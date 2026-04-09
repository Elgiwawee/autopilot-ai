# kubernetes_engine/tasks/commit.py

from celery import shared_task
from django.utils import timezone
from actions.models import ExecutionRecord
from audit.services.writer import write_audit_log
from billing.services.trigger import trigger_savings_computation
from cloud.kubernetes_engine.tasks import execution

@shared_task(bind=True)
def commit_execution(self, execution_record_id):
    execution = ExecutionRecord.objects.get(id=execution_record_id)

    execution.state = "COMPLETED"
    execution.finished_at = timezone.now()
    execution.save(update_fields=["state", "finished_at"])

  

    # AUDIT LOG# ✅ AUDIT
    write_audit_log(
        organization=execution.organization,
        actor="AUTOPILOT",
        action="K8S_COMMIT",
        resource_id=execution.decision.executionplan.resource_id,
        status="COMPLETED",
    )

    # ✅ BILLING
    trigger_savings_computation(execution)