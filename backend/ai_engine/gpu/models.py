from django.db import models


class GPUMetric(models.Model):
    """
    Historical GPU metrics used for
    ML training and optimization.
    """

    workload_id = models.CharField(
        max_length=128,
        db_index=True,
    )

    resource_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
        db_index=True,
    )

    provider = models.CharField(
        max_length=32,
        blank=True,
        default="",
    )

    region = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )

    gpu_model = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )

    utilization = models.FloatField()

    mem_used = models.IntegerField()

    mem_total = models.IntegerField()

    power_draw = models.FloatField(
        default=0,
    )

    temperature = models.FloatField(
        default=0,
    )

    timestamp = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-timestamp",
        ]

        indexes = [
            models.Index(
                fields=[
                    "workload_id",
                    "timestamp",
                ]
            ),
            models.Index(
                fields=[
                    "resource_id",
                    "timestamp",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.workload_id} "
            f"{self.utilization}%"
        )