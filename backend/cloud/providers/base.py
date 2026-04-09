# cloud/providers/base.py

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable, Dict, Any, List


class CloudProviderInterface(ABC):
    """
    Contract every cloud provider must implement.
    """

    def __init__(self, cloud_account):
        self.cloud_account = cloud_account

    # ---------- INVENTORY ----------

    @abstractmethod
    def fetch_resources(self) -> Iterable[Dict[str, Any]]:
        """
        Normalized resource inventory.
        Required keys:
          - resource_id
          - resource_type
          - region
          - metadata
        """
        pass

    # ---------- METRICS ----------

    def fetch_metrics(
        self,
        resource_ids: List[str],
        metric_name: str,
        start_date: date,
        end_date: date
    ) -> Iterable[Dict[str, Any]]:
        """
        Optional.
        Must return:
          - resource_id
          - timestamp
          - value
        """
        raise NotImplementedError

    # ---------- COST ----------

    @abstractmethod
    def fetch_costs(
        self,
        start_date: date,
        end_date: date
    ) -> Iterable[Dict[str, Any]]:
        """
        Must return:
          - service
          - resource_id (nullable)
          - date
          - cost
        """
        pass

    # ---------- EXECUTION ----------

    @abstractmethod
    def execute_action(self, action) -> None:
        pass

    @abstractmethod
    def rollback(self, action) -> None:
        pass
