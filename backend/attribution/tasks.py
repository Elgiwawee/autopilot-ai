from celery import shared_task

from actions.models import ActionExecution

from attribution.services.engine import AttributionEngine
from attribution.services.ledger import LedgerService
from attribution.services.verifier import SavingsVerifier
from billing.models import SavingsAttribution

@shared_task(bind=True, max_retries=3)
def process_execution_attribution(self, execution_id):
    """
    Runs the complete attribution pipeline.

        ActionExecution
                │
                ▼
        SavingVerifier
                │
                ▼
        AttributionEngine
                │
                ▼
        LedgerService
    """

    try:
        execution = (
            ActionExecution.objects
            .select_related(
                "optimization",
                "optimization__cloud_account",
                "optimization__cloud_account__organization",
                "optimization__cloud_account__provider",

                "plan",
                "plan__cloud_account",
                "plan__cloud_account__organization",
                "plan__cloud_account__provider",
            ) 
            .get(id=execution_id)
        )

    except ActionExecution.DoesNotExist:
        return

    # Only successful executions generate savings
    if execution.status != "success":
        return

    # Prevent duplicate attribution

    if SavingsAttribution.objects.filter(
        execution=execution
    ).exists():
        return

    # Verify execution is eligible
    if not SavingsVerifier.verify(execution):
        return

    # Compute savings
    result = AttributionEngine.compute(execution)

    # Persist to database
    LedgerService.record(result)