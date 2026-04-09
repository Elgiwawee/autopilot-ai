# accounts/services/autopilot_service.py

from accounts.models import GlobalSafety, AutopilotSettings
from cloud.models import CloudAccount


class AutopilotService:

    @staticmethod
    def get_effective_status(organization, cloud=None):

        # ✅ GLOBAL SAFETY
        safety, _ = GlobalSafety.objects.get_or_create(
            organization=organization
        )

        if not safety.autopilot_enabled:
            return {
                "autopilot_enabled": False,
                "mode": "OFF",
                "max_risk_allowed": None,
                "effective_status": "DISABLED",
                "active_accounts": 0,
            }

        # ✅ GET CLOUD ACCOUNTS
        accounts = CloudAccount.objects.filter(
            organization=organization,
            is_active=True
        )

        if cloud:
            accounts = accounts.filter(provider__slug=cloud)

        # ✅ GET ALL SETTINGS (NOT ONE!)
        settings = AutopilotSettings.objects.filter(
            cloud_account__in=accounts
        )

        # ✅ COUNT ACTIVE ACCOUNTS
        active_accounts = settings.exclude(mode="OFF").count()

        # ✅ DETERMINE STATUS
        effective_status = (
            "ACTIVE" if active_accounts > 0 else "PAUSED"
        )

        # Optional: pick one mode (for UI display)
        mode = settings.first().mode if settings.exists() else "OFF"
        max_risk = (
            settings.first().max_risk_allowed
            if settings.exists()
            else None
        )

        return {
            "autopilot_enabled": True,
            "mode": mode,
            "max_risk_allowed": max_risk,
            "effective_status": effective_status,
            "active_accounts": active_accounts,
        }