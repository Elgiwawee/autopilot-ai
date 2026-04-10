# control_plane/views/me.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


@method_decorator(never_cache, name='dispatch')
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = request.user.org_memberships.select_related("organization")

        return Response({
            "user": {
                "email": request.user.email,
            },
            "organizations": [
                {
                    "id": m.organization.id,
                    "name": m.organization.name,
                    "role": m.role,
                    "region": m.organization.region or "us-east-1",
                }
                for m in memberships
            ]
        })