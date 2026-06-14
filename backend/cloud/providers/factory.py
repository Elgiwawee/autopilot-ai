# cloud/providers/factory.py

from cloud.providers.aws import AWSProvider
from cloud.providers.gcp import GCPProvider
from cloud.providers.azure import AzureProvider

PROVIDERS = {
    "aws": AWSProvider,
    "gcp": GCPProvider,
    "azure": AzureProvider,
}


def get_provider(cloud_account):
    provider = getattr(cloud_account, "provider", None)

    if provider is None:
        raise ValueError("Cloud account has no provider.")

    provider_code = getattr(provider, "code", "").lower()

    provider_cls = PROVIDERS.get(provider_code)

    if provider_cls is None:
        raise ValueError(
            f"Unsupported cloud provider code: {provider_code}"
        )

    return provider_cls(cloud_account)