# control_plane/services/apply_optimizer.py

from actions.executors.aws_ec2 import stop_ec2_instance


def apply_optimization(opt):
    """
    Dispatch optimization execution to the proper executor.
    """

    provider = (
        getattr(opt.cloud_account.provider, "code", "")
        .lower()
    )

    if provider == "aws":
        return apply_aws(opt)

    raise NotImplementedError(
        f"Provider '{provider}' not supported."
    )


def apply_aws(opt):
    """
    Execute AWS optimization.
    """

    if opt.action_type == "TERMINATE":
        return stop_ec2_instance(
            instance_id=opt.resource_id,
            credentials=opt.cloud_account.credentials,
        )

    raise NotImplementedError(
        f"Unsupported AWS action '{opt.action_type}'."
    )