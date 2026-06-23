from cloud.pricing.aws import (
    AWSPricingProvider,
)

from cloud.pricing.gcp import (
    GCPPricingProvider,
)

from cloud.pricing.azure import (
    AzurePricingProvider,
)


PRICING_PROVIDERS = {
    "aws": AWSPricingProvider(),
    "gcp": GCPPricingProvider(),
    "azure": AzurePricingProvider(),
}