# control_plane/services/policy_service.py

from accounts.models import AutopilotPolicy


class PolicyService:

    @staticmethod
    def get_policy(user):
        org = user.org_memberships.first().organization

        policy, _ = AutopilotPolicy.objects.get_or_create(
            organization=org
        )

        return policy

    @staticmethod
    def update_policy(user, data):
        org = user.org_memberships.first().organization

        policy, _ = AutopilotPolicy.objects.get_or_create(
            organization=org
        )

        # Update fields safely
        for field in [
            "max_monthly_savings_pct",
            "allow_stop",
            "allow_resize",
            "allow_delete",
            "max_resources_per_day",
            "require_approval",
            "enable_kill_switch",
        ]:
            if field in data:
                setattr(policy, field, data[field])

        policy.save()
        return policy