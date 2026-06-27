from dataclasses import dataclass

from actions.models import ExecutionPlan


@dataclass
class RollbackResult:
    success: bool
    reason: str


class RollbackEngine:
    """
    Restores a resource to its previous state.

    This engine never decides WHEN to rollback.
    It only performs the rollback when requested.

    Decision flow:

        Execution
            ↓
        Verification
            ↓
        Verification failed?
            ↓
        RollbackEngine.rollback(...)
    """

    @staticmethod
    def rollback(
        executor,
        plan: ExecutionPlan,
    ) -> RollbackResult:

        try:

            result = executor.rollback(
                action=plan.action,
                current_state=plan.current_state or {},
                proposed_state=plan.proposed_state or {},
                target_type=plan.resource_type,
                namespace=plan.namespace,
                target_name=(
                    plan.target_name
                    or plan.provider_resource_id
                ),
                parameters=plan.parameters or {},
            )

            return RollbackResult(
                success=result.get("success", False),
                reason=result.get(
                    "reason",
                    "Rollback completed.",
                ),
            )

        except Exception as exc:

            return RollbackResult(
                success=False,
                reason=str(exc),
            )