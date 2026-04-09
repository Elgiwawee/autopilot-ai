# control_plane/api/v1/views/audit.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from control_plane.permissions.member import IsOrganizationMember
from control_plane.services.audit_service import build_audit


class AuditLogView(APIView):

    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        data = build_audit(request.organization)
        return Response(data)