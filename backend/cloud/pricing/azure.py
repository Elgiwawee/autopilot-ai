import requests

from functools import lru_cache

from cloud.pricing.base import PricingProvider


class AzurePricingProvider(
    PricingProvider
):
    """
    Production Azure pricing provider.

    Uses:

        Azure Retail Prices API

    Docs:
    https://prices.azure.com/api/retail/prices

    Returns:
        On-demand hourly VM pricing
    """

    BASE_URL = (
        "https://prices.azure.com/api/retail/prices"
    )

    @lru_cache(maxsize=1024)
    def get_live_price(
        self,
        instance_type,
        region,
    ):

        try:

            query = (
                "serviceName eq 'Virtual Machines' "
                f"and armSkuName eq '{instance_type}'"
            )

            response = requests.get(
                self.BASE_URL,
                params={
                    "$filter": query,
                },
                timeout=20,
            )

            if response.status_code != 200:

                return 0

            items = (
                response.json()
                .get(
                    "Items",
                    [],
                )
            )

            #
            # Prefer exact region match
            #

            for item in items:

                if (
                    item.get(
                        "armRegionName"
                    )
                    == region
                ):

                    return float(
                        item.get(
                            "retailPrice",
                            0,
                        )
                    )

            #
            # Fallback:
            # return first available SKU price
            #

            if items:

                return float(
                    items[0].get(
                        "retailPrice",
                        0,
                    )
                )

        except Exception as exc:

            print(
                f"Azure pricing error: {exc}"
            )

        return 0

    def sync_catalog(self):
        """
        Future enhancement:

        Periodically preload
        popular Azure VM families.

        Examples:

            Standard_B1s
            Standard_B2s
            Standard_D2s_v5
            Standard_D4s_v5
            Standard_NC4as_T4_v3
            Standard_NC8as_T4_v3

        and save them into
        InstancePricing.
        """

        return