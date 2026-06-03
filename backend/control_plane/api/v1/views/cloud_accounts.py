# control-plane/api/v1/views/cloud_accounts.py

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.models import (
    AWSAccount,
    AzureAccount,
    GCPAccount,
    AutopilotSettings,
)

from cloud.models import (
    CloudAccount,
    CloudProvider,
)

from control_plane.permissions.member import IsOrganizationMember
from control_plane.tasks import discover_cloud_account


class CloudAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):

        org = request.organization

        accounts = (
            CloudAccount.objects
            .filter(
                organization=org,
                is_active=True
            )
            .select_related("provider")
            .order_by("-created_at")
        )

        results = []

        for acc in accounts:

            results.append({
                "id": str(acc.id),
                "provider": acc.provider.display_name,
                "provider_code": acc.provider.code,
                "account_identifier": acc.account_identifier,
                "mode": acc.mode,
                "status": acc.status,
                "is_active": acc.is_active,
                "error_message": acc.error_message,
                "created_at": acc.created_at,
            })

        return Response({
            "results": results
        })

    @transaction.atomic
    def post(self, request):

        org = request.organization

        provider_code = request.data.get(
            "provider_code",
            ""
        ).strip().lower()

        account_identifier = request.data.get(
            "account_identifier"
        )

        role_arn = request.data.get("role_arn")

        mode = request.data.get(
            "mode",
            "observe"
        )

        if not provider_code or not account_identifier:

            return Response(
                {
                    "detail": "Missing required fields"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        provider = get_object_or_404(
            CloudProvider,
            code=provider_code,
            is_active=True
        )

        cloud_account = CloudAccount.objects.create(
            organization=org,
            provider=provider,
            account_identifier=account_identifier,
            role_arn=role_arn,
            external_id=request.data.get("external_id"),
            mode=mode,
            status=CloudAccount.STATUS_PENDING,
            is_active=True,
        )

        try:

            # AWS
            if provider_code == "aws":

                AWSAccount.objects.create(
                    cloud_account=cloud_account,
                    organization=org,
                    name="AWS Account",
                    account_id=account_identifier,
                    role_arn=role_arn,
                    external_id=request.data.get("external_id"),
                )

            # AZURE
            elif provider_code == "azure":

                AzureAccount.objects.create(
                    cloud_account=cloud_account,
                    organization=org,
                    name="Azure Account",
                    tenant_id=request.data.get("tenant_id"),
                    client_id=request.data.get("client_id"),
                    client_secret=request.data.get("client_secret"),
                    subscription_id=request.data.get("subscription_id"),
                )

            # GCP
            elif provider_code == "gcp":

                GCPAccount.objects.create(
                    cloud_account=cloud_account,
                    organization=org,
                    name="GCP Account",
                    project_id=request.data.get("project_id"),
                    service_account_json=request.data.get(
                        "service_account_json"
                    ),
                )

            # DEFAULT AUTOPILOT SETTINGS
            AutopilotSettings.objects.create(
                cloud_account=cloud_account,
                mode="AUTO_SAFE",
                max_risk_allowed=0.25
            )

            # RUN DISCOVERY TASK
            discover_cloud_account.delay(
                str(cloud_account.id)
            )

        except Exception as e:

            raise e

        return Response(
            {
                "id": str(cloud_account.id),
                "provider": cloud_account.provider.display_name,
                "provider_code": cloud_account.provider.code,
                "account_identifier": cloud_account.account_identifier,
                "mode": cloud_account.mode,
                "status": cloud_account.status,
                "created_at": cloud_account.created_at,
            },
            status=status.HTTP_201_CREATED
        )


class CloudAccountDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsOrganizationMember
    ]

    def delete(self, request, account_id):

        org = request.organization

        cloud_account = get_object_or_404(
            CloudAccount,
            id=account_id,
            organization=org,
        )

        cloud_account.is_active = False
        cloud_account.status = CloudAccount.STATUS_DISABLED

        cloud_account.save(
            update_fields=[
                "is_active",
                "status"
            ]
        )

        return Response(
            {
                "detail": "Cloud account disabled"
            },
            status=status.HTTP_200_OK
        )