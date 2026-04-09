# cloud/services/infra.py

from cloud.providers.factory import get_provider
from cloud.models import CloudResource


def sync_cloud_account_resources(cloud_account):
    provider = get_provider(cloud_account)

    resources = provider.fetch_resources()

    for resource in resources:
        normalized_type = normalize_resource_type(
            cloud_account.provider.slug,
            resource["resource_type"],
            resource["metadata"]
        )

        CloudResource.objects.update_or_create(
            cloud_account=cloud_account,
            external_id=resource["resource_id"],
            defaults={
                "provider": cloud_account.provider,
                "resource_type": normalized_type,  
                "region": resource["region"],
                "state": resource.get("state", "unknown"),
                "cost_per_hour": resource.get("cost_per_hour", 0),
                "metadata": resource,
            }
        )

def normalize_resource_type(provider, raw_type, metadata):
    
    # Detect GPU instances
    if provider == "aws":
        instance_type = metadata.get("InstanceType", "")
        if instance_type.startswith(("g", "p")):
            return "gpu"

    if provider == "gcp":
        if "gpu" in str(metadata).lower():
            return "gpu"

    if provider == "azure":
        if "gpu" in str(metadata).lower():
            return "gpu"

    return "vm"