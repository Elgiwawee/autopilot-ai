# billing/services/trigger.py

from billing.tasks import compute_savings


def trigger_savings_computation(execution):
    """
    Safe async trigger for savings computation.
    """

    if not execution or not execution.id:
        return

    compute_savings.apply_async(
        args=[execution.id],
        countdown=5,  # small delay to ensure DB consistency
    )