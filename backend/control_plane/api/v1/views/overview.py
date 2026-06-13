# control_plane/api/v1/views/overview.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cloud.models import CloudAccount
from control_plane.permissions.member import IsOrganizationMember
from control_plane.services.overview_service import (
    OverviewService,
    OverviewFilters,
)


class OverviewView(APIView):
    """
    GET /api/v1/overview/
    """

    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization

        cloud_code = self._resolve_cloud_code(
            organization=organization,
            cloud_account_id=request.query_params.get("cloud_account"),
        )

        if isinstance(cloud_code, Response):
            return cloud_code  # early return if validation failed

        filters = OverviewFilters(
            organization=organization,
            cloud=cloud_code,
            region=request.query_params.get("region"),
        )

        return Response(OverviewService.build(filters))

    # ---------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------

    def _resolve_cloud_code(self, organization, cloud_account_id):
        """
        Validate cloud account and return provider slug.
        Returns Response if invalid.
        """

        if not cloud_account_id:
            return None

        cloud_account = (
            CloudAccount.objects
            .filter(
                id=cloud_account_id,
                organization=organization,
                is_active=True,
            )
            .select_related("provider")
            .first()
        )

        if not cloud_account:
            return Response(
                {"detail": "Invalid or inactive cloud account."},
                status=404,
            )

        return cloud_account.provider.code