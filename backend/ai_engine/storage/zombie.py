# ai_engine/storage/zombie.py

from actions.models import ActionPlan


def is_zombie(volume):
    return (
        volume.state == "available"
        and not volume.attached_instance_id
    )


def generate_delete_plan(volume):

    savings = volume.size_gb * 0.10 * 24 * 30

    return ActionPlan.objects.create(
        resource=volume.cloud_resource,
        action_type="DELETE_VOLUME",
        estimated_savings=savings,
        risk_level="medium",
        is_safe=False,
        explanation=(
            "Unattached EBS volume detected. "
            "Manual approval recommended "
            "before deletion."
        ),
    )
