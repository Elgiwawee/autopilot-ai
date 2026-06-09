# billing/services/savings_service.py

from django.db.models import Sum, Count
from django.utils.timezone import now
from billing.models import SavingsEvent
from actions.models import OptimizationPlan

class SavingsService:
    """
    Domain service responsible for savings calculations.
    """

    # -------------------------------------------------------
    # Base Query Builder
    # -------------------------------------------------------

    @staticmethod
    def _base_queryset(organization):
        return SavingsEvent.objects.filter(
            organization=organization,
            is_billable=True,
        )

    # -------------------------------------------------------
    # Public API
    # -------------------------------------------------------

    @classmethod
    def summary(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
    ):
        qs = cls._base_queryset(organization)

        # Optional cloud filter (provider slug based)
        if cloud:
            qs = qs.filter(
                cloud=cloud
            )

        # Optional region filter (if relation exists)
        if region:
            qs = qs.filter(
                cloud_account__region=region
            )

        current_month = now().date().replace(day=1)

        lifetime = qs.aggregate(
            total_saved=Sum("savings_amount"),
            actions_taken=Count("id"),
        )

        monthly = qs.filter(
            occurred_at__date__gte=current_month
        ).aggregate(
            saved=Sum("savings_amount")
        )

        potential = (
            OptimizationPlan.objects.filter(
                cloud_account__organization=organization,
                status="PLANNED",
            )
            .aggregate(
                total=Sum("estimated_monthly_savings")
            )["total"] or 0
        )

        return {
            "currency": "USD",
            "current_month": {
                "savings": float(monthly["saved"] or 0),
            },
            "lifetime": {
                "total_saved": float(lifetime["total_saved"] or 0),
                "actions_taken": lifetime["actions_taken"] or 0,
            },
            "potential_monthly_savings": float(potential),
        }
    
        