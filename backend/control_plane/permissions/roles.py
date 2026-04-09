from rest_framework.permissions import BasePermission
from accounts.models import OrganizationMember


class IsOrgAdminOrOwner(BasePermission):

    def has_permission(self, request, view):
        org = getattr(request, "organization", None)

        if not org:
            return False

        member = OrganizationMember.objects.filter(
            organization=org,
            user=request.user
        ).first()

        if not member:
            return False

        return member.role in ["OWNER", "ADMIN"]