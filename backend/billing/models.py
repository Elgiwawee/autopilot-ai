# billing/models.py

import uuid
from django.db import models
from accounts.models import Organization
from django.utils import timezone


class CostRecord(models.Model):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=128)
    cost_usd = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)



def attribute_cost(resource):
    return resource.tags.get("team", "unknown")


class SavingsRecord(models.Model):
    action_id = models.CharField(max_length=128)
    before_cost = models.FloatField()
    after_cost = models.FloatField()
    savings = models.FloatField()


class CostSnapshot(models.Model):
    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)

    provider = models.CharField(max_length=20)  # AWS | GCP | AZURE
    service = models.CharField(max_length=50)   # EC2, EBS, EKS, etc
    resource_id = models.CharField(max_length=255, null=True)

    region = models.CharField(max_length=50)
    date = models.DateField()

    cost = models.DecimalField(max_digits=14, decimal_places=6)
    usage_quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        default=0,
    )
    currency = models.CharField(max_length=10, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "cloud_account",
            "service",
            "region",
            "date",
        )



class SavingsAttribution(models.Model):
    execution = models.OneToOneField(
        "actions.ActionExecution",
        on_delete=models.CASCADE,
        related_name="attribution",
    )

    resource_id = models.CharField(max_length=255)

    baseline_cost = models.DecimalField(max_digits=14, decimal_places=6)
    actual_cost = models.DecimalField(max_digits=14, decimal_places=6)

    gross_savings = models.DecimalField(max_digits=14, decimal_places=6)
    net_savings = models.DecimalField(max_digits=14, decimal_places=6)

    confidence = models.FloatField()
    explanation = models.TextField()

    calculated_at = models.DateTimeField(auto_now_add=True)



class SavingsLedger(models.Model):
    cloud_account = models.ForeignKey("cloud.CloudAccount", on_delete=models.CASCADE)
    attribution = models.ForeignKey("SavingsAttribution", on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10)

    period_start = models.DateField()
    period_end = models.DateField()

    checksum = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


class SavingsEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    cloud = models.CharField(max_length=20)
    resource_id = models.CharField(max_length=128)

    baseline_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2)

    action_id = models.CharField(max_length=64)
    confidence = models.FloatField()

    occurred_at = models.DateTimeField(auto_now_add=True)

    is_billable = models.BooleanField(default=True)
    region = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )


class BaselineSnapshot(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    cloud = models.CharField(max_length=20)

    baseline_cost = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(
        choices=[
            ("ROLLING_30", "Rolling 30 days"),
            ("LAST_MONTH", "Last month"),
        ],
        max_length=20,
    )

    computed_at = models.DateTimeField(auto_now_add=True)



class RevenueShare(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="revenue_shares"
    )

    savings_event = models.OneToOneField(
        SavingsEvent,
        on_delete=models.CASCADE,
        related_name="revenue_share"
    )

    pct = models.FloatField(default=20.0)  # platform cut %
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)

    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "savings_event")




class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE
    )

    period = models.CharField(max_length=7)  # YYYY-MM

    total_savings = models.DecimalField(
        max_digits=12, decimal_places=2
    )
    platform_fee = models.DecimalField(
        max_digits=12, decimal_places=2
    )

    currency = models.CharField(max_length=10, default="USD")

    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("issued", "Issued"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
        ],
        default="draft",
    )

    issued_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "period")


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="items", on_delete=models.CASCADE
    )

    savings_ledger = models.OneToOneField(
        SavingsLedger, on_delete=models.CASCADE
    )

    gross_savings = models.DecimalField(
        max_digits=12, decimal_places=2
    )
    platform_fee = models.DecimalField(
        max_digits=12, decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE
    )

    provider = models.CharField(
        max_length=20,
        choices=[
            ("PAYPAL", "PAYPAL"),
            ("STRIPE", "STRIPE"),
            ("MANUAL", "MANUAL"),
        ],
    )

    provider_reference = models.CharField(
        max_length=255, null=True, blank=True
    )

    amount = models.DecimalField(
        max_digits=12, decimal_places=2
    )

    currency = models.CharField(max_length=10, default="USD")

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "PENDING"),
            ("PAID", "PAID"),
            ("FAILED", "FAILED"),
        ],
        default="PENDING",
    )

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
