# cloud/collectors/aws_ec2

import boto3
from cloud.models import CloudAccount, CloudResource
from cloud.cost.ec2_cost import calculate_ec2_hourly_cost
from ai_engine.tasks.detector_tasks import scan_cloud_for_opportunities
from cloud.utils.json import json_safe

def collect_ec2_instances(cloud_account_id):
    cloud_account = CloudAccount.objects.get(id=cloud_account_id)

    # ✅ Use provider directly (FIXED)
    provider = cloud_account.provider

    # -----------------------------
    # ASSUME ROLE (SECURE)
    # -----------------------------
    sts = boto3.client("sts")

    assume_kwargs = {
        "RoleArn": cloud_account.role_arn,
        "RoleSessionName": "cloud-autopilot-session",
    }

    if cloud_account.external_id:
        assume_kwargs["ExternalId"] = cloud_account.external_id

    assumed = sts.assume_role(**assume_kwargs)

    creds = assumed["Credentials"]

    # ----------------------------------
    # DISCOVER ALL AWS REGIONS
    # ----------------------------------

    ec2_global = boto3.client(
        "ec2",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name="us-east-1",
    )

    regions = ec2_global.describe_regions()["Regions"]
    print(f"Found {len(regions)} AWS regions")

    for region_data in regions:

        region_name = region_data["RegionName"]
        print(f"Scanning region: {region_name}")

        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=region_name,
        )

        paginator = ec2.get_paginator(
            "describe_instances"
        )

        for page in paginator.paginate():

            for reservation in page.get(
                "Reservations",
                []
            ):

                for instance in reservation.get(
                    "Instances",
                    []
                ):

                    instance_id = instance["InstanceId"]

                    state = instance["State"]["Name"]

                    hourly_cost = calculate_ec2_hourly_cost(
                        instance,
                        provider=provider.code
                    )
                    print(
                        f"Found instance {instance_id} "
                        f"in {region_name}"
                    )

                    instance_type = instance.get("InstanceType", "")

                    GPU_PREFIXES = (
                        "g4",
                        "g5",
                        "g6",
                        "p2",
                        "p3",
                        "p4",
                        "p5",
                        "trn1",
                        "inf1",
                        "inf2",
                    )

                    resource_type = (
                        "gpu"
                        if instance_type.startswith(GPU_PREFIXES)
                        else "vm"
                    )

                    metadata = json_safe(instance)

                    metadata["instance_type"] = instance.get("InstanceType")

                    metadata["availability_zone"] = (
                        instance.get("Placement", {})
                        .get("AvailabilityZone")
                    )

                    metadata["private_ip"] = instance.get("PrivateIpAddress")

                    metadata["public_ip"] = instance.get("PublicIpAddress")

                    metadata["architecture"] = instance.get("Architecture")

                    metadata["platform"] = instance.get("PlatformDetails")

                    metadata["launch_time"] = (
                        instance.get("LaunchTime").isoformat()
                        if instance.get("LaunchTime")
                        else None
                    )

                    metadata["gpu_utilization"] = 0

                    metadata["memory_gb"] = None

                    metadata["attached_to"] = None

                    CloudResource.objects.update_or_create(
                        cloud_account=cloud_account,
                        external_id=instance_id,
                        defaults={
                            "provider": provider,
                            "resource_type": resource_type,
                            "region": region_name,
                            "state": state,
                            "cost_per_hour": hourly_cost,
                            "metadata": metadata,
                        },
                    )

    scan_cloud_for_opportunities.delay(
        cloud_account.id
    )