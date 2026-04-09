# ai_engine/training/auto_retrain.py

import logging
from django.core.cache import cache

from ai_engine.training.tasks import train_models

logger = logging.getLogger(__name__)

# Number of new samples required before retraining
THRESHOLD = 100

# Cache key
CACHE_KEY = "ai:new_training_samples"


def maybe_trigger_retraining():
    """
    Increment sample counter and trigger async model retraining
    when enough new samples have accumulated.
    """

    try:
        count = cache.get(CACHE_KEY, 0) + 1
        cache.set(CACHE_KEY, count, timeout=None)

        if count >= THRESHOLD:

            logger.info(
                "AI retraining triggered after %s new samples",
                count,
            )

            # Reset counter
            cache.set(CACHE_KEY, 0, timeout=None)

            # Trigger async training
            train_models.delay()

    except Exception:
        logger.exception("Failed to trigger AI retraining")