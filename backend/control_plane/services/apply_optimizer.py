# control_plane/services/apply_optimizer.py

from actions.executors.aws_ec2 import stop_ec2_instance


def apply_optimization(plan):
    """
    Dispatch optimization execution to the proper executor.
    """

    provider = (
        getattr(plan.cloud_account.provider, "code", "")
        .lower()
    )

    if provider == "aws":
        return apply_aws(plan)

    raise NotImplementedError(
        f"Provider '{provider}' not supported."
    )


def apply_aws(plan):
    """
    Execute AWS optimization.
    """

    if plan.action == "TERMINATE":
        return stop_ec2_instance(
            instance_id=plan.provider_resource_id,
            credentials=plan.cloud_account.credentials,
        )

    raise NotImplementedError(
        f"Unsupported AWS action '{plan.action}'."
    )