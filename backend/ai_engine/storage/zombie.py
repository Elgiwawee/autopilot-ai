# ai_engine/storage/zombie.py

from actions.models import ActionPlan

def is_zombie(volume):
    return volume.state == "available" and not volume.attached_instance_id


def generate_delete_plan(volume):
    return ActionPlan.objects.create(
        resource=volume.cloud_resource,
        resource_id=volume.id,
        action_type="delete_volume",
        estimated_savings=volume.size_gb * 0.1 * 24 * 30,
        risk_level="medium",
        is_safe=False,
        explanation="Unattached EBS volume detected."
    )
