from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from billing.models import CostSnapshot


class BaselineService:
    """
    Computes baseline cost estimates for a resource
    using historical CostSnapshot records.
    """

    DEFAULT_LOOKBACK_DAYS = 30

    @classmethod
    def calculate(
        cls,
        cloud_account,
        resource_id,
        lookback_days=None,
    ):
        """
        Returns average historical daily cost.

        Returns Decimal("0") if insufficient history.
        """

        if lookback_days is None:
            lookback_days = cls.DEFAULT_LOOKBACK_DAYS

        since = (
            timezone.now().date()
            - timezone.timedelta(days=lookback_days)
        )

        queryset = CostSnapshot.objects.filter(
            cloud_account=cloud_account,
            resource_id=resource_id,
            date__gte=since,
        )

        average = queryset.aggregate(
            avg=Avg("cost")
        )["avg"]

        if average is None:
            return Decimal("0")

        return Decimal(str(average))

    @classmethod
    def monthly_projection(
        cls,
        cloud_account,
        resource_id,
        lookback_days=None,
    ):
        """
        Projects monthly spend from average daily cost.
        """

        daily = cls.calculate(
            cloud_account=cloud_account,
            resource_id=resource_id,
            lookback_days=lookback_days,
        )

        return daily * Decimal("30")

