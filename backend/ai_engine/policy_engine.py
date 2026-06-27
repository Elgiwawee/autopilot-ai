from dataclasses import dataclass
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from accounts.models import AutopilotPolicy
from actions.models import ExecutionPlan
from cloud.services.cost_service import CostService


@dataclass
class PolicyResult:
    allowed: bool
    requires_approval: bool
    reason: str
    risk_level: str


class PolicyEngine:
    """
    Enterprise Policy Engine.

    Responsible only for deciding whether
    an ExecutionPlan may be executed.

    It never performs the execution itself.
    """

    @staticmethod
    def evaluate(plan: ExecutionPlan) -> PolicyResult:

        organization = plan.cloud_account.organization

        try:
            policy = organization.autopilot_policy

        except AutopilotPolicy.DoesNotExist:

            return PolicyResult(
                allowed=False,
                requires_approval=True,
                reason="No Autopilot policy configured.",
                risk_level="critical",
            )

        ##########################################################
        # Kill Switch
        ##########################################################

        if policy.enable_kill_switch:

            return PolicyResult(
                allowed=False,
                requires_approval=False,
                reason="Autopilot Kill Switch is enabled.",
                risk_level="critical",
            )

        ##########################################################
        # Action Permissions
        ##########################################################

        action = plan.action.lower()

        if action == "stop" and not policy.allow_stop:

            return PolicyResult(
                False,
                False,
                "Stopping resources is disabled by policy.",
                "high",
            )

        if action == "resize" and not policy.allow_resize:

            return PolicyResult(
                False,
                False,
                "Resizing resources is disabled by policy.",
                "high",
            )

        if action == "delete" and not policy.allow_delete:

            return PolicyResult(
                False,
                False,
                "Deleting resources is disabled by policy.",
                "critical",
            )

        ##########################################################
        # Daily Blast Radius
        ##########################################################

        today = timezone.now().date()

        executed_today = ExecutionPlan.objects.filter(
            cloud_account__organization=organization,
            status="committed",
            created_at__date=today,
        ).count()

        if executed_today >= policy.max_resources_per_day:

            return PolicyResult(
                False,
                False,
                "Daily execution limit has been reached.",
                "medium",
            )

        ##########################################################
        # Monthly Optimization Budget
        ##########################################################

        organization_monthly_cost = CostService.get_organization_monthly_cost(
            organization
        )

        allowed_budget = (
            organization_monthly_cost
            * Decimal(str(policy.max_monthly_savings_pct))
            / Decimal("100")
        )

        start_month = timezone.now().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        optimized_this_month = (
            ExecutionPlan.objects.filter(
                cloud_account__organization=organization,
                status="committed",
                created_at__gte=start_month,
            ).aggregate(
                total=Sum("estimated_monthly_savings")
            )["total"]
            or Decimal("0")
        )

        projected_total = (
            optimized_this_month
            + plan.estimated_monthly_savings
        )

        if projected_total > allowed_budget:

            return PolicyResult(
                allowed=False,
                requires_approval=True,
                reason="Monthly optimization budget would be exceeded.",
                risk_level="medium",
            )

        ##########################################################
        # Confidence Threshold
        ##########################################################

        if (
            policy.minimum_confidence_score
            and plan.confidence < policy.minimum_confidence_score
        ):

            return PolicyResult(
                allowed=False,
                requires_approval=True,
                reason="AI confidence is below the organization's minimum threshold.",
                risk_level="medium",
            )

        ##########################################################
        # High Risk Threshold
        ##########################################################

        if (
            policy.maximum_risk_score
            and plan.risk_score > policy.maximum_risk_score
        ):

            return PolicyResult(
                allowed=False,
                requires_approval=True,
                reason="Risk score exceeds the organization's policy.",
                risk_level="high",
            )

        ##########################################################
        # Manual Approval
        ##########################################################

        if policy.require_approval:

            return PolicyResult(
                allowed=True,
                requires_approval=True,
                reason="Manual approval is required before execution.",
                risk_level="low",
            )

        ##########################################################
        # Approved
        ##########################################################

        return PolicyResult(
            allowed=True,
            requires_approval=False,
            reason="Execution approved by policy engine.",
            risk_level="low",
        )