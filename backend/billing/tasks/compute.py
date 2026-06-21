# billing/tasks/compute.py

from celery import shared_task

from actions.models import ActionExecution

from attribution.services.engine import AttributionEngine
from attribution.services.ledger import LedgerService


@shared_task(bind=True, max_retries=3)
def compute_savings(self, execution_id):
    """
    Compute realized savings after an optimization
    has been executed.

    Pipeline:

        ActionExecution
                │
                ▼
        AttributionEngine
                │
                ▼
        LedgerService
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    SavingsEvent
    SavingsAttribution
    SavingsLedger
    RevenueShare
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

    # ---------------------------------------
    # only successful executions generate
    # realized savings
    # ---------------------------------------

    if execution.status != "success":

        return

    # ---------------------------------------
    # already attributed?
    # ---------------------------------------

    if hasattr(execution, "attribution"):

        return

    # ---------------------------------------
    # compute savings
    # ---------------------------------------

    result = AttributionEngine.compute(execution)

    # ---------------------------------------
    # persist
    # ---------------------------------------

    LedgerService.record(result)