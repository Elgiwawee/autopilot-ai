# control_plane/serializers/policy.py

from rest_framework import serializers
from accounts.models import AutopilotPolicy


class AutopilotPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = AutopilotPolicy
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at"]