# audit/models.py

import uuid
from django.db import models
from accounts.models import Organization

class AuditEvent(models.Model):
    event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    cloud_account = models.ForeignKey(
        "cloud.CloudAccount", on_delete=models.CASCADE
    )

    actor = models.CharField(max_length=50)
    # SYSTEM | USER | SCHEDULE | ROLLBACK_ENGINE

    event_type = models.CharField(max_length=50)
    # DECISION_MADE | ACTION_SIMULATED | ACTION_EXECUTED | ACTION_VERIFIED | ROLLBACK_TRIGGERED | EXECUTION_FAILED

    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=255)

    before_state = models.JSONField()
    after_state = models.JSONField(null=True, blank=True)

    metadata = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    checksum = models.CharField(max_length=128, editable=False)

    class Meta:
        ordering = ["created_at"]


    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError("AuditEvent is immutable and cannot be modified")
        super().save(*args, **kwargs)



class AuditLog(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )

    actor = models.CharField(max_length=100)

    action = models.CharField(max_length=100)

    resource_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    status = models.CharField(max_length=30)

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]