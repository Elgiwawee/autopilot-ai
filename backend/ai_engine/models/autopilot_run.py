from django.db import models

class AutopilotRun(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=["organization", "started_at"]),
        ]

    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE
    )

    started_at = models.DateTimeField(auto_now_add=True)

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    plans_generated = models.IntegerField(default=0)

    plans_executed = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        default="running"
    )