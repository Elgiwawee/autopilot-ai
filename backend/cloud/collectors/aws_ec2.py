# cloud/collectors/aws_ec2.py

import boto3
from cloud.models import CloudAccount, CloudResource
from cloud.cost.ec2_cost import calculate_ec2_hourly_cost
from ai_engine.tasks.detector_tasks import scan_cloud_for_opportunities


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

    for region_data in regions:

        region_name = region_data["RegionName"]

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
                        provider="aws"
                    )

                    CloudResource.objects.update_or_create(
                        cloud_account=cloud_account,
                        external_id=instance_id,
                        defaults={
                            "provider": provider,
                            "resource_type": "ec2",
                            "service": "compute",
                            "region": region_name,
                            "state": state,
                            "cost_per_hour": hourly_cost,
                            "metadata": instance,
                        },
                    )

    scan_cloud_for_opportunities.delay(
        cloud_account.id
    )