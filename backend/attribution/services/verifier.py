from decimal import Decimal

from billing.models import CostSnapshot


class SavingsVerifier:
    """
    Verifies that an optimization produced measurable savings.

    This is intentionally conservative: if the observed reduction
    is smaller than expected, we do not attribute the savings.
    """

    @classmethod
    def verify(
        cls,
        cloud_account,
        resource_id,
        expected_savings,
        date,
    ):
        """
        Returns:

        {
            "verified": bool,
            "actual_cost": Decimal,
            "observed_savings": Decimal,
            "confidence": float,
        }
        """

        snapshots = CostSnapshot.objects.filter(
            cloud_account=cloud_account,
            resource_id=resource_id,
            date=date,
        )

        actual_cost = (
            snapshots.first().cost
            if snapshots.exists()
            else Decimal("0")
        )

        expected = Decimal(str(expected_savings))

        observed = max(expected - actual_cost, Decimal("0"))

        if expected <= 0:
            confidence = 0.0
        else:
            confidence = float(
                min(
                    Decimal("1"),
                    observed / expected,
                )
            )

        return {
            "verified": confidence >= 0.80,
            "actual_cost": actual_cost,
            "observed_savings": observed,
            "confidence": confidence,
        }