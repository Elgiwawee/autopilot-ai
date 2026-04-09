# control_plane/api/v1/views/policy.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_plane.permissions.member import IsOrganizationMember
from control_plane.services.policy_service import PolicyService
from control_plane.serializers.policy import AutopilotPolicySerializer


class AutopilotPolicyView(APIView):

    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        policy = PolicyService.get_policy(request.user)
        serializer = AutopilotPolicySerializer(policy)
        return Response(serializer.data)

    def patch(self, request):
        policy = PolicyService.update_policy(request.user, request.data)
        serializer = AutopilotPolicySerializer(policy)
        return Response(serializer.data)