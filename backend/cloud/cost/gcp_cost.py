# cloud/cost/gcp_cost.py

from cloud.services.pricing_service import (
    PricingService,
)


def calculate_gcp_hourly_cost(
    instance_metadata,
    provider="gcp",
):
    """
    Compute Engine pricing lookup.

    instance_metadata is the raw
    GCP instance payload.
    """

    machine_type = (
        instance_metadata
        .get("machineType", "")
        .split("/")[-1]
    )

    zone = (
        instance_metadata
        .get("zone", "")
        .split("/")[-1]
    )

    region = "-".join(
        zone.split("-")[:-1]
    )

    return PricingService.get_hourly_price(
        provider=provider,
        instance_type=machine_type,
        region=region,
    )