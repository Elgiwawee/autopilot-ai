# control_plane/services/autopilot_guard.py

from django.db import transaction

from accounts.models import (
    GlobalSafety,
    AutopilotSettings,
)

from accounts.exceptions import (
    AutopilotDisabledError,
    AutopilotRiskExceededError,
    AutopilotModeError,
    AutopilotConfigurationError,
)


class AutopilotGuard:

    SAFE_BLOCKED_ACTIONS = [
        "DELETE",
        "TERMINATE",
        "DESTROY",
    ]

    @staticmethod
    @transaction.atomic
    def validate_global_access(organization):

        safety, _ = GlobalSafety.objects.select_for_update().get_or_create(
            organization=organization
        )

        if not safety.autopilot_enabled:
            raise AutopilotDisabledError(
                "Autopilot disabled globally"
            )

        return safety

    @staticmethod
    def validate_account_access(
        cloud_account,
        risk_score=None,
        action=None,
    ):

        # ---------------------------------------------------
        # GLOBAL VALIDATION
        # ---------------------------------------------------

        AutopilotGuard.validate_global_access(
            cloud_account.organization
        )

        # ---------------------------------------------------
        # SETTINGS VALIDATION
        # ---------------------------------------------------

        settings = AutopilotSettings.objects.filter(
            cloud_account=cloud_account
        ).first()

        if not settings:
            raise AutopilotConfigurationError(
                "Autopilot settings missing"
            )

        # ---------------------------------------------------
        # MODE VALIDATION
        # ---------------------------------------------------

        if settings.mode == "OFF":
            raise AutopilotModeError(
                "Autopilot OFF for account"
            )

        if settings.mode == "RECOMMEND":
            raise AutopilotModeError(
                "Recommendation-only mode"
            )

        # ---------------------------------------------------
        # RISK VALIDATION
        # ---------------------------------------------------

        if risk_score is not None:

            if risk_score > settings.max_risk_allowed:
                raise AutopilotRiskExceededError(
                    f"Risk score {risk_score} exceeds "
                    f"allowed threshold "
                    f"{settings.max_risk_allowed}"
                )

        # ---------------------------------------------------
        # SAFE MODE RESTRICTIONS
        # ---------------------------------------------------

        if (
            settings.mode == "AUTO_SAFE"
            and action in AutopilotGuard.SAFE_BLOCKED_ACTIONS
        ):
            raise AutopilotModeError(
                f"{action} blocked in AUTO_SAFE mode"
            )

        return settings