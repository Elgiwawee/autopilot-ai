# accounts/services/autopilot_service.py

from accounts.models import (
    GlobalSafety,
    AutopilotSettings,
)

from cloud.models import CloudAccount


class AutopilotService:

    @staticmethod
    def get_status(organization):

        safety, _ = GlobalSafety.objects.get_or_create(
            organization=organization
        )

        accounts = CloudAccount.objects.filter(
            organization=organization,
            is_active=True,
        )

        settings = AutopilotSettings.objects.filter(
            cloud_account__in=accounts
        ).select_related("cloud_account")

        configured_accounts = settings.count()

        active_accounts = settings.exclude(
            mode="OFF"
        ).count()

        recommendation_accounts = settings.filter(
            mode="RECOMMEND"
        ).count()

        safe_accounts = settings.filter(
            mode="AUTO_SAFE"
        ).count()

        aggressive_accounts = settings.filter(
            mode="AUTO_AGGRESSIVE"
        ).count()

        # -----------------------------------------
        # EFFECTIVE STATUS
        # -----------------------------------------

        if not safety.autopilot_enabled:

            effective_status = "DISABLED"

        elif active_accounts == 0:

            effective_status = "PAUSED"

        else:

            effective_status = "ACTIVE"

        return {
            "autopilot_enabled": safety.autopilot_enabled,
            "effective_status": effective_status,
            "total_accounts": accounts.count(),
            "configured_accounts": configured_accounts,
            "active_accounts": active_accounts,
            "recommendation_accounts": recommendation_accounts,
            "safe_accounts": safe_accounts,
            "aggressive_accounts": aggressive_accounts,
            "accounts": [
                {
                    "cloud_account_id": str(
                        s.cloud_account.id
                    ),
                    "mode": s.mode,
                    "max_risk_allowed": (
                        s.max_risk_allowed
                    ),
                }
                for s in settings
            ],
        }