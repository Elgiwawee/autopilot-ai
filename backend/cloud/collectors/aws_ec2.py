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

    assumed = sts.assume_role(
        RoleArn=cloud_account.role_arn,
        RoleSessionName="cloud-autopilot-session",
        ExternalId=cloud_account.external_id,  # ✅ IMPORTANT
    )

    creds = assumed["Credentials"]

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=cloud_account.region or "us-east-1",
    )

    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):

                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]

                # -----------------------------
                # COST CALCULATION
                # -----------------------------
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
                        "region": ec2.meta.region_name,
                        "state": state,
                        "cost_per_hour": hourly_cost,
                        "metadata": instance,
                    },
                )

    # 🔥 TRIGGER AI DETECTOR
    scan_cloud_for_opportunities.delay(cloud_account.id)