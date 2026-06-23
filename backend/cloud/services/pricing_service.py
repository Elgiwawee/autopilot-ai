# cloud/services/pricing_service.py

from django.utils import timezone

from cloud.models import (
    CloudProvider,
    InstancePricing,
)

from cloud.pricing.registry import (
    PRICING_PROVIDERS,
)


class PricingService:
    """
    Unified pricing layer.

    Flow:

    DB Cache
       ↓
    Cloud Provider Pricing API
       ↓
    Store Cache
       ↓
    Return Price
    """

    @classmethod
    def get_hourly_price(
        cls,
        provider,
        instance_type,
        region,
        operating_system="linux",
        pricing_model="on_demand",
    ):

        provider_obj = CloudProvider.objects.get(
            code=provider
        )

        cached = (
            InstancePricing.objects.filter(
                provider=provider_obj,
                instance_type=instance_type,
                region=region,
                operating_system=operating_system,
                pricing_model=pricing_model,
            )
            .first()
        )

        if cached:
            return float(
                cached.price_per_hour
            )

        provider_engine = (
            PRICING_PROVIDERS.get(
                provider
            )
        )

        if not provider_engine:
            return 0

        price = provider_engine.get_live_price(
            instance_type=instance_type,
            region=region,
        )

        if price > 0:

            InstancePricing.objects.update_or_create(
                provider=provider_obj,
                instance_type=instance_type,
                region=region,
                operating_system=operating_system,
                pricing_model=pricing_model,
                defaults={
                    "price_per_hour": price,
                    "source": "api",
                    "last_verified_at": timezone.now(),
                },
            )

        return float(price)

    @classmethod
    def refresh_provider(
        cls,
        provider_code,
    ):

        provider_engine = (
            PRICING_PROVIDERS.get(
                provider_code
            )
        )

        if not provider_engine:
            return

        provider_engine.sync_catalog()

    @classmethod
    def refresh_all(cls):

        for provider_code in (
            PRICING_PROVIDERS.keys()
        ):

            cls.refresh_provider(
                provider_code
            )