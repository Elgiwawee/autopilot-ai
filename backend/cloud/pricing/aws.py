import json
import boto3

from functools import lru_cache

from cloud.pricing.base import PricingProvider


class AWSPricingProvider(PricingProvider):
    """
    AWS live pricing provider.

    Uses AWS Pricing API.

    This provider is intentionally stateless because
    caching is handled by:

        InstancePricing
            +
        lru_cache
    """

    def __init__(self):

        self.client = boto3.client(
            "pricing",
            region_name="us-east-1",
        )

    # --------------------------------------------------
    # LIVE LOOKUP
    # --------------------------------------------------

    @lru_cache(maxsize=1024)
    def get_live_price(
        self,
        instance_type,
        region,
    ):
        """
        Returns hourly on-demand Linux pricing.
        """

        try:

            response = self.client.get_products(
                ServiceCode="AmazonEC2",
                Filters=[
                    {
                        "Type": "TERM_MATCH",
                        "Field": "instanceType",
                        "Value": instance_type,
                    },
                    {
                        "Type": "TERM_MATCH",
                        "Field": "location",
                        "Value": self._region_name(
                            region
                        ),
                    },
                    {
                        "Type": "TERM_MATCH",
                        "Field": "operatingSystem",
                        "Value": "Linux",
                    },
                    {
                        "Type": "TERM_MATCH",
                        "Field": "preInstalledSw",
                        "Value": "NA",
                    },
                    {
                        "Type": "TERM_MATCH",
                        "Field": "capacitystatus",
                        "Value": "Used",
                    },
                    {
                        "Type": "TERM_MATCH",
                        "Field": "tenancy",
                        "Value": "Shared",
                    },
                ],
                MaxResults=1,
            )

            price_list = response.get(
                "PriceList",
                []
            )

            if not price_list:
                return 0

            item = json.loads(
                price_list[0]
            )

            terms = (
                item
                .get("terms", {})
                .get("OnDemand", {})
            )

            for term in terms.values():

                for dimension in (
                    term.get(
                        "priceDimensions",
                        {}
                    ).values()
                ):

                    return float(
                        dimension[
                            "pricePerUnit"
                        ]["USD"]
                    )

        except Exception as e:

            print(
                f"AWS pricing error: {e}"
            )

        return 0

    # --------------------------------------------------
    # DAILY CATALOG REFRESH
    # --------------------------------------------------

    def sync_catalog(self):
        """
        Future improvement:

        Download EC2 catalog
        and refresh frequently used
        instance families.

        For now live lookup is enough.
        """

        return

    # --------------------------------------------------
    # REGION TRANSLATION
    # --------------------------------------------------

    def _region_name(
        self,
        region_code,
    ):

        mapping = {

            "us-east-1":
                "US East (N. Virginia)",

            "us-east-2":
                "US East (Ohio)",

            "us-west-1":
                "US West (N. California)",

            "us-west-2":
                "US West (Oregon)",

            "eu-west-1":
                "EU (Ireland)",

            "eu-west-2":
                "EU (London)",

            "eu-west-3":
                "EU (Paris)",

            "eu-central-1":
                "EU (Frankfurt)",

            "eu-north-1":
                "EU (Stockholm)",

            "ap-south-1":
                "Asia Pacific (Mumbai)",

            "ap-southeast-1":
                "Asia Pacific (Singapore)",

            "ap-southeast-2":
                "Asia Pacific (Sydney)",

            "ap-northeast-1":
                "Asia Pacific (Tokyo)",

            "ca-central-1":
                "Canada (Central)",
        }

        return mapping.get(
            region_code,
            "US East (N. Virginia)",
        )