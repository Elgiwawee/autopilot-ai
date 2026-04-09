# actions/services/executions.py

from actions.models import ExecutionPlan
from audit.services.receipt import generate_execution_receipt

def get_recent_actions(organization, limit=10):
    """
    Read-only execution history for dashboards.
    """

    return list(
        ExecutionPlan.objects
        .filter(cloud_account__organization=organization)
        .order_by("-created_at")[:limit]
    )

def get_execution_receipt(execution_id):
    """Generate a receipt for a completed execution, including details and audit info.
    """
    execution = ExecutionPlan.objects.get(id=execution_id)
    return generate_execution_receipt(execution)