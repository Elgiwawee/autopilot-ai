from cloud.providers.aws import AWSProvider
from cloud.providers.gcp import GCPProvider
from cloud.providers.azure import AzureProvider

PROVIDERS = {
    "aws": AWSProvider,
    "gcp": GCPProvider,
    "azure": AzureProvider,
}


def get_provider(cloud_account):
    print("=== FACTORY DEBUG ===")
    print("cloud_account:", cloud_account)
    print("provider:", cloud_account.provider)
    print("provider type:", type(cloud_account.provider))

    provider_code = cloud_account.provider.code.lower()

    print("provider_code:", provider_code)
    print("available:", PROVIDERS.keys())

    provider_cls = PROVIDERS.get(provider_code)

    print("provider_cls:", provider_cls)

    if provider_cls is None:
        raise ValueError(
            f"Unsupported provider code: {provider_code}"
        )

    return provider_cls(cloud_account)