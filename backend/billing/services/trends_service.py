# billing/services/trends_service.py

from django.db.models import Sum

from billing.models import CostSnapshot


class TrendService:

    @classmethod
    def cost_trend(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
        days: int = 7,
    ):
        """
        Returns aggregated daily cost trend for an organization.
        """

        qs = CostSnapshot.objects.filter(
            cloud_account__organization=organization
        )

        if cloud:
            qs = qs.filter(provider__iexact=cloud)

        if region:
            qs = qs.filter(region__iexact=region)

        qs = (
            qs.values("date")
            .annotate(total_cost=Sum("cost"))
            .order_by("-date")[:days]
        )

        trend = list(reversed(qs))

        return [
            {
                "date": row["date"].isoformat() if hasattr(row["date"], "isoformat") else str(row["date"]),
                "cost": float(row["total_cost"] or 0),
            }
            for row in trend
        ]