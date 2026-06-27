from dataclasses import dataclass


@dataclass
class VerificationResult:
    success: bool
    reason: str
    actual_state: dict | None = None


class VerificationEngine:
    """
    Confirms that the cloud provider actually performed
    the requested action.

    It NEVER executes actions.

    It only verifies.
    """

    @staticmethod
    def verify(executor, plan):

        result = executor.verify(
            target_type=plan.resource_type,
            namespace=plan.namespace,
            target_name=(
                plan.target_name
                or plan.provider_resource_id
            ),
            action=plan.action,
            parameters=plan.parameters or {},
        )

        return VerificationResult(
            success=result.get("verified", False),
            reason=result.get("reason", ""),
            actual_state=result.get("actual_state"),
        )