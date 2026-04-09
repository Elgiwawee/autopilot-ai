from django.db import models
from cloud.models import CloudAccount


class ResourceUsage(models.Model):
    cloud_account = models.ForeignKey(
        CloudAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resource_usages"
    )
    resource_id = models.CharField(max_length=255)
    service = models.CharField(max_length=50)  # EC2 / EKS
    date = models.DateField()

    cpu_hours = models.FloatField(default=0)
    memory_gb_hours = models.FloatField(default=0)

    weight = models.FloatField()  # normalized later



