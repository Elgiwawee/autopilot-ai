from celery import shared_task
from cloud.services.accounts import get_active_cloud_accounts
from cloud.services.infra import sync_cloud_account_resources


@shared_task
def collect_all_cloud_resources(org_id):
    accounts = get_active_cloud_accounts(org_id)

    for account in accounts:
        sync_cloud_account_resources(account)