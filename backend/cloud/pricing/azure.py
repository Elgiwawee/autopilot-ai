import logging
from functools import lru_cache
from typing import Iterable

import requests

from cloud.pricing.base import PricingProvider

logger = logging.getLogger(__name__)


class AzurePricingProvider(PricingProvider):
    """
    Production Azure pricing provider.

    Uses:
        Azure Retail Prices API

    This provider:
    - looks up live prices
    - falls back to the first matching SKU if an exact region match is absent
    - can prime the InstancePricing cache via sync_catalog()
    """

    BASE_URL = "https://prices.azure.com/api/retail/prices"

    # Practical starter list for cache priming.
    # You can expand this later without changing the API behavior.
    DEFAULT_VM_SIZES = (
        "Standard_B1s",
        "Standard_B2s",
        "Standard_B4ms",
        "Standard_D2s_v5",
        "Standard_D4s_v5",
        "Standard_D8s_v5",
        "Standard_E2s_v5",
        "Standard_E4s_v5",
        "Standard_NC4as_T4_v3",
        "Standard_NC8as_T4_v3",
    )

    DEFAULT_REGIONS = (
        "eastus",
        "eastus2",
        "westus2",
        "westus3",
        "centralus",
        "westeurope",
        "northeurope",
        "uksouth",
        "southeastasia",
        "australiaeast",
    )

    def _fetch_prices(self, instance_type: str, region: str):
        query = (
            "serviceName eq 'Virtual Machines' "
            f"and armSkuName eq '{instance_type}'"
        )

        response = requests.get(
            self.BASE_URL,
            params={"$filter": query},
            timeout=20,
        )

        if response.status_code != 200:
            logger.warning(
                "Azure pricing API returned %s for %s in %s",
                response.status_code,
                instance_type,
                region,
            )
            return []

        return response.json().get("Items", []) or []

    @lru_cache(maxsize=1024)
    def get_live_price(self, instance_type, region):
        """
        Query Azure Retail Prices API for the best hourly price.
        """
        try:
            items = self._fetch_prices(instance_type, region)

            if not items:
                return 0

            normalized_region = (region or "").strip().lower()

            # Prefer an exact region match.
            for item in items:
                item_region = str(item.get("armRegionName", "")).strip().lower()
                if item_region == normalized_region:
                    return float(item.get("retailPrice", 0) or 0)

            # Fallback to first available SKU.
            return float(items[0].get("retailPrice", 0) or 0)

        except Exception as exc:
            logger.exception("Azure pricing error for %s in %s", instance_type, region)
            return 0

    def sync_catalog(self):
        """
        Prime the InstancePricing cache for commonly used Azure VM sizes.

        Strategy:
        - use regions already seen in InstancePricing for Azure
        - otherwise use a curated default region list
        - store live prices into InstancePricing
        """
        from django.utils import timezone
        from cloud.models import CloudProvider, InstancePricing

        try:
            provider = CloudProvider.objects.get(code="azure")
        except CloudProvider.DoesNotExist:
            logger.warning("Azure CloudProvider row missing; skipping pricing sync")
            return

        existing_regions = list(
            InstancePricing.objects.filter(provider=provider)
            .values_list("region", flat=True)
            .distinct()
        )
        regions = existing_regions or list(self.DEFAULT_REGIONS)

        for vm_size in self.DEFAULT_VM_SIZES:
            for region in regions:
                price = self.get_live_price(vm_size, region)
                if price <= 0:
                    continue

                InstancePricing.objects.update_or_create(
                    provider=provider,
                    instance_type=vm_size,
                    region=region,
                    operating_system="linux",
                    pricing_model="on_demand",
                    defaults={
                        "price_per_hour": price,
                        "source": "azure_retail_api",
                        "last_verified_at": timezone.now(),
                    },
                )