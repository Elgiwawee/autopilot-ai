from celery import shared_task
from datetime import date, timedelta
from cloud.providers.factory import get_provider
from cloud.services.accounts import get_active_cloud_accounts


@shared_task
def sync_cloud_costs(org_id):
    accounts = get_active_cloud_accounts(org_id)

    end = date.today()
    start = end - timedelta(days=1)

    for acc in accounts:
        provider = get_provider(acc)
        costs = provider.fetch_costs(start, end)

        # store in your billing DB