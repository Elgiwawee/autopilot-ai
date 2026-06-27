# control_plane/services/policy_service.py

from django.utils import timezone

from accounts.models import AutopilotPolicy


class PolicyService:

    @staticmethod
    def get_policy(user):
        organization = user.org_memberships.first().organization

        policy, _ = AutopilotPolicy.objects.get_or_create(
            organization=organization
        )

        return policy

    @staticmethod
    def update_policy(user, data):
        organization = user.org_memberships.first().organization

        policy, _ = AutopilotPolicy.objects.get_or_create(
            organization=organization
        )

        editable_fields = [

            # Optimization

            "mode",

            "allow_stop",
            "allow_resize",
            "allow_delete",

            # Financial

            "max_monthly_savings_pct",
            "max_monthly_cost_change_pct",

            # Safety

            "require_approval",
            "enable_kill_switch",

            # Blast radius

            "max_resources_per_day",
            "max_actions_per_hour",

            # Scheduling

            "maintenance_window_start",
            "maintenance_window_end",

            # Protection

            "protected_tags",

            # Notifications

            "notify_on_execution",
            "notify_on_failure",
        ]

        for field in editable_fields:

            if field in data:
                setattr(policy, field, data[field])

        policy.updated_at = timezone.now()
        policy.updated_by = user

        policy.save()

        return policy