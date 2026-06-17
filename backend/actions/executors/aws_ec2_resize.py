# actions/executors/aws_ec2_resize.py

import boto3


def resize_ec2_instance(resource, credentials, target_instance_type):
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    instance_id = resource.external_id

    ec2.stop_instances(InstanceIds=[instance_id])
    ec2.get_waiter("instance_stopped").wait(InstanceIds=[instance_id])

    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={"Value": target_instance_type},
    )

    ec2.start_instances(InstanceIds=[instance_id])


def rollback_resize(resource, credentials, original_instance_type):
    resize_ec2_instance(resource, credentials, original_instance_type)
