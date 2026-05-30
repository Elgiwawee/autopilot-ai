# cloud/tasks/schedular.py

from celery import shared_task
from accounts.models import Organization
from cloud.tasks.collect_inventory import (
    collect_all_cloud_resources
)


@shared_task
def schedule_inventory_collection():

    organizations = Organization.objects.filter(
        is_active=True
    )

    for org in organizations:
        collect_all_cloud_resources.delay(
            str(org.id)
        )