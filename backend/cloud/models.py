# cloud/models.py

import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from accounts.models import Organization


class CloudProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(
        max_length=32,
        unique=True,
        choices=(
            ("aws", "AWS"),
            ("azure", "Azure"),
            ("gcp", "GCP"),
            ("kubernetes", "Kubernetes"),
        ),
    )
    
    display_name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name



class CloudAccount(models.Model):

    MODE_CHOICES = (
        ("observe", "Observe"),
        ("recommend", "Recommend"),
        ("autopilot", "Autopilot"),
    )

    STATUS_PENDING = "pending"
    STATUS_CONNECTED = "connected"
    STATUS_FAILED = "failed"
    STATUS_DISABLED = "disabled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONNECTED, "Connected"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DISABLED, "Disabled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="cloud_accounts",
    )

    provider = models.ForeignKey(
        CloudProvider,
        on_delete=models.CASCADE
    )

    account_identifier = models.CharField(max_length=128)

    role_arn = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    mode = models.CharField(
        max_length=16,
        choices=MODE_CHOICES,
        default="observe"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    is_active = models.BooleanField(default=True)

    last_checked_at = models.DateTimeField(
        blank=True,
        null=True
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.display_name} - {self.account_identifier}"
    
class CloudResource(models.Model):
    RESOURCE_TYPES = (
        ("vm", "Virtual Machine"),
        ("db", "Database"),
        ("bucket", "Object Storage"),
        ("volume", "Block Storage"),
        ("gpu", "GPU"),
        ("pod", "Kubernetes Pod"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cloud_account = models.ForeignKey(
        CloudAccount, on_delete=models.CASCADE, related_name="resources"
    )
    provider = models.ForeignKey(CloudProvider, on_delete=models.CASCADE)

    resource_type = models.CharField(max_length=32, choices=RESOURCE_TYPES)
    external_id = models.CharField(max_length=128)
    region = models.CharField(max_length=64)

    state = models.CharField(max_length=32)
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cloud_account", "external_id")

    def __str__(self):
        return f"{self.resource_type} - {self.external_id}"


class K8sCluster(models.Model):
    organization = models.ForeignKey(
    "accounts.Organization",
    on_delete=models.CASCADE,
    related_name="k8s_clusters"
)
    name = models.CharField(max_length=128)
    provider = models.CharField(max_length=20)  # eks, gke, aks
    region = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)


class K8sWorkload(models.Model):
    cluster = models.ForeignKey(K8sCluster, on_delete=models.CASCADE)
    namespace = models.CharField(max_length=64)
    kind = models.CharField(max_length=20)  # deployment, statefulset
    name = models.CharField(max_length=128)

    cpu_request = models.FloatField()   # cores
    cpu_limit = models.FloatField(null=True, blank=True)
    mem_request = models.IntegerField() # MiB
    mem_limit = models.IntegerField(null=True, blank=True)

    replicas = models.IntegerField()
    last_seen = models.DateTimeField(auto_now=True)


class K8sNodeGroup(models.Model):
    cluster = models.ForeignKey("cloud.K8sCluster", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    instance_type = models.CharField(max_length=64)
    min_nodes = models.IntegerField()
    max_nodes = models.IntegerField()
    desired_nodes = models.IntegerField()

    pricing_model = models.CharField(
        max_length=20,
        choices=[("on_demand", "On-Demand"), ("spot", "Spot")]
    )

    cpu_capacity = models.FloatField()
    mem_capacity = models.IntegerField()  # MiB


class GPUWorkload(models.Model):
    workload = models.OneToOneField("cloud.K8sWorkload", on_delete=models.CASCADE)
    gpu_type = models.CharField(max_length=32)  # A100, T4, L4
    gpu_count = models.IntegerField()
    utilization_avg = models.FloatField()
    utilization_p95 = models.FloatField()


def gpu_underutilized(p95_util):
    return p95_util < 40


def recommend_gpu(gpu):
    if gpu.utilization_p95 < 30:
        return "T4"
    return gpu.gpu_type


class InstancePricing(models.Model):
    provider = models.ForeignKey(
        "CloudProvider",
        on_delete=models.CASCADE
    )

    instance_type = models.CharField(
        max_length=64
    )

    region = models.CharField(
        max_length=64
    )

    operating_system = models.CharField(
        max_length=32,
        default="linux"
    )

    pricing_model = models.CharField(
        max_length=20,
        choices=[
            ("on_demand", "On-Demand"),
            ("spot", "Spot"),
        ],
        default="on_demand"
    )

    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=6
    )

    # NEW

    source = models.CharField(
        max_length=50,
        default="api"
    )

    last_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = (
            "provider",
            "instance_type",
            "region",
            "operating_system",
            "pricing_model",
        )


class GPUMetrics(models.Model):
    cloud_account = models.ForeignKey(CloudAccount, on_delete=models.CASCADE)
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
        "actions.ExecutionPlan", on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)

    baseline_error_rate = models.FloatField()
    baseline_latency_ms = models.FloatField()

    observed_error_rate = models.FloatField(null=True)
    observed_latency_ms = models.FloatField(null=True)


class KubernetesCluster(models.Model):
    cloud_account = models.ForeignKey(
        CloudAccount,
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
    cloud_account = models.ForeignKey(CloudAccount, on_delete=models.CASCADE)
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


