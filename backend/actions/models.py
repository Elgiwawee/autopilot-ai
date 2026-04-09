# actions/models.py

import uuid
from django.db import models
from django.conf import settings
from cloud.models import CloudAccount
from django.utils import timezone

class ActionPlan(models.Model):
    """
    A simulated, safe plan of what *would* happen.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(
        "cloud.CloudResource", on_delete=models.CASCADE
    )

    action_type = models.CharField(max_length=64)  # stop, resize, delete
    estimated_savings = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    risk_level = models.CharField(
        max_length=16, choices=(("low", "Low"), ("medium", "Medium"), ("high", "High"))
    )

    is_safe = models.BooleanField(default=True)
    explanation = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class ActionExecution(models.Model):
    """
    What actually happened (or attempted).
    """
    STATUS = (
        ("planned", "Planned"),
        ("executing", "Executing"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("rolled_back", "Rolled Back"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_plan = models.OneToOneField(
        ActionPlan, on_delete=models.CASCADE
    )

    status = models.CharField(max_length=16, choices=STATUS)
    executed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)


class ActionApproval(models.Model):
    action_plan = models.OneToOneField(
        "actions.ActionPlan",
        on_delete=models.CASCADE,
        related_name="approval",
    )

    approved = models.BooleanField(null=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_actions",
    )

    approved_at = models.DateTimeField(null=True, blank=True)



# actions/models.py

class OptimizationPlan(models.Model):
    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=50)  # EC2, EBS, RDS, EKS
    resource_id = models.CharField(max_length=255)

    action_type = models.CharField(max_length=50)
    # examples: STOP, TERMINATE, RESIZE, SCALE_DOWN

    current_state = models.JSONField()
    proposed_state = models.JSONField()

    estimated_monthly_savings = models.DecimalField(max_digits=12, decimal_places=2)

    confidence = models.FloatField()  # ML or heuristic
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PLANNED", "PLANNED"),
            ("REJECTED", "REJECTED"),
            ("APPROVED", "APPROVED"),
        ],
        default="PLANNED"
    )

class EC2IdlePlanner:
    def generate_plans(self, ec2_instance, metrics):
        if metrics.avg_cpu < 5 and metrics.network_in < 1:
            return OptimizationPlan(
                resource_type="EC2",
                resource_id=ec2_instance.id,
                action_type="STOP",
                current_state={"instance_type": ec2_instance.type},
                proposed_state={"state": "stopped"},
                estimated_monthly_savings=ec2_instance.monthly_cost,
                confidence=0.82,
            )

class Decision(models.Model):
    plan = models.OneToOneField(OptimizationPlan, on_delete=models.CASCADE)

    risk_score = models.FloatField()
    risk_level = models.CharField(max_length=20)

    auto_execute_allowed = models.BooleanField()
    reason = models.TextField()

    decided_at = models.DateTimeField(auto_now_add=True)



class ExecutionRecord(models.Model):
    decision = models.OneToOneField(
        "actions.Decision",
        on_delete=models.CASCADE
    )

    STATE_CHOICES = [
        ("DETECTED", "Detected"),
        ("PLANNED", "Planned"),
        ("SIMULATED", "Simulated"),
        ("APPROVED", "Approved"),
        ("EXECUTING", "Executing"),
        ("VERIFIED", "Verified"),
        ("COMPLETED", "Completed"),
        ("ROLLED_BACK", "Rolled Back"),
        ("FAILED", "Failed"),
    ]

    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="DETECTED",
    )

    before_state = models.JSONField()
    after_state = models.JSONField(null=True, blank=True)

    rollback_payload = models.JSONField()
    error = models.TextField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)



class ExecutionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)
    cluster_id = models.CharField(max_length=128)

    target_type = models.CharField(max_length=32)  # Deployment, StatefulSet
    namespace = models.CharField(max_length=64)
    target_name = models.CharField(max_length=128)

    action = models.CharField(max_length=64)  # resize_pod, scale_down, etc
    parameters = models.JSONField()

    risk_score = models.FloatField()
    confidence = models.FloatField()

    status = models.CharField(
        max_length=32,
        choices=[
            ("planned", "Planned"),
            ("canary", "Canary"),
            ("committed", "Committed"),
            ("rolled_back", "Rolled Back"),
            ("failed", "Failed"),
        ],
        default="planned",
    )

    created_at = models.DateTimeField(auto_now_add=True)



class Policy(models.Model):
    cloud_account = models.ForeignKey(
        CloudAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies"
    )

    name = models.CharField(
        max_length=128,
        default="Unnamed Policy"
    )

    description = models.TextField(blank=True)

    scope = models.JSONField(
        default=dict,
        blank=True
    )

    rules = models.JSONField(
        default=dict,
        blank=True
    )

    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )



class PolicyDecision(models.Model):
    execution_plan = models.ForeignKey(ExecutionPlan, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    decision = models.CharField(max_length=16)  # allow / deny
    reason = models.TextField()
    decided_at = models.DateTimeField(auto_now_add=True)
