#monitoring/services/metrics_collector.py

from cloud.models import CloudResource
from monitoring.collectors.aws_cloudwatch import collect_ec2_cpu_metrics


def collect_metrics(account):
    """
    Collect metrics for all resources in a cloud account.
    Returns structured metric data for the AI engine.
    """

    resources = CloudResource.objects.filter(cloud_account=account)

    collected = []

    for resource in resources:

        # Example: EC2 instance
        if resource.resource_type == "ec2":

            metrics = collect_ec2_cpu_metrics(
                resource,
                account.get_temporary_credentials(),
            )

            if metrics:

                collected.append(
                    {
                        "resource_id": resource.external_id,
                        "resource_type": resource.resource_type,
                        "values": metrics["values"],
                        "avg": metrics["avg"],
                        "max": metrics["max"],
                        "min": metrics["min"],
                    }
                )

    return collected