# billing/services/savings_attribution.py

from decimal import Decimal
from datetime import date

from billing.baseline.engine import BaselineEngine
from billing.models import SavingsEvent


class SavingsAttributionService:

    @classmethod
    def record(cls, execution):
        optimization = execution.optimization

        engine = BaselineEngine()

        baseline, confidence, explanations = engine.compute(
            cloud_account=optimization.cloud_account,
            service=optimization.resource_type,
            resource_id=optimization.resource_id,
            target_date=date.today(),
        )

        if baseline is None:
            # Fallback until enough history exists
            baseline = Decimal(
                str(optimization.estimated_monthly_savings)
            )

        baseline = Decimal(str(baseline))

        #
        # Temporary approximation.
        #
        # Later we'll pull the post-action value
        # from CostSnapshot after billing sync.
        #
        actual_cost = Decimal("0.00")

        savings = baseline - actual_cost

        return SavingsEvent.objects.create(
            organization=optimization.cloud_account.organization,
            cloud=optimization.cloud_account.provider.code.lower(),
            resource_id=optimization.resource_id,
            baseline_cost=baseline,
            actual_cost=actual_cost,
            savings_amount=savings,
            action_id=str(execution.id),
            confidence=confidence,
            is_billable=True,
        )