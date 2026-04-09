# billing/tasks/savings.py

from celery import shared_task
from ai_engine.reinforcement.trainer import RLTrainer
from billing.models import CostSnapshot, BaselineSnapshot, SavingsEvent


@shared_task
def compute_savings_for_period(organization_id, cloud):
    baseline = BaselineSnapshot.objects.filter(
        organization_id=organization_id,
        cloud=cloud,
    ).latest("computed_at")

    current = CostSnapshot.objects.filter(
        organization_id=organization_id,
        cloud=cloud,
    ).latest("period_end")

    savings = baseline.baseline_cost - current.total_cost

    if savings > 0:
        SavingsEvent.objects.create(
            organization_id=organization_id,
            cloud=cloud,
            resource_id="GLOBAL",
            baseline_cost=baseline.baseline_cost,
            actual_cost=current.total_cost,
            savings_amount=savings,
            action_id="AUTOPILOT",
            confidence=0.92,
        )

        trainer = RLTrainer()
        trainer.update(action_id=baseline.action_type)

