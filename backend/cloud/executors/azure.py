from __future__ import annotations

import logging
import re

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

from cloud.executors.base import CloudExecutor

logger = logging.getLogger(__name__)


class AzureExecutor(CloudExecutor):
    """
    Azure executor for VM and Kubernetes workloads.

    Supported actions:
    - scale_deployment
    - stop_vm / stop_instance        -> deallocate
    - start_vm / start_instance
    - delete_vm / delete_instance
    - resize_vm / resize_instance
    """

    ARM_RG_RE = re.compile(r"/resourceGroups/([^/]+)/providers/", re.IGNORECASE)
    ARM_VM_RE = re.compile(r"/virtualMachines/([^/]+)", re.IGNORECASE)

    def __init__(self, cloud_account):
        super().__init__(cloud_account)
        self._credential = None
        self._compute_client = None

    def _azure_account(self):
        return getattr(self.cloud_account, "azure", None)

    def _credentials(self):
        if self._credential is not None:
            return self._credential

        azure_account = self._azure_account()
        if not azure_account:
            raise ValueError("Azure account details are missing")

        self._credential = ClientSecretCredential(
            tenant_id=azure_account.tenant_id,
            client_id=azure_account.client_id,
            client_secret=azure_account.client_secret,
        )
        return self._credential

    def _compute(self):
        if self._compute_client is not None:
            return self._compute_client

        azure_account = self._azure_account()
        if not azure_account:
            raise ValueError("Azure account details are missing")

        self._compute_client = ComputeManagementClient(
            self._credentials(),
            azure_account.subscription_id,
        )
        return self._compute_client

    def _resolve_vm(self, target_name, parameters):
        parameters = parameters or {}

        resource = self._find_resource(
            provider_resource_id=parameters.get("provider_resource_id")
            or parameters.get("resource_id")
            or parameters.get("vm_id"),
            target_name=target_name,
        )

        vm_name = (
            parameters.get("vm_name")
            or parameters.get("name")
            or target_name
        )
        resource_group = (
            parameters.get("resource_group")
            or parameters.get("resourceGroup")
        )

        if resource:
            metadata = self._resource_metadata(resource)
            vm_name = resource.name or vm_name or self._parse_vm_name(resource.external_id)
            resource_group = (
                resource_group
                or metadata.get("resource_group")
                or metadata.get("resourceGroup")
                or self._parse_resource_group(resource.external_id)
                or self._parse_resource_group(metadata.get("id"))
            )

        if not vm_name:
            raise ValueError("Azure VM name is required")

        if not resource_group:
            raise ValueError("Azure resource group is required")

        return resource, vm_name, resource_group

    def _parse_resource_group(self, arm_id):
        if not arm_id or not isinstance(arm_id, str):
            return None
        match = self.ARM_RG_RE.search(arm_id)
        if match:
            return match.group(1)
        return None

    def _parse_vm_name(self, arm_id):
        if not arm_id or not isinstance(arm_id, str):
            return None
        match = self.ARM_VM_RE.search(arm_id)
        if match:
            return match.group(1)
        return None

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

        if action_key in {"stop_vm", "stop_instance"}:
            return self._stop_vm(target_name=target_name, parameters=parameters)

        if action_key in {"start_vm", "start_instance"}:
            return self._start_vm(target_name=target_name, parameters=parameters)

        if action_key in {"delete_vm", "delete_instance", "terminate_instance"}:
            return self._delete_vm(target_name=target_name, parameters=parameters)

        if action_key in {"resize_vm", "resize_instance"}:
            return self._resize_vm(target_name=target_name, parameters=parameters)

        raise ValueError(f"Unsupported Azure action: {action}")

    def _stop_vm(self, *, target_name, parameters):
        _, vm_name, resource_group = self._resolve_vm(target_name, parameters)
        client = self._compute()

        try:
            # Cost-saving stop = deallocate, not power_off.
            if parameters.get("power_off", False):
                poller = client.virtual_machines.begin_power_off(
                    resource_group_name=resource_group,
                    vm_name=vm_name,
                )
            else:
                poller = client.virtual_machines.begin_deallocate(
                    resource_group_name=resource_group,
                    vm_name=vm_name,
                )

            poller.result()

            logger.info(
                "Azure VM stopped/deallocated %s in %s",
                vm_name,
                resource_group,
            )

            return {
                "provider": "azure",
                "action": "stop_vm",
                "vm_name": vm_name,
                "resource_group": resource_group,
                "status": "stopped",
                "deallocated": not parameters.get("power_off", False),
            }

        except Exception as exc:
            logger.exception("Azure stop VM failed")
            raise RuntimeError(
                f"Failed to stop Azure VM {vm_name}: {exc}"
            ) from exc

    def _start_vm(self, *, target_name, parameters):
        _, vm_name, resource_group = self._resolve_vm(target_name, parameters)
        client = self._compute()

        try:
            poller = client.virtual_machines.begin_start(
                resource_group_name=resource_group,
                vm_name=vm_name,
            )
            poller.result()

            logger.info(
                "Azure VM started %s in %s",
                vm_name,
                resource_group,
            )

            return {
                "provider": "azure",
                "action": "start_vm",
                "vm_name": vm_name,
                "resource_group": resource_group,
                "status": "running",
            }

        except Exception as exc:
            logger.exception("Azure start VM failed")
            raise RuntimeError(
                f"Failed to start Azure VM {vm_name}: {exc}"
            ) from exc

    def _delete_vm(self, *, target_name, parameters):
        _, vm_name, resource_group = self._resolve_vm(target_name, parameters)
        client = self._compute()

        try:
            force_deletion = bool(parameters.get("force_deletion", False))

            try:
                if force_deletion:
                    poller = client.virtual_machines.begin_delete(
                        resource_group_name=resource_group,
                        vm_name=vm_name,
                        force_deletion=True,
                    )
                else:
                    poller = client.virtual_machines.begin_delete(
                        resource_group_name=resource_group,
                        vm_name=vm_name,
                    )
            except TypeError:
                poller = client.virtual_machines.begin_delete(
                    resource_group_name=resource_group,
                    vm_name=vm_name,
                )

            poller.result()

            logger.info(
                "Azure VM deleted %s in %s",
                vm_name,
                resource_group,
            )

            return {
                "provider": "azure",
                "action": "delete_vm",
                "vm_name": vm_name,
                "resource_group": resource_group,
                "status": "deleted",
            }

        except Exception as exc:
            logger.exception("Azure delete VM failed")
            raise RuntimeError(
                f"Failed to delete Azure VM {vm_name}: {exc}"
            ) from exc

    def _resize_vm(self, *, target_name, parameters):
        parameters = parameters or {}
        new_vm_size = (
            parameters.get("vm_size")
            or parameters.get("instance_type")
            or parameters.get("target_vm_size")
            or parameters.get("new_vm_size")
        )

        if not new_vm_size:
            raise ValueError("vm_size is required for resize_vm")

        _, vm_name, resource_group = self._resolve_vm(target_name, parameters)
        client = self._compute()

        try:
            # Resize a VM safely by deallocating first.
            self._stop_vm(target_name=target_name, parameters=parameters)

            vm = client.virtual_machines.get(
                resource_group_name=resource_group,
                vm_name=vm_name,
            )

            if not vm.hardware_profile:
                raise RuntimeError(
                    f"Azure VM {vm_name} has no hardware_profile"
                )

            vm.hardware_profile.vm_size = new_vm_size

            poller = client.virtual_machines.begin_create_or_update(
                resource_group_name=resource_group,
                vm_name=vm_name,
                parameters=vm,
            )
            poller.result()

            if parameters.get("start_after_resize", True):
                self._start_vm(target_name=target_name, parameters=parameters)

            logger.info(
                "Azure VM resized %s to %s",
                vm_name,
                new_vm_size,
            )

            return {
                "provider": "azure",
                "action": "resize_vm",
                "vm_name": vm_name,
                "resource_group": resource_group,
                "vm_size": new_vm_size,
                "status": "running",
            }

        except Exception as exc:
            logger.exception("Azure resize VM failed")
            raise RuntimeError(
                f"Failed to resize Azure VM {vm_name}: {exc}"
            ) from exc