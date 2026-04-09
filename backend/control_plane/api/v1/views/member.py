from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import OrganizationMember
from control_plane.permissions.member import IsOrganizationMember
from control_plane.permissions.roles import IsOrgAdminOrOwner

User = get_user_model()


class AddMemberView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role", "VIEWER")

        if not email:
            return Response(
                {"error": "Email required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ check if user exists
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not found. Send invite instead."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ prevent duplicate membership
        exists = OrganizationMember.objects.filter(
            organization=request.organization,
            user=user
        ).exists()

        if exists:
            return Response(
                {"error": "User already a member"},
                status=status.HTTP_400_BAD_REQUEST
            )

        OrganizationMember.objects.create(
            organization=request.organization,
            user=user,
            role=role
        )

        return Response({
            "message": "Member added successfully"
        })
    

class ListMembersView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        members = OrganizationMember.objects.filter(
            organization=request.organization
        ).select_related("user")

        return Response([
            {
                "email": m.user.email,
                "role": m.role,
                "joined_at": m.joined_at,
            }
            for m in members
        ])
    

class RemoveMemberView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def delete(self, request):
        email = request.data.get("email")

        member = OrganizationMember.objects.filter(
            organization=request.organization,
            user__email=email
        ).first()

        if not member:
            return Response({"error": "Member not found"}, status=404)

        # ❌ prevent removing OWNER
        if member.role == "OWNER":
            return Response(
                {"error": "Cannot remove owner"},
                status=400
            )

        member.delete()

        return Response({"message": "Member removed"})


class UpdateMemberRoleView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def patch(self, request):
        email = request.data.get("email")
        role = request.data.get("role")

        member = OrganizationMember.objects.filter(
            organization=request.organization,
            user__email=email
        ).first()

        if not member:
            return Response({"error": "Member not found"}, status=404)

        if member.role == "OWNER":
            return Response(
                {"error": "Cannot change owner role"},
                status=400
            )

        member.role = role
        member.save()

        return Response({"message": "Role updated"})