# control_plane/api/v1/views/savings.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_plane.permissions.member import IsOrganizationMember
from billing.services.savings_service import SavingsService
from billing.services.trends_service import TrendService
from actions.services.optimizer import list_optimizations


class SavingsOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        cloud = request.query_params.get("cloud")
        region = request.query_params.get("region")

        summary = SavingsService.summary(
            organization=organization,
            cloud=cloud,
            region=region,
        )

        return Response(summary)


class SavingsTrendView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        cloud = request.query_params.get("cloud")
        region = request.query_params.get("region")

        trend = TrendService.cost_trend(
            organization=organization,
            cloud=cloud,
            region=region,
            days=7,
        )

        return Response(trend)


class SavingsRecommendationView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        cloud = request.query_params.get("cloud")

        recommendations = list_optimizations(
            organization=organization,
            cloud=cloud,
        )

        return Response({
            "count": len(recommendations),
            "recommendations": recommendations,
        })