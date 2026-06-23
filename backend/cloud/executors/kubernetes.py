from __future__ import annotations

from cloud.executors.base import CloudExecutor


class KubernetesExecutor(CloudExecutor):
    """
    Generic Kubernetes executor.

    Supports only:
    - scale_deployment
    """

    def execute(
        self,
        *,
        target_type,
        namespace,
        target_name,
        action,
        parameters,
    ):
        parameters = parameters or {}
        action_key = (action or "").lower()

        if action_key != "scale_deployment":
            raise ValueError(f"Unsupported Kubernetes action: {action}")

        return self._scale_kubernetes_deployment(
            namespace=namespace or parameters.get("namespace"),
            target_name=target_name or parameters.get("name"),
            replicas=parameters.get("replicas"),
            parameters=parameters,
        )