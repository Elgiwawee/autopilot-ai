# ai_engine/tasks/detector_tasks.py

from celery import shared_task
from cloud.models import CloudAccount
from ai_engine.optimizer.opportunity_detector import OpportunityDetector
from ai_engine.autopilot_engine import AutopilotEngine


@shared_task
def scan_cloud_for_opportunities(cloud_account_id):
    """
    Main AI pipeline:
    1. Detect opportunities (creates OptimizationPlan)
    2. Run autopilot (optional execution)
    """

    try:
        account = CloudAccount.objects.get(id=cloud_account_id)
    except CloudAccount.DoesNotExist:
        return

    # -----------------------------
    # STEP 1: DETECT OPPORTUNITIES
    # -----------------------------
    detector = OpportunityDetector()
    detector.run(account)

    # -----------------------------
    # STEP 2: RUN AUTOPILOT ENGINE
    # -----------------------------
    engine = AutopilotEngine()
    engine.run_for_organization(account.organization)