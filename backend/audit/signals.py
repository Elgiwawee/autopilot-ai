# audit/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from audit.models import AuditEvent
from audit.utils import generate_checksum

@receiver(pre_save, sender=AuditEvent)
def set_checksum(sender, instance, **kwargs):
    if not instance.checksum:
        instance.checksum = generate_checksum(instance)
