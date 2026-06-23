import logging
from functools import lru_cache

import requests
from google.oauth2 import service_account

try:
    # Preferred import path for the generated client library.
    from google.cloud.billing_v1.services.cloud_catalog import CloudCatalogClient
except Exception:  # pragma: no cover
    CloudCatalogClient = None

from cloud.pricing.base import PricingProvider

logger = logging.getLogger(__name__)


class GCPPricingProvider(PricingProvider):
    """
    Production GCP pricing provider.

    Uses:
        Cloud Billing Catalog API

    This provider:
    - can be configured with a service account JSON payload
    - looks up live prices from the catalog
    - can prime the InstancePricing cache via sync_catalog()
    """

    DEFAULT_MACHINE_TYPES = (
        "e2-micro",
        "e2-small",
        "e2-medium",
        "e2-standard-2",
        "e2-standard-4",
        "e2-standard-8",
        "n2-standard-2",
        "n2-standard-4",
        "n2-standard-8",
        "a2-highgpu-1g",
        "a2-highgpu-2g",
    )

    DEFAULT_REGIONS = (
        "us-central1",
        "us-east1",
        "us-east4",
        "us-west1",
        "europe-west1",
        "europe-west4",
        "asia-east1",
        "asia-southeast1",
        "australia-southeast1",
    )

    def __init__(self):
        self.client = None
        self._service_account_json = None

    def configure(self, service_account_json):
        """
        Lazy initialization. Call this once before live lookups.
        """
        if not service_account_json:
            raise ValueError("service_account_json is required for GCP pricing")

        self._service_account_json = service_account_json

        if CloudCatalogClient is None:
            raise ImportError(
                "google-cloud-billing is not installed correctly. "
                "Run: python -m pip install --upgrade google-cloud-billing google-auth"
            )

        credentials = service_account.Credentials.from_service_account_info(
            service_account_json
        )
        self.client = CloudCatalogClient(credentials=credentials)

    def _ensure_client(self, service_account_json=None):
        if self.client is not None:
            return self.client

        if service_account_json is not None:
            self.configure(service_account_json)
            return self.client

        return None

    def _sku_matches(self, sku, instance_type: str, region: str) -> bool:
        description = str(getattr(sku, "description", "") or "").lower()
        machine = instance_type.lower().replace("_", "-")

        # Match by description first.
        if machine not in description and instance_type.lower() not in description:
            return False

        # Prefer region-aware SKUs when region info is available.
        sku_regions = [
            str(r).lower()
            for r in (getattr(sku, "service_regions", None) or [])
            if r
        ]

        if region and sku_regions:
            normalized_region = region.strip().lower()
            if normalized_region not in sku_regions:
                return False

        return True

    @lru_cache(maxsize=1024)
    def get_live_price(self, instance_type, region, service_account_json=None):
        """
        Query GCP Cloud Billing Catalog API for hourly price.
        """
        try:
            client = self._ensure_client(service_account_json)
            if client is None:
                return 0

            services = client.list_services()

            compute_service = None
            for service in services:
                if str(getattr(service, "display_name", "")).strip() == "Compute Engine":
                    compute_service = service.name
                    break

            if not compute_service:
                logger.warning("GCP Compute Engine service not found in catalog")
                return 0

            skus = client.list_skus(parent=compute_service)

            for sku in skus:
                if not self._sku_matches(sku, instance_type, region):
                    continue

                pricing_info = getattr(sku, "pricing_info", None) or []
                if not pricing_info:
                    continue

                expression = pricing_info[0].pricing_expression
                tiered_rates = getattr(expression, "tiered_rates", None) or []
                if not tiered_rates:
                    continue

                tier = tiered_rates[0]
                unit_price = tier.unit_price

                units = getattr(unit_price, "units", 0) or 0
                nanos = getattr(unit_price, "nanos", 0) or 0

                return float(units + nanos / 1_000_000_000)

        except Exception as exc:
            logger.exception("GCP pricing error for %s in %s", instance_type, region)

        return 0

    def sync_catalog(self, service_account_json=None):
        """
        Prime the InstancePricing cache for commonly used GCP machine types.

        Strategy:
        - use regions already seen in InstancePricing for GCP
        - otherwise use a curated default region list
        - store live prices into InstancePricing
        """
        from django.utils import timezone
        from cloud.models import CloudProvider, InstancePricing

        try:
            provider = CloudProvider.objects.get(code="gcp")
        except CloudProvider.DoesNotExist:
            logger.warning("GCP CloudProvider row missing; skipping pricing sync")
            return

        # Ensure we have a client.
        if self.client is None:
            if service_account_json is None and self._service_account_json is not None:
                service_account_json = self._service_account_json

            if service_account_json is not None:
                try:
                    self.configure(service_account_json)
                except Exception:
                    logger.exception("Unable to configure GCP pricing client")
                    return

        existing_regions = list(
            InstancePricing.objects.filter(provider=provider)
            .values_list("region", flat=True)
            .distinct()
        )
        regions = existing_regions or list(self.DEFAULT_REGIONS)

        for machine_type in self.DEFAULT_MACHINE_TYPES:
            for region in regions:
                price = self.get_live_price(
                    machine_type,
                    region,
                    service_account_json=service_account_json,
                )
                if price <= 0:
                    continue

                InstancePricing.objects.update_or_create(
                    provider=provider,
                    instance_type=machine_type,
                    region=region,
                    operating_system="linux",
                    pricing_model="on_demand",
                    defaults={
                        "price_per_hour": price,
                        "source": "gcp_billing_catalog",
                        "last_verified_at": timezone.now(),
                    },
                )