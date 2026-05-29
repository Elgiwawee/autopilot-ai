# cloud/tasks/collect_inventory.py

from celery import shared_task
from cloud.services.accounts import get_active_cloud_accounts
from cloud.services.infra import sync_cloud_account_resources

import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def collect_all_cloud_resources(self, org_id):

    logger.info(
        f"Starting cloud inventory sync "
        f"for org {org_id}"
    )

    accounts = get_active_cloud_accounts(org_id)

    logger.info(
        f"Found {accounts.count()} active cloud accounts"
    )

    for account in accounts:

        try:
            logger.info(
                f"Syncing account {account.id} "
                f"({account.provider.slug})"
            )

            sync_cloud_account_resources(account)

            logger.info(
                f"Completed sync for account "
                f"{account.id}"
            )

        except Exception as e:
            logger.exception(
                f"Inventory sync failed for "
                f"{account.id}: {str(e)}"
            )

    logger.info(
        f"Completed inventory sync for org {org_id}"
    )