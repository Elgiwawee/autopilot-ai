
# accounts/models.py

from django.utils import timezone
from datetime import timedelta
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Organization(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    region = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class AWSAccount(models.Model):
    cloud_account = models.OneToOneField(
        "cloud.CloudAccount",
        on_delete=models.CASCADE,
        related_name="aws",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="aws_accounts"
    )

    name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=20)
    role_arn = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AzureAccount(models.Model):
    cloud_account = models.OneToOneField(
        "cloud.CloudAccount",
        on_delete=models.CASCADE,
        related_name="azure",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="azure_accounts"
    )

    name = models.CharField(max_length=255)

    tenant_id = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    subscription_id = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Azure {self.subscription_id}"
    

class GCPAccount(models.Model):
    cloud_account = models.OneToOneField(
        "cloud.CloudAccount",
        on_delete=models.CASCADE,
        related_name="gcp",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="gcp_accounts"
    )

    name = models.CharField(max_length=255)

    project_id = models.CharField(max_length=255)
    service_account_json = models.JSONField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GCP {self.project_id}"


class AutopilotPolicy(models.Model):
    """
    Organization-level safety rules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.OneToOneField(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="autopilot_policy",
    )

    # Hard limits
    max_monthly_savings_pct = models.FloatField(
        default=30.0,
        help_text="Maximum % of total spend that autopilot can optimize per month"
    )

    allow_stop = models.BooleanField(default=False)
    allow_resize = models.BooleanField(default=False)
    allow_delete = models.BooleanField(default=False)

    # Blast radius
    max_resources_per_day = models.IntegerField(default=3)

    # Safety
    require_approval = models.BooleanField(default=True)
    enable_kill_switch = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Policy - {self.organization.name}"


class EBSVolume(models.Model):
    aws_account = models.ForeignKey("accounts.AWSAccount", on_delete=models.CASCADE)
    volume_id = models.CharField(max_length=32)
    volume_type = models.CharField(max_length=20)
    size_gb = models.IntegerField()
    iops = models.IntegerField(null=True, blank=True)
    throughput = models.IntegerField(null=True, blank=True)
    attached_instance_id = models.CharField(max_length=32, null=True, blank=True)
    state = models.CharField(max_length=20)
    is_encrypted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# class GlobalSettings(models.Model):
#    kill_switch = models.BooleanField(default=False)

# if settings.kill_switch:
#     return


class AutopilotSettings(models.Model):
    MODE_CHOICES = [
        ("OFF", "Off"),
        ("RECOMMEND", "Recommend Only"),
        ("AUTO_SAFE", "Auto Safe"),
        ("AUTO_AGGRESSIVE", "Auto Aggressive"),
    ]

    cloud_account = models.OneToOneField(
        "cloud.CloudAccount",
        on_delete=models.CASCADE
    )

    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default="OFF"
    )

    max_risk_allowed = models.FloatField(default=0.25)

    def __str__(self):
        return f"{self.cloud_account} - {self.mode}"


class GlobalSafety(models.Model):
    organization = models.OneToOneField(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="global_safety",
        null=True,          
        blank=True
    )
    autopilot_enabled = models.BooleanField(default=True)


def assert_autopilot_enabled(org):
    safety, _ = GlobalSafety.objects.get_or_create(
        organization=org
    )

    if not safety.autopilot_enabled:
        raise RuntimeError("Autopilot disabled by global safety switch")

class OrganizationMember(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="org_memberships"
    )

    role = models.CharField(
        choices=[
            ("OWNER", "OWNER"),
            ("ADMIN", "ADMIN"),
            ("VIEWER", "VIEWER"),
        ],
        default="OWNER"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")


def default_expiry():
    return timezone.now() + timedelta(days=7)


class OrganizationInvite(models.Model):
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="invites"
    )

    email = models.EmailField()

    role = models.CharField(
        choices=[
            ("ADMIN", "ADMIN"),
            ("VIEWER", "VIEWER"),
        ],
        default="VIEWER"
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invites"
    )

    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(default=default_expiry)

    def is_valid(self):
        return not self.accepted and timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.email} invited to {self.organization.name}"