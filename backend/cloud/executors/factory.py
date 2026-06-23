from __future__ import annotations

from typing import Dict, Type

from cloud.executors.aws import AWSExecutor
from cloud.executors.azure import AzureExecutor
from cloud.executors.base import CloudExecutor
from cloud.executors.gcp import GCPExecutor
from cloud.executors.kubernetes import KubernetesExecutor

EXECUTORS: Dict[str, Type[CloudExecutor]] = {
    "aws": AWSExecutor,
    "gcp": GCPExecutor,
    "azure": AzureExecutor,
    "kubernetes": KubernetesExecutor,
}


def get_cloud_executor(cloud_account) -> CloudExecutor:
    """
    Return the correct executor for the cloud account provider.
    """
    provider_code = getattr(cloud_account.provider, "code", None)

    if not provider_code:
        raise ValueError("Cloud account provider is missing")

    provider_code = str(provider_code).strip().lower()

    executor_cls = EXECUTORS.get(provider_code)

    if not executor_cls:
        raise ValueError(f"No executor for provider: {provider_code}")

    return executor_cls(cloud_account)