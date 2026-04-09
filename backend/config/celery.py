# config/celery.py

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# ------------------------------
# Celery Beat Schedule
# ------------------------------

app.conf.beat_schedule = {

    # Collect AWS metrics
    "collect-aws-metrics": {
        "task": "cloud.tasks.collect_aws_ec2_task",
        "schedule": crontab(minute="*/5"),
    },

    # Kubernetes metrics
    "collect-k8s-metrics": {
        "task": "cloud.kubernetes_engine.tasks.metrics.collect_pod_metrics",
        "schedule": crontab(minute="*/5"),
    },

    # Autopilot brain
    "autopilot-loop": {
        "task": "ai_engine.autopilot.tasks.autopilot_loop",
        "schedule": crontab(minute="*/15"),
    },

    # Health verification
    "verify-health": {
        "task": "monitoring.tasks.verify_system_health",
        "schedule": crontab(minute="*/5"),
    },

    # Billing invoice generation
    "generate-invoices": {
        "task": "billing.tasks.invoicing.generate_all_invoices",
        "schedule": crontab(hour=1, minute=0),
    },

    # Train AI models
    "train-ai-models": {
        "task": "ai_engine.training.tasks.train_models",
        "schedule": crontab(hour=3, minute=0),
    },
    # Manual trigger for autopilot (can be called from API or admin)
    "run-autopilot-manual-trigger": {
        "task": "control_plane.tasks.run_autopilot_for_org",
        "schedule": crontab(minute="*/30"),
        "args": (),
    },

    "collect-cloud-inventory": {
        "task": "cloud.tasks.collect_inventory.collect_all_cloud_resources",
        "schedule": crontab(minute="*/10"),
    },
    
    "run-optimizer-every-10-minutes": {
        "task": "actions.tasks.run_optimizer_scan",
        "schedule": 600,
    },

}