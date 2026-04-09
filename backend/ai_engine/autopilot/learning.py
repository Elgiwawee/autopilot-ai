# ai_engine/autopilot/learning.py

import logging

from django.utils import timezone

from ai_engine.models.action_outcome import ActionOutcome
from actions.models import ActionExecution

from ai_engine.training.auto_retrain import maybe_trigger_retraining
from ai_engine.features.feature_builder import store_resource_features
from ai_engine.training.online_learning import update_online_model

logger = logging.getLogger(__name__)


def learn_from_outcome(plan, execution: ActionExecution, utilization, decision):
    """
    Enterprise Learning Pipeline

    Responsibilities:
    1. Store execution outcome
    2. Store ML features
    3. Update online model
    4. Trigger async retraining (NON-BLOCKING)
    """

    try:
        resource = plan.resource
        cloud_account = resource.cloud_account
        organization = cloud_account.organization

        success = execution.status == "success"

        execution_time = None
        if execution.executed_at and plan.created_at:
            execution_time = (
                execution.executed_at - plan.created_at
            ).total_seconds()

        # =============================
        # 1️⃣ STORE OUTCOME
        # =============================
        outcome = ActionOutcome.objects.create(
            organization=organization,
            cloud_account=cloud_account,
            resource_type=resource.resource_type,
            resource_id=resource.resource_id,
            action_type=plan.action_type,

            before_state=getattr(plan, "current_state", {}),
            after_state=getattr(plan, "proposed_state", {}),

            estimated_savings=float(
                getattr(plan, "estimated_savings", 0)
            ),

            success=success,
            execution_time_seconds=execution_time,
            failure_reason=execution.error_message,
            created_at=timezone.now(),
        )

        logger.info(f"[LEARNING] Outcome stored plan={plan.id}")

        # =============================
        # 2️⃣ FEATURE STORE
        # =============================
        store_resource_features(
            plan=plan,
            utilization=utilization,
            decision=decision,
            outcome=outcome,
        )

        # =============================
        # 3️⃣ ONLINE LEARNING (FAST)
        # =============================
        update_online_model(
            plan,
            utilization,
            decision,
            outcome,
        )

    except Exception:
        logger.exception("[LEARNING] Failed pipeline")

    # =============================
    # 4️⃣ ASYNC RETRAIN TRIGGER
    # =============================
    try:
        maybe_trigger_retraining.delay()
    except Exception:
        logger.warning("[LEARNING] Retraining trigger failed")