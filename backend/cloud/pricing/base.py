from abc import ABC
from abc import abstractmethod


class PricingProvider(ABC):

    @abstractmethod
    def get_live_price(
        self,
        instance_type,
        region,
    ):
        pass

    @abstractmethod
    def sync_catalog(self):
        pass