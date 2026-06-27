# cloud/executors/aws.py

from __future__ import annotations

import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from cloud.executors.base import CloudExecutor

logger = logging.getLogger(__name__)


class AWSExecutor(CloudExecutor):
    """
    AWS executor for EC2 and Kubernetes workloads.

    Supported actions:
    - scale_deployment
    - stop_vm / stop_instance / terminate / TERMINATE
    - start_vm / start_instance
    - delete_vm / terminate_instance / terminate_vm
    - resize_vm / resize_instance / RIGHTSIZE
    - reboot_vm / reboot_instance
    """

    def __init__(self, cloud_account):
        super().__init__(cloud_account)
        self._session = None

    def _aws_account(self):
        return getattr(self.cloud_account, "aws", None)

    def _session_or_default(self):
        if self._session is not None:
            return self._session

        aws_account = self._aws_account()

        if not aws_account or not getattr(aws_account, "role_arn", None):
            self._session = boto3.Session()
            return self._session

        sts = boto3.client("sts")
        assume_kwargs = {
            "RoleArn": aws_account.role_arn,
            "RoleSessionName": "autopilot-executor",
        }

        if getattr(aws_account, "external_id", None):
            assume_kwargs["ExternalId"] = aws_account.external_id

        assumed = sts.assume_role(**assume_kwargs)
        creds = assumed["Credentials"]

        self._session = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
        return self._session

    def _default_region(self):
        aws_account = self._aws_account()
        if aws_account and getattr(aws_account, "default_region", None):
            return aws_account.default_region

        resource = self._find_resource()
        metadata = self._resource_metadata(resource)

        region = (
            metadata.get("region")
            or metadata.get("availability_zone")
            or getattr(self.cloud_account, "region", None)
            or "us-east-1"
        )

        if isinstance(region, str) and len(region) > 2:
            # Convert us-east-1a -> us-east-1 when an AZ is provided.
            if region[-1].isalpha() and region[-2].isdigit():
                return region[:-1]

        return region

    def _ec2_client(self, region=None):
        session = self._session_or_default()
        return session.client("ec2", region_name=region or self._default_region())

    def _resolve_instance(self, target_name, parameters):
        parameters = parameters or {}

        resource = self._find_resource(
            provider_resource_id=parameters.get("provider_resource_id")
            or parameters.get("resource_id")
            or parameters.get("instance_id"),
            target_name=target_name,
        )

        instance_id = (
            parameters.get("instance_id")
            or parameters.get("resource_id")
            or parameters.get("external_id")
        )

        if resource:
            instance_id = resource.external_id or instance_id

        if not instance_id:
            raise ValueError("EC2 instance id is required")

        region = (
            parameters.get("region")
            or parameters.get("availability_zone")
            or parameters.get("zone")
        )

        if not region and resource:
            metadata = self._resource_metadata(resource)
            region = (
                metadata.get("region")
                or metadata.get("availability_zone")
                or metadata.get("zone")
            )

        if region and len(region) > 2:
            if region[-1].isalpha() and region[-2].isdigit():
                region = region[:-1]

        return resource, str(instance_id), region or self._default_region()

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

        if action_key in {"stop_vm", "stop_instance", "terminate", "terminate_instance"}:
            return self._stop_instance(target_name=target_name, parameters=parameters)

        if action_key in {"start_vm", "start_instance"}:
            return self._start_instance(target_name=target_name, parameters=parameters)

        if action_key in {"delete_vm", "terminate_vm", "delete_instance"}:
            return self._terminate_instance(target_name=target_name, parameters=parameters)

        if action_key in {"resize_vm", "resize_instance", "rightsize"}:
            return self._resize_instance(target_name=target_name, parameters=parameters)

        if action_key in {"reboot_vm", "reboot_instance"}:
            return self._reboot_instance(target_name=target_name, parameters=parameters)

        raise ValueError(f"Unsupported AWS action: {action}")

    def _stop_instance(self, *, target_name, parameters):
        _, instance_id, region = self._resolve_instance(target_name, parameters)

        # Preserve your IAM assume-role pattern, but keep execution logic here.
        aws_account = self._aws_account()
        if not aws_account:
            raise ValueError("AWS account details are missing")

        sts = boto3.client("sts")
        assume_kwargs = {
            "RoleArn": aws_account.role_arn,
            "RoleSessionName": "autopilot-executor",
        }
        if getattr(aws_account, "external_id", None):
            assume_kwargs["ExternalId"] = aws_account.external_id

        assumed = sts.assume_role(**assume_kwargs)
        creds = assumed["Credentials"]

        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=region,
        )

        try:
            ec2.stop_instances(InstanceIds=[instance_id])

            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    "Delay": self.POLL_INTERVAL_SECONDS,
                    "MaxAttempts": max(
                        1,
                        int(self.OPERATION_TIMEOUT_SECONDS / self.POLL_INTERVAL_SECONDS),
                    ),
                },
            )

            logger.info(
                "AWS EC2 stopped instance %s in %s",
                instance_id,
                region,
            )

            return {
                "provider": "aws",
                "action": "stop_instance",
                "instance_id": instance_id,
                "region": region,
                "status": "stopped",
            }

        except (ClientError, BotoCoreError) as exc:
            logger.exception("AWS stop instance failed")
            raise RuntimeError(
                f"Failed to stop EC2 instance {instance_id}: {exc}"
            ) from exc

    def _start_instance(self, *, target_name, parameters):
        _, instance_id, region = self._resolve_instance(target_name, parameters)
        ec2 = self._ec2_client(region)

        try:
            ec2.start_instances(InstanceIds=[instance_id])

            waiter = ec2.get_waiter("instance_running")
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    "Delay": self.POLL_INTERVAL_SECONDS,
                    "MaxAttempts": max(
                        1,
                        int(self.OPERATION_TIMEOUT_SECONDS / self.POLL_INTERVAL_SECONDS),
                    ),
                },
            )

            logger.info("AWS EC2 started instance %s in %s", instance_id, region)

            return {
                "provider": "aws",
                "action": "start_instance",
                "instance_id": instance_id,
                "region": region,
                "status": "running",
            }

        except (ClientError, BotoCoreError) as exc:
            logger.exception("AWS start instance failed")
            raise RuntimeError(
                f"Failed to start EC2 instance {instance_id}: {exc}"
            ) from exc

    def _terminate_instance(self, *, target_name, parameters):
        _, instance_id, region = self._resolve_instance(target_name, parameters)
        ec2 = self._ec2_client(region)

        try:
            ec2.terminate_instances(InstanceIds=[instance_id])

            waiter = ec2.get_waiter("instance_terminated")
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    "Delay": self.POLL_INTERVAL_SECONDS,
                    "MaxAttempts": max(
                        1,
                        int(self.OPERATION_TIMEOUT_SECONDS / self.POLL_INTERVAL_SECONDS),
                    ),
                },
            )

            logger.info(
                "AWS EC2 terminated instance %s in %s",
                instance_id,
                region,
            )

            return {
                "provider": "aws",
                "action": "terminate_instance",
                "instance_id": instance_id,
                "region": region,
                "status": "terminated",
            }

        except (ClientError, BotoCoreError) as exc:
            logger.exception("AWS terminate instance failed")
            raise RuntimeError(
                f"Failed to terminate EC2 instance {instance_id}: {exc}"
            ) from exc

    def _resize_instance(self, *, target_name, parameters):
        parameters = parameters or {}
        new_instance_type = (
            parameters.get("instance_type")
            or parameters.get("target_instance_type")
            or parameters.get("new_instance_type")
        )

        if not new_instance_type:
            raise ValueError("instance_type is required for resize_vm")

        _, instance_id, region = self._resolve_instance(target_name, parameters)
        ec2 = self._ec2_client(region)

        try:
            ec2.stop_instances(InstanceIds=[instance_id])
            ec2.get_waiter("instance_stopped").wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    "Delay": self.POLL_INTERVAL_SECONDS,
                    "MaxAttempts": max(
                        1,
                        int(self.OPERATION_TIMEOUT_SECONDS / self.POLL_INTERVAL_SECONDS),
                    ),
                },
            )

            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={"Value": new_instance_type},
            )

            ec2.start_instances(InstanceIds=[instance_id])
            ec2.get_waiter("instance_running").wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    "Delay": self.POLL_INTERVAL_SECONDS,
                    "MaxAttempts": max(
                        1,
                        int(self.OPERATION_TIMEOUT_SECONDS / self.POLL_INTERVAL_SECONDS),
                    ),
                },
            )

            logger.info(
                "AWS EC2 resized instance %s to %s",
                instance_id,
                new_instance_type,
            )

            return {
                "provider": "aws",
                "action": "resize_instance",
                "instance_id": instance_id,
                "region": region,
                "instance_type": new_instance_type,
                "status": "running",
            }

        except (ClientError, BotoCoreError) as exc:
            logger.exception("AWS resize instance failed")
            raise RuntimeError(
                f"Failed to resize EC2 instance {instance_id}: {exc}"
            ) from exc

    def _reboot_instance(self, *, target_name, parameters):
        _, instance_id, region = self._resolve_instance(target_name, parameters)
        ec2 = self._ec2_client(region)

        try:
            ec2.reboot_instances(InstanceIds=[instance_id])

            logger.info("AWS EC2 rebooted instance %s in %s", instance_id, region)

            return {
                "provider": "aws",
                "action": "reboot_instance",
                "instance_id": instance_id,
                "region": region,
                "status": "rebooted",
            }

        except (ClientError, BotoCoreError) as exc:
            logger.exception("AWS reboot instance failed")
            raise RuntimeError(
                f"Failed to reboot EC2 instance {instance_id}: {exc}"
            ) from exc