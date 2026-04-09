# ai_engine/idle_detection.py

from django.db.models import Avg
from cloud.models import CloudResource


def detect_idle_ec2_instances():
    resources = CloudResource.objects.filter(
        resource_type="vm",
        state="running",
    )

    idle_resources = []

    for resource in resources:
        avg_cpu = resource.metrics.filter(
            metric_name="cpu_avg"
        ).aggregate(avg=Avg("value"))["avg"]

        if avg_cpu is not None and avg_cpu < 5:
            idle_resources.append(resource)

    return idle_resources