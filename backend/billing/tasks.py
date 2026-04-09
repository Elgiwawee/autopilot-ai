# billing/task.py

from celery import shared_task
from django.db import models
from billing.services.revenue import create_revenue_share_from_ledger
from billing.models import CostSnapshot, SavingsAttribution, SavingsLedger
from billing.baseline.engine import BaselineEngine
from actions.models import ExecutionRecord


@shared_task(bind=True, max_retries=3)
def compute_savings(self, execution_id):
    execution = ExecutionRecord.objects.get(id=execution_id)

    decision = execution.decision
    plan = decision.plan

    account = plan.cloud_account
    resource = plan.resource

    resource_id = resource.id
    service = resource.service
    account = resource.cloud_account
    region = execution.before_state.get("region")
    date = execution.finished_at.date()

    # 🧠 BASELINE
    baseline_engine = BaselineEngine()
    baseline, stability, reasons = baseline_engine.compute(
        cloud_account=account,
        service=service,
        resource_id=resource_id,
        target_date=date,
    )

    if baseline is None:
        return

    # 📉 ACTUAL COST
    actual = CostSnapshot.objects.filter(
        cloud_account=account,
        service=service,
        resource_id=resource_id,
        date=date,
    ).aggregate(total=models.Sum("cost"))["total"] or 0

    # 💰 SAVINGS
    gross = baseline - actual
    gross = max(gross, 0)

    net = gross * stability * decision.confidence
    net = max(net, 0)

    attribution = SavingsAttribution.objects.create(
        execution=execution,
        baseline_cost=baseline,
        actual_cost=actual,
        savings=net,
        confidence=stability,
        metadata={
            "baseline_components": reasons,
            "gross": float(gross),
            "decision_confidence": decision.confidence,
        },
    )

    ledger = SavingsLedger.objects.create(
        cloud_account=account,
        execution=execution,
        amount=round(net, 2),
        currency="USD",
        period_start=date,
        period_end=date,
        checksum="TODO",
    )

    # 💸 PLATFORM REVENUE (MANDATORY)
    create_revenue_share_from_ledger(ledger)

    # 🚫 Prevent duplicate billing
    if SavingsLedger.objects.filter(execution=execution).exists():
        return

