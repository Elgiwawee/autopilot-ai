from django.utils import timezone

from actions.models import (
    ActionApproval,
    ExecutionPlan,
)

from ai_engine.policy_engine import (
    PolicyEngine,
)


class ApprovalEngine:
    """
    Enterprise Approval Engine.

    Responsibilities

    • evaluate policy
    • determine approval workflow
    • update ExecutionPlan status
    • create ActionApproval records

    It NEVER executes cloud actions.
    """

    @staticmethod
    def process(plan: ExecutionPlan):

        result = PolicyEngine.evaluate(plan)

        #
        # Block immediately
        #

        if not result.allowed:

            plan.status = "skipped_policy"
            plan.save(update_fields=["status"])

            return result

        #
        # Manual approval required
        #

        if result.requires_approval:

            ActionApproval.objects.update_or_create(
                action_plan_id=plan.id,
                defaults={
                    "approved": None,
                    "approved_by": None,
                    "approved_at": None,
                },
            )

            plan.status = "planned"
            plan.save(update_fields=["status"])

            return result

        #
        # Auto approved
        #

        ActionApproval.objects.update_or_create(
            action_plan_id=plan.id,
            defaults={
                "approved": True,
                "approved_at": timezone.now(),
            },
        )

        plan.status = "queued"
        plan.save(update_fields=["status"])

        return result