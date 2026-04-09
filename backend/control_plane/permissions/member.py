# control_plane/permissions/member.py

from rest_framework.permissions import BasePermission
from accounts.models import Organization, OrganizationMember


class IsOrganizationMember(BasePermission):
    """
    Ensures the user belongs to the requested organization.
    Expects X-Organization-ID header.
    Attaches organization to request.organization.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        org_id = request.headers.get("X-Organization-ID")

        if not org_id:
            return False

        try:
            organization = Organization.objects.get(id=org_id, is_active=True)
        except Organization.DoesNotExist:
            return False

        is_member = OrganizationMember.objects.filter(
            organization=organization,
            user=request.user
        ).exists()

        if not is_member:
            return False

        # Attach to request for use in views
        request.organization = organization
        return True