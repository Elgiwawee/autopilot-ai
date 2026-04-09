# monitoring/collectors/aws_cloudwatch.py

import boto3
from datetime import datetime, timedelta
from monitoring.models import ResourceMetric


def collect_ec2_cpu_metrics(resource, credentials):

    cloudwatch = boto3.client(
        "cloudwatch",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": resource.external_id}],
        StartTime=datetime.utcnow() - timedelta(days=14),
        EndTime=datetime.utcnow(),
        Period=3600,
        Statistics=["Average"],
    )

    values = []

    for point in response.get("Datapoints", []):

        ResourceMetric.objects.create(
            resource=resource,
            metric_name="cpu_avg",
            value=point["Average"],
        )

        values.append(point["Average"])

    if values:
        return {
            "avg": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "samples": len(values),
            "values": values,
        }

    return None