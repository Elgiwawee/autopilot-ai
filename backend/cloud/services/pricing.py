# cloud/services/pricing.py

import boto3
import json
from functools import lru_cache
from cloud.models import InstancePricing


class AWSPricingService:
    def __init__(self):
        self.client = boto3.client("pricing", region_name="us-east-1")

    @lru_cache(maxsize=512)
    def get_ec2_price(self, instance_type, region):
        try:
            response = self.client.get_products(
                ServiceCode="AmazonEC2",
                Filters=[
                    {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                    {"Type": "TERM_MATCH", "Field": "location", "Value": self._region_name(region)},
                    {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                    {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                    {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
                    {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                ],
                MaxResults=1,
            )

            price_list = response.get("PriceList", [])
            if not price_list:
                return 0

            price_item = json.loads(price_list[0])

            terms = price_item.get("terms", {}).get("OnDemand", {})
            for term in terms.values():
                for dimension in term.get("priceDimensions", {}).values():
                    return float(dimension["pricePerUnit"]["USD"])

        except Exception as e:
            print("AWS pricing error:", e)

        return 0

    def _region_name(self, region_code):
        mapping = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "EU (Ireland)",
        }
        return mapping.get(region_code, "US East (N. Virginia)")


pricing_service = AWSPricingService()


def get_hourly_price(provider, instance_type, region, operating_system="linux"):
    """
    Unified pricing entry point:
    1. Try DB
    2. Fallback to AWS API
    3. Cache in DB
    """

    # -----------------------------
    # 1. TRY DB FIRST (FAST)
    # -----------------------------
    try:
        pricing = InstancePricing.objects.get(
            provider=provider,
            instance_type=instance_type,
            region=region,
            operating_system=operating_system,
            pricing_model="on_demand",
        )
        return float(pricing.price_per_hour)

    except InstancePricing.DoesNotExist:
        pass

    # -----------------------------
    # 2. FETCH FROM AWS API
    # -----------------------------
    if provider == "aws":
        price = pricing_service.get_ec2_price(instance_type, region)

        if price > 0:
            # -----------------------------
            # 3. SAVE TO DB (CACHE)
            # -----------------------------
            InstancePricing.objects.create(
                provider=provider,
                instance_type=instance_type,
                region=region,
                operating_system=operating_system,
                pricing_model="on_demand",
                price_per_hour=price,
            )

        return price

    return 0