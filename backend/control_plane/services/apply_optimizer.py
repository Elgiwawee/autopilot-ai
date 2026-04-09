import boto3


def apply_optimization(opt):
    provider = opt.cloud_account.provider

    if provider == "AWS":
        return apply_aws(opt)


def apply_aws(opt):
    ec2 = boto3.client("ec2")

    if opt.action_type == "TERMINATE":
        ec2.terminate_instances(
            InstanceIds=[opt.resource_id]
        )

    elif opt.action_type == "RIGHTSIZE":
        ec2.modify_instance_attribute(
            InstanceId=opt.resource_id,
            InstanceType={"Value": "t3.medium"}  # example
        )

    elif opt.action_type == "SPOT":
        # simplified example
        ec2.request_spot_instances(
            InstanceCount=1,
            Type="one-time"
        )