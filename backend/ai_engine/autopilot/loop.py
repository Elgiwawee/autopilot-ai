import logging

from celery import shared_task

from accounts.models import Organization
from ai_engine.autopilot_engine import AutopilotEngine

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 5},
)
def autopilot_loop(self, organization_id):
    """
    Celery entrypoint for Autopilot.

    This task is intentionally lightweight.
    All orchestration lives inside AutopilotEngine.
    """

    logger.info(
        "[AUTOPILOT] Starting organization %s",
        organization_id,
    )

    organization = Organization.objects.get(
        id=organization_id
    )

    engine = AutopilotEngine()

    return engine.run_for_organization(
        organization
    )