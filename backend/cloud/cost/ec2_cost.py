# cloud/cost/ec2_cost.py

from cloud.services.pricing import get_hourly_price


def calculate_ec2_hourly_cost(instance_metadata, provider):
    instance_type = instance_metadata.get("InstanceType")

    region = instance_metadata.get("Placement", {}).get("AvailabilityZone", "")
    region = region[:-1] if region else "us-east-1"

    return get_hourly_price(
        provider=provider,
        instance_type=instance_type,
        region=region,
    )