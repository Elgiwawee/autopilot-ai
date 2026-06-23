from cloud.services.pricing_service import (
    PricingService,
)


def calculate_azure_hourly_cost(
    vm,
    provider="azure",
):
    """
    Azure VM pricing lookup.
    """

    vm_size = (
        vm.get(
            "hardwareProfile",
            {},
        )
        .get("vmSize")
    )

    location = vm.get("location")

    return PricingService.get_hourly_price(
        provider=provider,
        instance_type=vm_size,
        region=location,
    )