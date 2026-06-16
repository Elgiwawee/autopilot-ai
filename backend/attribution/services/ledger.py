from decimal import Decimal

from django.db import transaction

from billing.models import (
    SavingsEvent,
    SavingsAttribution,
    SavingsLedger,
    RevenueShare,
)


class LedgerService:
    """
    Persist attribution results into billing tables.

    This is the single place responsible for creating:

    - SavingsEvent
    - SavingsAttribution
    - SavingsLedger
    - RevenueShare
    """

    PLATFORM_FEE_PERCENT = Decimal("20.0")

    @classmethod
    @transaction.atomic
    def record(cls, result):

        execution = result["execution"]
        optimization = result["optimization"]
        cloud_account = result["cloud_account"]

        baseline_cost = result["baseline_cost"]
        actual_cost = result["actual_cost"]
        savings = result["realized_savings"]

        # --------------------------------------------------
        # Prevent duplicate processing
        # --------------------------------------------------

        if SavingsEvent.objects.filter(
            action_id=str(execution.id)
        ).exists():

            return

        # --------------------------------------------------
        # Savings Event
        # --------------------------------------------------

        savings_event = SavingsEvent.objects.create(
            organization=cloud_account.organization,
            cloud=cloud_account.provider.code,
            resource_id=optimization.resource_id,
            baseline_cost=baseline_cost,
            actual_cost=actual_cost,
            savings_amount=savings,
            action_id=str(execution.id),
            confidence=optimization.confidence,
            region=(
    		optimization.current_state.get("region", "")
    		if optimization.current_state
    		else ""
		),
        )

        # --------------------------------------------------
        # Savings Attribution
        # --------------------------------------------------

        attribution = SavingsAttribution.objects.create(
            execution=execution,
            resource_id=optimization.resource_id,
            baseline_cost=baseline_cost,
            actual_cost=actual_cost,
            gross_savings=savings,
            net_savings=savings,
            confidence=optimization.confidence,
            explanation=(
                "Autopilot realized savings attribution."
            ),
        )

        # --------------------------------------------------
        # Savings Ledger
        # --------------------------------------------------

        ledger = SavingsLedger.objects.create(
            cloud_account=cloud_account,
            attribution=attribution,
            amount=savings,
            currency="USD",
            period_start=result["date"],
            period_end=result["date"],
            checksum=f"{execution.id}-{optimization.resource_id}",
        )

        # --------------------------------------------------
        # Revenue Share
        # --------------------------------------------------

        platform_fee = (
            savings
            * cls.PLATFORM_FEE_PERCENT
            / Decimal("100")
        )

        RevenueShare.objects.create(
            organization=cloud_account.organization,
            savings_event=savings_event,
            pct=float(cls.PLATFORM_FEE_PERCENT),
            amount_due=platform_fee,
        )

        return ledger

