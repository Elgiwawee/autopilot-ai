# billing/services/trigger.py

from attribution.tasks import process_execution_attribution


def trigger_savings_computation(execution):
    """
    Safe async trigger for savings computation.
    """

    if not execution or not execution.id:
        return

    process_execution_attribution.apply_async(
        args=[execution.id],
        countdown=5,
    )