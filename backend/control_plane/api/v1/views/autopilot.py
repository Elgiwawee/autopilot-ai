# control_plane/api/v1/views/autopilot.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import assert_autopilot_enabled
from control_plane.tasks import run_autopilot_for_org
from control_plane.permissions.member import IsOrganizationMember
from accounts.models import (
    AutopilotSettings,
)
from cloud.models import CloudAccount

from accounts.services.autopilot_service import (
    AutopilotService
)

class AutopilotStatusView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOrganizationMember,
    ]

    def get(self, request):

        status = AutopilotService.get_status(
            request.organization
        )

        return Response(status)

class AutopilotModeView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        org = request.organization

        account_id = request.data.get("cloud_account_id")
        mode = request.data.get("mode")

        if not account_id or not mode:
            return Response(
                {"detail": "cloud_account_id and mode required"},
                status=400
            )

        account = CloudAccount.objects.get(
            id=account_id,
            organization=org,
            is_active=True
        )

        settings, _ = AutopilotSettings.objects.get_or_create(
            cloud_account=account
        )

        settings.mode = mode
        settings.save()

        return Response({
            "cloud_account_id": str(account.id),
            "mode": settings.mode
        })
    


class AutopilotRunView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        org = request.organization

        # Kill switch enforcement
        try:
            assert_autopilot_enabled(org)
        except RuntimeError as e:
            return Response(
                {"detail": str(e)},
                status=403
            )

        accounts = CloudAccount.objects.filter(
            organization=org,
            is_active=True
        )

        active_autopilot_accounts = AutopilotSettings.objects.filter(
            cloud_account__in=accounts
        ).exclude(mode="OFF")

        run_autopilot_for_org(org.id)
        
        return Response({
            "status": "Autopilot execution triggered",
            "accounts_considered": active_autopilot_accounts.count()
        })
    

