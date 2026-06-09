import boto3


def stop_ec2_instance(instance_id, cloud_account):
    """
    Stops an EC2 instance using AssumeRole credentials.
    """

    sts = boto3.client("sts")

    assume_kwargs = {
        "RoleArn": cloud_account.role_arn,
        "RoleSessionName": "autopilot-execution",
    }

    if cloud_account.external_id:
        assume_kwargs["ExternalId"] = cloud_account.external_id

    assumed = sts.assume_role(**assume_kwargs)

    creds = assumed["Credentials"]

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name="us-east-1",  # we'll improve this later
    )

    return ec2.stop_instances(
        InstanceIds=[instance_id]
    )