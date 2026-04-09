# ai_engine/autopilot/loop.py

import logging
from celery import shared_task
from django.utils import timezone

from ai_engine.autopilot.state import AutopilotState
from ai_engine.autopilot.safety import kill_switch_enabled, can_act
from ai_engine.autopilot.rollback import rollback_if_needed
from ai_engine.autopilot.circuit_breaker import circuit_breaker_open

from monitoring.services.metrics_collector import collect_metrics
from ai_engine.services.recommendation_service import generate_recommendations
from actions.services.executor import execute_plan
from monitoring.health import health_failed

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 5},
)
def autopilot_loop(self, organization_id):
    """
    Enterprise autopilot loop.
    Fully safe, observable, and fault-tolerant.
    """

    logger.info(f"[AUTOPILOT] Start org={organization_id}")

    # 🔴 Kill switch
    if kill_switch_enabled():
        logger.warning("[AUTOPILOT] Kill switch active")
        return "disabled"

    # 🚫 Circuit breaker
    if circuit_breaker_open(organization_id):
        logger.error("[AUTOPILOT] Circuit breaker OPEN")
        return "circuit_open"

    try:
        # =============================
        # STATE: OBSERVE
        # =============================
        state = AutopilotState.OBSERVE
        metrics = collect_metrics(organization_id)

        # =============================
        # STATE: SIMULATE
        # =============================
        state = AutopilotState.SIMULATE
        plans = generate_recommendations(organization_id, metrics)

        if not plans:
            return "no_plans"

        # =============================
        # STATE: ACT
        # =============================
        if can_act(organization_id):
            state = AutopilotState.ACT

            executed = 0

            for plan in plans:
                try:
                    if plan.dry_run:
                        continue  # simulation only

                    execute_plan(plan)
                    executed += 1

                except Exception:
                    logger.exception(f"[AUTOPILOT] Execution failed plan={plan.id}")

        # =============================
        # STATE: VERIFY
        # =============================
        state = AutopilotState.VERIFY
        verify_health(organization_id)

        # =============================
        # STATE: ROLLBACK
        # =============================
        if health_failed(organization_id):
            state = AutopilotState.ROLLBACK
            rollback_if_needed(organization_id)

        logger.info(f"[AUTOPILOT] Completed org={organization_id}")
        return "success"

    except Exception as e:
        logger.exception(f"[AUTOPILOT] Crash org={organization_id}")
        raise self.retry(exc=e)