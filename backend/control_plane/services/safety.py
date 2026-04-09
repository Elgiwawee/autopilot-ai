# control_plane/services/safety.py

from accounts.models import AutopilotSettings, GlobalSafety


def assert_autopilot_allowed(cloud_account, risk_score, action):

    # ✅ FIXED: Organization-aware safety
    global_safety, _ = GlobalSafety.objects.get_or_create(
        organization=cloud_account.organization
    )

    if not global_safety.autopilot_enabled:
        raise RuntimeError("Autopilot globally disabled")

    settings = AutopilotSettings.objects.filter(
        cloud_account=cloud_account
    ).first()

    if not settings:
        raise RuntimeError("Autopilot settings not configured")

    if settings.mode == "OFF":
        raise RuntimeError("Autopilot is OFF")

    if settings.mode == "RECOMMEND":
        raise RuntimeError("Autopilot in recommendation-only mode")

    if risk_score > settings.max_risk_allowed:
        raise RuntimeError("Risk exceeds allowed threshold")

    if settings.mode == "AUTO_SAFE":
        if action in ["DELETE", "TERMINATE"]:
            raise RuntimeError(
                "Destructive actions blocked in AUTO_SAFE mode"
            )
    # AUTO_AGGRESSIVE allows everything within risk threshold
