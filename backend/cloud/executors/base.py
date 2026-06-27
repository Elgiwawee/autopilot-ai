from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from cloud.models import CloudResource

logger = logging.getLogger(__name__)


class CloudExecutor(ABC):
    """
    Base executor for cloud/provider actions.

    Shared capabilities:
    - Kubernetes deployment scaling
    - Resource lookup by provider resource ID or target name
    - Common timeouts / logging
    """

    OPERATION_TIMEOUT_SECONDS = 900
    POLL_INTERVAL_SECONDS = 5

    def __init__(self, cloud_account):
        self.cloud_account = cloud_account

    @abstractmethod
    def execute(
        self,
        *,
        target_type,
        namespace,
        target_name,
        action,
        parameters,
    ):
        raise NotImplementedError


    @abstractmethod
    def verify(
        self,
        *,
        target_type,
        namespace,
        target_name,
        action,
        parameters,
    ):
        """
        Verify that the requested action was actually applied
        by the cloud provider.

        Returns:
        {
            "verified": bool,
            "reason": str,
            "actual_state": dict
        }
        """
        raise NotImplementedError

    @abstractmethod
    def rollback(
        self,
        *,
        action,
        current_state,
        proposed_state,
        target_type,
        namespace,
        target_name,
        parameters,
    ):
        """
        Restore the resource to its previous state.

        Returns:

        {
            "success": bool,
            "reason": str,
        }
        """
        raise NotImplementedError

    def _find_resource(
        self,
        *,
        provider_resource_id: Optional[str] = None,
        target_name: Optional[str] = None,
    ) -> Optional[CloudResource]:
        qs = CloudResource.objects.filter(
            cloud_account=self.cloud_account
        )

        if provider_resource_id:
            resource = qs.filter(
                external_id=str(provider_resource_id)
            ).first()
            if resource:
                return resource

        if target_name:
            resource = qs.filter(name=target_name).first()
            if resource:
                return resource

        return None

    @staticmethod
    def _resource_metadata(resource: Optional[CloudResource]) -> dict[str, Any]:
        if not resource:
            return {}

        metadata = resource.metadata or {}
        if isinstance(metadata, dict):
            return metadata

        return {}

    def _kubernetes_apps_api(self, parameters=None):
        """
        Load Kubernetes API client.

        Supports:
        - kubeconfig string in parameters["kubeconfig"]
        - kubeconfig dict in parameters["kubeconfig_dict"]
        - kubeconfig file path in parameters["kubeconfig_path"]
        - in-cluster config
        - local kubeconfig fallback
        """
        parameters = parameters or {}

        try:
            from kubernetes import client, config
        except ImportError as exc:
            raise RuntimeError(
                "kubernetes package is required for scale_deployment actions."
            ) from exc

        kubeconfig_path = parameters.get("kubeconfig_path")
        kubeconfig = (
            parameters.get("kubeconfig")
            or parameters.get("kubeconfig_json")
            or parameters.get("kubeconfig_dict")
        )
        kube_context = parameters.get("kube_context")

        if kubeconfig_path:
            config.load_kube_config(
                config_file=kubeconfig_path,
                context=kube_context,
            )
            return client.AppsV1Api()

        if kubeconfig:
            if isinstance(kubeconfig, dict):
                payload = json.dumps(kubeconfig)
            else:
                payload = kubeconfig

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".kubeconfig",
                delete=False,
            ) as handle:
                handle.write(payload)
                tmp_path = handle.name

            try:
                config.load_kube_config(
                    config_file=tmp_path,
                    context=kube_context,
                )
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

            return client.AppsV1Api()

        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config(context=kube_context)

        return client.AppsV1Api()

    def _scale_kubernetes_deployment(
        self,
        *,
        namespace: str,
        target_name: str,
        replicas: int,
        parameters=None,
    ):
        if not namespace:
            raise ValueError("namespace is required for scale_deployment")

        if not target_name:
            raise ValueError("target_name is required for scale_deployment")

        if replicas is None:
            raise ValueError("replicas is required for scale_deployment")

        replicas = int(replicas)
        apps_api = self._kubernetes_apps_api(parameters=parameters)

        body = {"spec": {"replicas": replicas}}

        apps_api.patch_namespaced_deployment_scale(
            name=target_name,
            namespace=namespace,
            body=body,
        )

        self._wait_for_kubernetes_scale(
            apps_api=apps_api,
            namespace=namespace,
            target_name=target_name,
            desired_replicas=replicas,
        )

        return {
            "provider": getattr(self.cloud_account.provider, "code", None),
            "action": "scale_deployment",
            "namespace": namespace,
            "target_name": target_name,
            "replicas": replicas,
            "status": "scaled",
        }

    def _wait_for_kubernetes_scale(
        self,
        *,
        apps_api,
        namespace: str,
        target_name: str,
        desired_replicas: int,
    ):
        deadline = time.monotonic() + self.OPERATION_TIMEOUT_SECONDS

        while time.monotonic() < deadline:
            scale = apps_api.read_namespaced_deployment_scale(
                name=target_name,
                namespace=namespace,
            )

            spec = getattr(scale, "spec", None)
            status = getattr(scale, "status", None)

            spec_replicas = getattr(spec, "replicas", None) if spec else None
            current_replicas = getattr(status, "replicas", None) if status else None
            ready_replicas = getattr(status, "ready_replicas", None) if status else None
            available_replicas = getattr(status, "available_replicas", None) if status else None

            if (
                spec_replicas == desired_replicas
                and (
                    ready_replicas == desired_replicas
                    or available_replicas == desired_replicas
                    or current_replicas == desired_replicas
                )
            ):
                return scale

            time.sleep(self.POLL_INTERVAL_SECONDS)

        raise TimeoutError(
            f"Timed out waiting for deployment {namespace}/{target_name} "
            f"to scale to {desired_replicas} replicas"
        )