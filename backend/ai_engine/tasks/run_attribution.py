# ai_engine/tasks/run_attribution.py


from celery import shared_task
from ai_engine.attribution.splitter import split_service_cost
from ai_engine.models.resource_usage import ResourceUsage
from billing.models import CostSnapshot   # ✅ FIXED


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60)
def run_attribution(self, snapshot_id):

    # ✅ Load correct model
    snapshot = CostSnapshot.objects.get(id=snapshot_id)

    # ✅ Resource usage stays same
    usages = ResourceUsage.objects.filter(
        cloud_account=snapshot.cloud_account,
        service=snapshot.service,
        date=snapshot.date,
    )

    # ✅ Split cost across resources
    split_service_cost(snapshot, usages)