# control_plane/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication


class OrganizationJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        result = super().authenticate(request)

        if not result:
            return None

        user, token = result

        # Only authenticate user
        return (user, token)