#control_plane/services/billing_service.py

from decimal import Decimal

from django.db.models import Sum
from django.utils.timezone import now

from billing.models import CostSnapshot


def build_billing_overview(organization):
    qs = CostSnapshot.objects.filter(
        cloud_account__organization=organization
    )

    today = now().date()

    current_month = qs.filter(
        date__year=today.year,
        date__month=today.month,
    )

    current_total = (
        current_month.aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0")
    )

    previous_month = today.month - 1

    previous_year = today.year

    if previous_month == 0:
        previous_month = 12
        previous_year -= 1

    last_total = (
        qs.filter(
            date__year=previous_year,
            date__month=previous_month,
        ).aggregate(
            total=Sum("cost")
        )["total"]
        or Decimal("0")
    )

    average = (
        qs.values("date")
        .annotate(total=Sum("cost"))
        .aggregate(avg=Sum("total"))["avg"]
        or Decimal("0")
    )

    forecast = current_total * Decimal("1.05")

    return {
        "current_month": float(current_total),
        "last_month": float(last_total),
        "average": float(average),
        "forecast": float(forecast),
    }