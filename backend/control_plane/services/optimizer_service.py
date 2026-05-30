# control_plane/services/optimizer_service.py

from cloud.models import CloudAccount
from actions.services.optimizer import list_optimizations
from cloud.tasks.collect_inventory import (
    collect_all_cloud_resources
)


def build_optimizer(organization):
    accounts = CloudAccount.objects.filter(
        organization=organization,
        is_active=True
    )

    # -----------------------------
    # ASYNC RESOURCE COLLECTION
    # -----------------------------
    collect_all_cloud_resources.delay(
        str(organization.id)
    )

    # -----------------------------
    # RETURN EXISTING OPTIMIZATIONS
    # -----------------------------
    return {
        "organization": organization.id,
        "optimizations": list_optimizations(organization),
    }