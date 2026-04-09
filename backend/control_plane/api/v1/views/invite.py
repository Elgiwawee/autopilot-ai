from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import OrganizationInvite
from control_plane.permissions.member import IsOrganizationMember
from control_plane.permissions.roles import IsOrgAdminOrOwner
from django.contrib.auth import get_user_model
from accounts.models import OrganizationInvite, OrganizationMember
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class InviteMemberView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role", "VIEWER")

        invite = OrganizationInvite.objects.create(
            organization=request.organization,
            email=email,
            role=role,
            invited_by=request.user
        )

        invite_link = f"http://localhost:5173/accept-invite/{invite.token}"

        send_mail(
            subject="You're invited to join Autopilot AI",
            message=f"""
You have been invited to join {request.organization.name}.

Click below to accept:
{invite_link}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        existing = OrganizationInvite.objects.filter(
            organization=request.organization,
            email=email,
            accepted=False
        ).exists()

        if existing:
            return Response(
                {"error": "Invite already sent"},
                status=400
    )

        return Response({"message": "Invitation sent"})
    






class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        try:
            invite = OrganizationInvite.objects.get(token=token)
        except OrganizationInvite.DoesNotExist:
            return Response({"error": "Invalid invite"}, status=400)

        # ✅ NEW: validate invite
        if not invite.is_valid():
            return Response(
                {"error": "Invite expired or already used"},
                status=400
            )

        user = request.user

        # prevent duplicate join
        exists = OrganizationMember.objects.filter(
            organization=invite.organization,
            user=user
        ).exists()

        if exists:
            return Response({"error": "Already a member"}, status=400)

        OrganizationMember.objects.create(
            organization=invite.organization,
            user=user,
            role=invite.role
        )

        invite.accepted = True
        invite.save()

        return Response({"message": "Joined organization"})
    

class ListInvitesView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        invites = OrganizationInvite.objects.filter(
            organization=request.organization,
            accepted=False
        )

        return Response([
            {
                "email": i.email,
                "role": i.role,
                "created_at": i.created_at,
                "expires_at": i.expires_at,
            }
            for i in invites
        ])
    
class CancelInviteView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def delete(self, request):
        email = request.data.get("email")

        invite = OrganizationInvite.objects.filter(
            organization=request.organization,
            email=email,
            accepted=False
        ).first()

        if not invite:
            return Response({"error": "Invite not found"}, status=404)

        invite.delete()

        return Response({"message": "Invite cancelled"})
    


class ResendInviteView(APIView):
    permission_classes = [IsOrganizationMember, IsOrgAdminOrOwner]

    def post(self, request):
        email = request.data.get("email")

        invite = OrganizationInvite.objects.filter(
            organization=request.organization,
            email=email,
            accepted=False
        ).first()

        if not invite:
            return Response({"error": "Invite not found"}, status=404)

        invite.token = uuid.uuid4()
        invite.expires_at = timezone.now() + timedelta(days=7)
        invite.save()

        return Response({"message": "Invite resent"})