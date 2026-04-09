from django.db import models


class OptimizationOpportunity(models.Model):
    """
    Detected optimization opportunity before turning into an execution plan.
    """

    cloud_account_id = models.UUIDField()

    resource_type = models.CharField(max_length=100)

    resource_id = models.CharField(max_length=200)

    action_type = models.CharField(max_length=100)

    cpu_utilization = models.FloatField(null=True, blank=True)

    memory_utilization = models.FloatField(null=True, blank=True)

    estimated_savings = models.FloatField(default=0)

    detected_at = models.DateTimeField(auto_now_add=True)

    converted_to_plan = models.BooleanField(default=False)