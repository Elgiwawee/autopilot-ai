# control_plane/tasks.py

from celery import shared_task
from django.db import transaction
from django.utils import timezone
import logging

from accounts.models import Organization
from cloud.models import CloudAccount

from ai_engine.autopilot_engine import AutopilotEngine
from cloud.collectors.aws_ec2 import collect_ec2_instances

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def run_autopilot_for_org(self, organization_id):

    try:

        org = Organization.objects.get(
            id=organization_id
        )

        logger.info(
            f"Starting autopilot for org={org.id}"
        )

        engine = AutopilotEngine()

        engine.run_for_organization(org)

        logger.info(
            f"Autopilot completed for org={org.id}"
        )

    except Organization.DoesNotExist:

        logger.error(
            f"Organization not found: {organization_id}"
        )

    except Exception as e:

        logger.exception(
            f"Autopilot failed for org={organization_id}: {str(e)}"
        )

        raise


@shared_task
def discover_cloud_account(cloud_account_id):

    try:

        account = CloudAccount.objects.get(
            id=cloud_account_id
        )

        logger.info(
            f"Starting discovery for account {account.id}"
        )

        if account.provider.code == "aws":

            collect_ec2_instances(account.id)

        account.status = CloudAccount.STATUS_CONNECTED
        account.error_message = None
        account.last_checked_at = timezone.now()

        account.save(
            update_fields=[
                "status",
                "error_message",
                "last_checked_at",
            ]
        )

        logger.info(
            f"Discovery completed for account {account.id}"
        )

    except CloudAccount.DoesNotExist:

        logger.error(
            f"Cloud account {cloud_account_id} not found"
        )

    except Exception as e:

        logger.exception(
            f"Discovery failed: {str(e)}"
        )

        try:

            account = CloudAccount.objects.get(
                id=cloud_account_id
            )

            account.status = CloudAccount.STATUS_FAILED
            account.error_message = str(e)
            account.last_checked_at = timezone.now()

            account.save(
                update_fields=[
                    "status",
                    "error_message",
                    "last_checked_at",
                ]
            )

        except Exception:
            pass

@shared_task
def schedule_autopilot():

    organizations = Organization.objects.filter(
        is_active=True
    )

    for org in organizations:
        run_autopilot_for_org.delay(org.id)