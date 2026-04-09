# ai_engine/utilization.py

from django.db.models import Avg
from datetime import timedelta
from django.utils.timezone import now


def utilization_profile(resource, days=14):
    since = now() - timedelta(days=days)

    metrics = resource.metrics.filter(timestamp__gte=since)

    return {
        "cpu_avg": metrics.filter(metric_name="cpu_avg").aggregate(avg=Avg("value"))["avg"],
        "cpu_max": metrics.filter(metric_name="cpu_max").aggregate(avg=Avg("value"))["avg"],
        "memory_avg": metrics.filter(metric_name="memory_avg").aggregate(avg=Avg("value"))["avg"],
        "network_avg": metrics.filter(metric_name="network_avg").aggregate(avg=Avg("value"))["avg"],
    }