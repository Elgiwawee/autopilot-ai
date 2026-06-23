# cloud/tasks/pricing_sync.py

from celery import shared_task

from cloud.services.pricing_service import (
    PricingService,
)

from cloud.pricing.registry import (
    PRICING_PROVIDERS,
)


@shared_task
def refresh_pricing_catalog():

    for provider in (
        PRICING_PROVIDERS.keys()
    ):

        try:

            PricingService.refresh_provider(
                provider
            )

        except Exception as exc:

            print(
                f"Pricing refresh failed for "
                f"{provider}: {exc}"
            )