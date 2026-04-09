# cloud/aws_test.py

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

print("DEBUG AWS_ROLE_ARN =", os.getenv("AWS_ROLE_ARN"))

import boto3

def test_assume_role():
    sts = boto3.client(
        "sts",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    assumed_role = sts.assume_role(
        RoleArn=os.getenv("AWS_ROLE_ARN"),
        RoleSessionName="ai-cloud-autopilot-session"
    )

    creds = assumed_role["Credentials"]

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    instances = ec2.describe_instances()
    print("✅ AWS CONNECTION SUCCESSFUL")
    print(f"Found {len(instances['Reservations'])} EC2 reservation(s)")


if __name__ == "__main__":
    test_assume_role()
