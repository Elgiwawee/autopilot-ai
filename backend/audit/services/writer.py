# audit/services/writer.py

from audit.models import AuditLog


def write_audit_log(
    *,
    organization,
    actor,
    action,
    resource_id=None,
    status="SUCCESS",
    metadata=None,
):
    """
    Centralized audit writer.

    Every execution should create logs through this function.
    """

    return AuditLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        resource_id=resource_id,
        status=status,
        metadata=metadata or {},
    )