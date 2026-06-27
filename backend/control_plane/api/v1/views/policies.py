# control_plane/api/v1/views/policy.py

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from control_plane.permissions.member import IsOrganizationMember
from control_plane.serializers.policy import AutopilotPolicySerializer
from control_plane.services.policy_service import PolicyService


class AutopilotPolicyView(APIView):

    permission_classes = (
        IsAuthenticated,
        IsOrganizationMember,
    )

    def get(self, request):

        policy = PolicyService.get_policy(request.user)

        serializer = AutopilotPolicySerializer(policy)

        return Response(serializer.data)

    def patch(self, request):

        policy = PolicyService.get_policy(request.user)

        serializer = AutopilotPolicySerializer(
            policy,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        updated = PolicyService.update_policy(
            request.user,
            serializer.validated_data,
        )

        return Response(
            AutopilotPolicySerializer(updated).data
        )