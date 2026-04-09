# actions/services/aws_client.py

import boto3


def get_aws_session(cloud_account):
    """
    Assume role into customer's AWS account
    """

    sts = boto3.client("sts")

    assumed = sts.assume_role(
        RoleArn=cloud_account.role_arn,
        RoleSessionName="autopilot-session",
        ExternalId=cloud_account.external_id,  # 🔥 security
    )

    creds = assumed["Credentials"]

    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )


def get_aws_clients(cloud_account):
    session = get_aws_session(cloud_account)

    return {
        "ec2": session.client("ec2"),
        "cloudwatch": session.client("cloudwatch"),
    }