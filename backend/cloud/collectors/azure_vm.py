import logging

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

from cloud.models import (
    CloudAccount,
    CloudResource,
)

from cloud.cost.azure_cost import (
    calculate_azure_hourly_cost,
)

from cloud.utils.json import json_safe

from ai_engine.tasks.detector_tasks import (
    scan_cloud_for_opportunities,
)

logger = logging.getLogger(__name__)

GPU_PREFIXES = (
    "Standard_N",
    "Standard_NC",
    "Standard_ND",
    "Standard_NV",
)


def collect_azure_instances(
    cloud_account_id,
):
    """
    Production Azure VM inventory sync.
    """

    cloud_account = (
        CloudAccount.objects
        .select_related(
            "provider",
            "azure",
        )
        .get(id=cloud_account_id)
    )

    provider = cloud_account.provider
    azure = cloud_account.azure

    credential = ClientSecretCredential(
        tenant_id=azure.tenant_id,
        client_id=azure.client_id,
        client_secret=azure.client_secret,
    )

    compute_client = ComputeManagementClient(
        credential,
        azure.subscription_id,
    )

    logger.info(
        "[AZURE] Starting VM inventory sync subscription=%s",
        azure.subscription_id,
    )

    for vm in compute_client.virtual_machines.list_all():

        try:

            vm_id = vm.id

            vm_name = vm.name

            vm_size = (
                vm.hardware_profile.vm_size
                if vm.hardware_profile
                else ""
            )

            resource_type = (
                "gpu"
                if vm_size.startswith(
                    GPU_PREFIXES
                )
                else "vm"
            )

            hourly_cost = (
                calculate_azure_hourly_cost(
                    vm_size=vm_size,
                    region=vm.location,
                )
            )

            metadata = json_safe(
                vm.as_dict()
            )

            metadata["vm_size"] = vm_size
            metadata["location"] = vm.location
            metadata["subscription_id"] = (
                azure.subscription_id
            )

            metadata["provisioning_state"] = (
                vm.provisioning_state
            )

            CloudResource.objects.update_or_create(
                cloud_account=cloud_account,
                external_id=vm_id,
                defaults={
                    "provider": provider,
                    "resource_type": resource_type,
                    "region": vm.location,
                    "state": (
                        vm.provisioning_state
                        or "unknown"
                    ).lower(),
                    "cost_per_hour": hourly_cost,
                    "name": vm_name,
                    "metadata": metadata,
                },
            )

        except Exception:
            logger.exception(
                "[AZURE] Failed processing VM %s",
                getattr(vm, "name", "unknown"),
            )

    logger.info(
        "[AZURE] Inventory sync complete"
    )

    scan_cloud_for_opportunities.delay(
        cloud_account.id
    )