from functools import lru_cache

from google.cloud import billing_v1
from google.oauth2 import service_account

from cloud.pricing.base import PricingProvider


class GCPPricingProvider(PricingProvider):
    """
    Production GCP pricing provider.

    Uses:

        Cloud Billing Catalog API

    Docs:
    https://cloud.google.com/billing/docs/reference/rest

    Returns on-demand hourly pricing.
    """

    def __init__(self):

        self.client = None

    def configure(
        self,
        service_account_json,
    ):
        """
        Lazy initialization.

        Called by PricingService when needed.
        """

        credentials = (
            service_account.Credentials
            .from_service_account_info(
                service_account_json
            )
        )

        self.client = (
            billing_v1.CloudCatalogClient(
                credentials=credentials
            )
        )

    @lru_cache(maxsize=1024)
    def get_live_price(
        self,
        instance_type,
        region,
    ):
        """
        Query GCP Cloud Billing Catalog.

        Returns hourly USD cost.
        """

        if self.client is None:
            return 0

        try:

            services = (
                self.client.list_services()
            )

            compute_service = None

            for service in services:

                if (
                    service.display_name
                    == "Compute Engine"
                ):
                    compute_service = (
                        service.name
                    )
                    break

            if not compute_service:
                return 0

            skus = self.client.list_skus(
                parent=compute_service
            )

            for sku in skus:

                description = (
                    sku.description.lower()
                )

                if (
                    instance_type.lower()
                    not in description
                ):
                    continue

                pricing_info = (
                    sku.pricing_info
                )

                if not pricing_info:
                    continue

                expression = (
                    pricing_info[0]
                    .pricing_expression
                )

                if (
                    not expression.tiered_rates
                ):
                    continue

                tier = (
                    expression.tiered_rates[0]
                )

                units = (
                    tier.unit_price.units
                )

                nanos = (
                    tier.unit_price.nanos
                )

                return float(
                    units
                    + nanos / 1_000_000_000
                )

        except Exception as exc:

            print(
                f"GCP pricing error: {exc}"
            )

        return 0

    def sync_catalog(self):
        """
        Future enhancement:

        Bulk sync popular machine types
        into InstancePricing.

        Example:

            e2-micro
            e2-small
            e2-medium
            n2-standard-2
            n2-standard-4
            a2-highgpu-1g
            a2-highgpu-2g
        """

        return