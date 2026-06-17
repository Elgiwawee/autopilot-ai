# ai_engine/storage/planner.py
from actions.models import ActionPlan


def generate_gp3_plan(volume):
    savings = volume.size_gb * 0.02 * 24 * 30

    return ActionPlan.objects.create(
        resource=volume.cloud_resource,
        action_type="CONVERT_GP2_TO_GP3",
        estimated_savings=savings,
        risk_level="low",
        is_safe=True,
        explanation=(
            f"EBS volume {volume.volume_id} "
            "can be converted from GP2 to GP3 "
            "to reduce storage cost while "
            "maintaining performance."
        ),
    )
