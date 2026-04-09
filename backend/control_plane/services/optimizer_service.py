# control_plane/services/optimizer_service.py

from cloud.models import CloudAccount
from actions.services.optimizer import list_optimizations
from cloud.tasks import collect_aws_ec2_task


def build_optimizer(organization):
    accounts = CloudAccount.objects.filter(
        organization=organization,
        is_active=True
    )

    # -----------------------------
    # ASYNC RESOURCE COLLECTION
    # -----------------------------
    for acc in accounts:
        if acc.provider.code == "aws":
            collect_aws_ec2_task.delay(acc.id)  # 🚀 async

    # -----------------------------
    # RETURN EXISTING OPTIMIZATIONS
    # -----------------------------
    return {
        "organization": organization.id,
        "optimizations": list_optimizations(organization),
    }