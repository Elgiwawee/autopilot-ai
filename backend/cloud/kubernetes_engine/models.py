# cloud/kubernetes_engine/models.py

from django.db import models
from django.apps import apps

ExecutionPlan = apps.get_model("actions", "ExecutionPlan")


class GPUMetrics(models.Model):
    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)
    cluster_id = models.CharField(max_length=128)

    namespace = models.CharField(max_length=64)
    pod_name = models.CharField(max_length=128)

    gpu_type = models.CharField(max_length=32)  # A100, H100
    gpu_memory_requested_mb = models.IntegerField()
    gpu_memory_used_mb_p95 = models.IntegerField()
    gpu_utilization_p95 = models.FloatField()

    sample_window_hours = models.IntegerField(default=24)
    source = models.CharField(
        max_length=32,
        choices=[("dcgm", "DCGM"), ("nvidia-smi", "NVIDIA-SMI")]
    )

    collected_at = models.DateTimeField(auto_now=True)


class CanaryWindow(models.Model):
    execution_plan = models.OneToOneField(
        ExecutionPlan, on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)

    baseline_error_rate = models.FloatField()
    baseline_latency_ms = models.FloatField()

    observed_error_rate = models.FloatField(null=True)
    observed_latency_ms = models.FloatField(null=True)


class KubernetesCluster(models.Model):
    cloud_account = models.ForeignKey(
        "cloud.CloudAccount",
        on_delete=models.CASCADE,
        related_name="kubernetes_clusters",
    )

    name = models.CharField(max_length=200)

    cluster_id = models.CharField(
        max_length=128,
        unique=True,
    )

    provider = models.CharField(
        max_length=20,
        choices=[
            ("aws", "AWS"),
            ("gcp", "GCP"),
            ("azure", "Azure"),
            ("onprem", "On Prem"),
        ],
    )

    region = models.CharField(max_length=100)

    kubeconfig = models.TextField()

    version = models.CharField(
        max_length=30,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["cloud_account"]),
            models.Index(fields=["cluster_id"]),
        ]


class PodMetrics(models.Model):
    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)
    cluster = models.ForeignKey(
        KubernetesCluster,
        on_delete=models.CASCADE,
        related_name="pod_metrics",
    )

    namespace = models.CharField(max_length=64)
    workload_kind = models.CharField(max_length=32)  # Deployment, StatefulSet
    workload_name = models.CharField(max_length=128)

    pod_name = models.CharField(max_length=128)

    cpu_request_millicores = models.IntegerField()
    cpu_usage_p95_millicores = models.IntegerField()

    memory_request_mb = models.IntegerField()
    memory_usage_p95_mb = models.IntegerField()

    sample_window_hours = models.IntegerField(default=24)
    collected_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["cluster", "namespace", "workload_name"]),
        ]


