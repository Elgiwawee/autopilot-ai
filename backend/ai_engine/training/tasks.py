# ai_engine/training/tasks.py

import logging
from celery import shared_task
from ai_engine.training.train_model import train_risk_model

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def train_models(self):
    logger.info("[AI] Training started")

    train_risk_model()

    logger.info("[AI] Training completed")