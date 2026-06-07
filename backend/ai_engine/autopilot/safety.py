# ai_engine/autopilot/safety.py

from accounts.models import AutopilotPolicy
from django.utils import timezone
from actions.models import ActionExecution
from django.conf import settings

def kill_switch_enabled(organization=None) -> bool:
    """
    Global or organization-level kill switch.
    """

    # Global platform kill switch
    if getattr(settings, "AUTOPILOT_GLOBAL_KILL_SWITCH", False):
        return True

    qs = AutopilotPolicy.objects.all()

    if organization:
        qs = qs.filter(organization=organization)

    return qs.filter(enable_kill_switch=True).exists()




def blast_radius_exceeded(organization, max_actions: int) -> bool:
    """
    Prevent too many actions in a short window.
    """
    window_start = timezone.now() - timezone.timedelta(hours=24)

    executed_recently = ActionExecution.objects.filter(
        optimization__cloud_account__organization=organization,
        executed_at__gte=window_start,
        status="success",
    ).count()

    return executed_recently >= max_actions


def can_act(organization) -> bool:
    policy = AutopilotPolicy.objects.filter(
        organization=organization
    ).first()

    if not policy:
        return False
    
    if policy.enable_kill_switch:
        return False

    if blast_radius_exceeded(
        organization=organization,
        max_actions=policy.max_resources_per_day,
    ):
        return False

    return True
