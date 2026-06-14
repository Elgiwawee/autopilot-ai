# billing/tasks/cost_sync.py

from celery import shared_task
from datetime import date, timedelta

from accounts.models import Organization
from billing.models import CostSnapshot
from cloud.providers.factory import get_provider
from cloud.services.accounts import get_active_cloud_accounts


@shared_task
def sync_cloud_costs(org_id):

    organization = Organization.objects.get(id=org_id)

    accounts = get_active_cloud_accounts(organization)

    end = date.today()
    start = end - timedelta(days=1)

    for account in accounts:

        try:

            provider = get_provider(account)

            costs = provider.fetch_costs(
                start_date=start,
                end_date=end,
            )

            for item in costs:

                CostSnapshot.objects.update_or_create(

                    cloud_account=account,

                    resource_id=item.get("resource_id"),

                    date=item["date"],

                    defaults={
                        "provider": account.provider.code.upper(),
                        "service": item.get("service", "UNKNOWN"),
                        "region": item.get("region", "global"),
                        "cost": item["cost"],
                        "usage_quantity": item.get("usage", 0),
                        "currency": item.get("currency", "USD"),
                    },
                )

        except Exception as exc:

            print(
                f"Cost sync failed for {account.id}: {exc}"
            )