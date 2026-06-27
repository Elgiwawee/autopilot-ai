# control_plane/serializers/policy.py

from rest_framework import serializers

from accounts.models import AutopilotPolicy


class AutopilotPolicySerializer(serializers.ModelSerializer):
    """
    Organization Autopilot Policy Serializer.
    """

    class Meta:
        model = AutopilotPolicy
        fields = "__all__"

        read_only_fields = (
            "id",
            "organization",
            "created_at",
            "updated_at",
            "updated_by",
        )

    def validate_max_monthly_savings_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Monthly savings limit must be between 0 and 100."
            )
        return value

    def validate_max_resources_per_day(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Must allow at least one resource per day."
            )
        return value

    def validate_max_actions_per_hour(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Must allow at least one action per hour."
            )
        return value

    def validate_max_monthly_cost_change_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Maximum monthly cost change must be between 0 and 100."
            )
        return value