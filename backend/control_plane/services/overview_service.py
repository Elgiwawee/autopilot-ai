# control_plane/services/overview_service.py

from dataclasses import dataclass
from typing import Optional
from actions.models import OptimizationPlan
from accounts.services.autopilot_service import AutopilotService
from ai_engine.services.ai_service import AIService
from billing.services.savings_service import SavingsService
from billing.services.trends_service import TrendService
from monitoring.services.gpu_service import GPUService
from actions.services.action_service import ActionService


# -------------------------------------------------------
# Response Contract
# -------------------------------------------------------

@dataclass
class OverviewFilters:
    organization: object
    cloud: Optional[str] = None
    region: Optional[str] = None


class OverviewService:
    """
    High-level orchestration service.
    This layer should NOT query models directly.
    It only coordinates domain services.
    """

    @classmethod
    def build(cls, filters: OverviewFilters):

        organization = filters.organization
        cloud = filters.cloud
        region = filters.region

        # ----------------------------
        # Core Domain Calls
        # ----------------------------

        ai_status = AIService.status(
            organization=organization,
            cloud=cloud,
            region=region,
        )


        savings = SavingsService.summary(
            organization=organization,
            cloud=cloud,
            region=region,
        )

        gpu_count = GPUService.count(
            organization=organization,
            cloud=cloud,
            region=region,
        )

        actions = ActionService.recent(
            organization=organization,
            cloud=cloud,
            region=region,
            limit=5,
        )

        cost_trend = TrendService.cost_trend(
            organization=organization,
            cloud=cloud,
            region=region,
            days=7,
        )

        autopilot = AutopilotService.get_status(
            organization=organization
        )

        active = OptimizationPlan.objects.filter(
            cloud_account__organization=organization,
            status="PLANNED",
        ).count()

        # ----------------------------
        # Unified Response
        # ----------------------------

        return {
            "autopilot": autopilot,
            "ai_status": ai_status.as_dict(),
            "kpis": {
                "monthly_savings": savings["current_month"]["savings"],
                "lifetime_savings": savings["lifetime"]["total_saved"],
                "gpu_count": gpu_count,
                "active_optimizations": active,
            },
            "cost_trend": cost_trend,
            "recent_actions": actions[:5],
        }