# control_plane/api/v1/views/optimizer.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from control_plane.permissions.member import IsOrganizationMember
from control_plane.services.optimizer_service import build_optimizer


class OptimizerView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization

        data = build_optimizer(organization)

        return Response(data)
