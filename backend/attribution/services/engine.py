# attribution/services/engine.py

from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from billing.models import CostSnapshot
from attribution.services.baseline import BaselineService


class AttributionEngine:
    """
    Computes realized savings after an optimization execution.

    This service DOES NOT save anything to the database.
    It only calculates values.

    Persistence is handled separately by ledger.py.
    """

    @classmethod
    def compute(cls, execution):

        optimization = execution.plan or execution.optimization

        if optimization is None:
            raise RuntimeError(
                "Execution is not linked to a plan."
            )

        cloud_account = optimization.cloud_account

        resource_id = getattr(
            optimization,
            "provider_resource_id",
            None,
        ) or getattr(
            optimization,
            "resource_id",
            None,
        )

        service = getattr(
            optimization,
            "resource_type",
            "",
        )

        today = timezone.now().date()

        baseline_cost = BaselineService.calculate(
            cloud_account=cloud_account,
            resource_id=resource_id,
        )

        actual_cost = (
            CostSnapshot.objects.filter(
                cloud_account=cloud_account,
                resource_id=resource_id,
                date=today,
            ).aggregate(
                total=Sum("cost")
            )["total"]
            or Decimal("0")
        )

        realized_savings = baseline_cost - actual_cost

        if realized_savings < 0:

            realized_savings = Decimal("0")

        return {
            "optimization": optimization,
            "execution": execution,
            "cloud_account": cloud_account,
            "resource_id": resource_id,
            "service": service,
            "baseline_cost": baseline_cost,
            "actual_cost": actual_cost,
            "realized_savings": realized_savings,
            "confidence": getattr(
                optimization,
                "confidence",
                1.0,
            ),
            "date": today,
        }

