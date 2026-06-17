# actions/executors/aws_ebs_gp3.py

import boto3


def convert_to_gp3(volume, credentials):
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    ec2.modify_volume(
        VolumeId=volume.volume_id,
        VolumeType="gp3"
    )


def rollback_gp3(volume, credentials):
    ec2.modify_volume(
        VolumeId=volume.volume_id,
        VolumeType="gp2"
    )
