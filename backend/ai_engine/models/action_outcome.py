from django.db import models

class ActionOutcome(models.Model):
    """
    Dataset used to train the learning models.
    Each row represents the outcome of an executed action.
    """

    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="action_outcomes"
    )

    cloud_account = models.ForeignKey(
        "cloud.CloudAccount",
        on_delete=models.CASCADE,
        related_name="action_outcomes"
    )

    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=255)

    action_type = models.CharField(max_length=50)

    before_state = models.JSONField()
    after_state = models.JSONField(null=True, blank=True)

    estimated_savings = models.FloatField(default=0)

    success = models.BooleanField(default=False)

    execution_time_seconds = models.FloatField(null=True, blank=True)

    failure_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["resource_type"]),
            models.Index(fields=["action_type"]),
        ]