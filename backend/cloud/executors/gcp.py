from __future__ import annotations

import logging

from google.cloud import compute_v1
from google.oauth2 import service_account

from cloud.executors.base import CloudExecutor

logger = logging.getLogger(__name__)


class GCPExecutor(CloudExecutor):
    """
    GCP executor for Compute Engine and Kubernetes workloads.

    Supported actions:
    - scale_deployment
    - stop_vm / stop_instance / terminate
    - start_vm / start_instance
    - delete_vm / delete_instance
    - resize_vm / resize_instance / rightsize
    """

    def __init__(self, cloud_account):
        super().__init__(cloud_account)
        self._credentials = None
        self._instances_client = None

    def _gcp_account(self):
        return getattr(self.cloud_account, "gcp", None)

    def _credential(self):
        if self._credentials is not None:
            return self._credentials

        gcp_account = self._gcp_account()
        if not gcp_account:
            raise ValueError("GCP account details are missing")

        self._credentials = service_account.Credentials.from_service_account_info(
            gcp_account.service_account_json
        )
        return self._credentials

    def _instances(self):
        if self._instances_client is not None:
            return self._instances_client

        self._instances_client = compute_v1.InstancesClient(
            credentials=self._credential()
        )
        return self._instances_client

    def _project_id(self):
        gcp_account = self._gcp_account()
        if not gcp_account:
            raise ValueError("GCP account details are missing")
        return gcp_account.project_id

    def _resolve_gcp_target(self, target_name, parameters):
        parameters = parameters or {}

        resource = self._find_resource(
            provider_resource_id=parameters.get("provider_resource_id")
            or parameters.get("resource_id")
            or parameters.get("instance_id"),
            target_name=target_name,
        )

        instance_name = (
            parameters.get("instance_name")
            or parameters.get("name")
            or parameters.get("instance_id")
            or target_name
        )

        zone = (
            parameters.get("zone")
            or parameters.get("availability_zone")
        )

        if resource:
            metadata = self._resource_metadata(resource)
            instance_name = resource.name or instance_name or resource.external_id
            zone = zone or metadata.get("zone") or resource.region

        if not instance_name:
            raise ValueError("GCP instance name is required")

        if not zone:
            raise ValueError("GCP zone is required")

        return resource, instance_name, zone

    @staticmethod
    def _machine_type_uri(zone: str, machine_type: str) -> str:
        if machine_type.startswith("zones/"):
            return machine_type
        return f"zones/{zone}/machineTypes/{machine_type}"

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

        if action_key == "scale_deployment":
            return self._scale_kubernetes_deployment(
                namespace=namespace or parameters.get("namespace"),
                target_name=target_name or parameters.get("name"),
                replicas=parameters.get("replicas"),
                parameters=parameters,
            )

        if action_key in {"stop_vm", "stop_instance", "terminate"}:
            return self._stop_instance(target_name=target_name, parameters=parameters)

        if action_key in {"start_vm", "start_instance"}:
            return self._start_instance(target_name=target_name, parameters=parameters)

        if action_key in {"delete_vm", "delete_instance", "terminate_instance"}:
            return self._delete_instance(target_name=target_name, parameters=parameters)

        if action_key in {"resize_vm", "resize_instance", "rightsize"}:
            return self._resize_instance(target_name=target_name, parameters=parameters)

        raise ValueError(f"Unsupported GCP action: {action}")

    def _stop_instance(self, *, target_name, parameters):
        _, instance_name, zone = self._resolve_gcp_target(target_name, parameters)
        client = self._instances()

        try:
            operation = client.stop(
                project=self._project_id(),
                zone=zone,
                instance=instance_name,
            )
            operation.result(timeout=self.OPERATION_TIMEOUT_SECONDS)

            logger.info(
                "GCP Compute Engine stopped instance %s in %s",
                instance_name,
                zone,
            )

            return {
                "provider": "gcp",
                "action": "stop_instance",
                "instance_name": instance_name,
                "zone": zone,
                "status": "stopped",
            }

        except Exception as exc:
            logger.exception("GCP stop instance failed")
            raise RuntimeError(
                f"Failed to stop GCP instance {instance_name}: {exc}"
            ) from exc

    def _start_instance(self, *, target_name, parameters):
        _, instance_name, zone = self._resolve_gcp_target(target_name, parameters)
        client = self._instances()

        try:
            operation = client.start(
                project=self._project_id(),
                zone=zone,
                instance=instance_name,
            )
            operation.result(timeout=self.OPERATION_TIMEOUT_SECONDS)

            logger.info(
                "GCP Compute Engine started instance %s in %s",
                instance_name,
                zone,
            )

            return {
                "provider": "gcp",
                "action": "start_instance",
                "instance_name": instance_name,
                "zone": zone,
                "status": "running",
            }

        except Exception as exc:
            logger.exception("GCP start instance failed")
            raise RuntimeError(
                f"Failed to start GCP instance {instance_name}: {exc}"
            ) from exc

    def _delete_instance(self, *, target_name, parameters):
        _, instance_name, zone = self._resolve_gcp_target(target_name, parameters)
        client = self._instances()

        try:
            operation = client.delete(
                project=self._project_id(),
                zone=zone,
                instance=instance_name,
            )
            operation.result(timeout=self.OPERATION_TIMEOUT_SECONDS)

            logger.info(
                "GCP Compute Engine deleted instance %s in %s",
                instance_name,
                zone,
            )

            return {
                "provider": "gcp",
                "action": "delete_instance",
                "instance_name": instance_name,
                "zone": zone,
                "status": "deleted",
            }

        except Exception as exc:
            logger.exception("GCP delete instance failed")
            raise RuntimeError(
                f"Failed to delete GCP instance {instance_name}: {exc}"
            ) from exc

    def _resize_instance(self, *, target_name, parameters):
        parameters = parameters or {}
        new_machine_type = (
            parameters.get("machine_type")
            or parameters.get("target_machine_type")
            or parameters.get("new_machine_type")
        )

        if not new_machine_type:
            raise ValueError("machine_type is required for resize_vm")

        _, instance_name, zone = self._resolve_gcp_target(target_name, parameters)
        client = self._instances()

        try:
            # Stop first (required before machine type changes).
            self._stop_instance(target_name=target_name, parameters=parameters)

            operation = client.set_machine_type(
                project=self._project_id(),
                zone=zone,
                instance=instance_name,
                machine_type=self._machine_type_uri(zone, new_machine_type),
            )
            operation.result(timeout=self.OPERATION_TIMEOUT_SECONDS)

            # Start again after resize.
            self._start_instance(target_name=target_name, parameters=parameters)

            logger.info(
                "GCP Compute Engine resized instance %s to %s",
                instance_name,
                new_machine_type,
            )

            return {
                "provider": "gcp",
                "action": "resize_instance",
                "instance_name": instance_name,
                "zone": zone,
                "machine_type": new_machine_type,
                "status": "running",
            }

        except Exception as exc:
            logger.exception("GCP resize instance failed")
            raise RuntimeError(
                f"Failed to resize GCP instance {instance_name}: {exc}"
            ) from exc