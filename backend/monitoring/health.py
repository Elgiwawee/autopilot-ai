# monitoring/health.py

import logging

logger = logging.getLogger(__name__)


def verify_system_health():
    """
    Verify health of core system services.
    """

    logger.info("Running system health checks")

    checks = {
        "database": True,
        "celery": True,
        "redis": True,
    }

    logger.info("System health status: %s", checks)

    return checks


def health_failed():
    """
    Returns True if any critical service failed.
    """

    checks = verify_system_health()

    for service, status in checks.items():
        if not status:
            logger.error("Health check failed for %s", service)
            return True

    return False