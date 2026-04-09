# control_plane/api/v1/views/global_safety.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from control_plane.permissions.member import IsOrganizationMember
from accounts.models import GlobalSafety


class GlobalSafetyStatusView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        gs, _ = GlobalSafety.objects.get_or_create(
            organization=request.organization
        )

        return Response({
            "autopilot_enabled": bool(
                gs and gs.autopilot_enabled
            )
        })

class ToggleAutopilotView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        org = request.organization

        safety, _ = GlobalSafety.objects.get_or_create(
            organization=org
        )

        safety.autopilot_enabled = not safety.autopilot_enabled
        safety.save()

        return Response({
            "autopilot_enabled": safety.autopilot_enabled
        })