# control_plane/middleware/organization.py

from accounts.models import OrganizationMember
from django.utils.deprecation import MiddlewareMixin


class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.organization = None

        if not request.user.is_authenticated:
            return

        membership = (
            OrganizationMember.objects
            .select_related("organization")
            .filter(user=request.user)
            .first()
        )

        if membership:
            request.organization = membership.organization
