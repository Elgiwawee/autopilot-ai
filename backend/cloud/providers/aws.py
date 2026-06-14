# cloud/providers/aws.py
import boto3
from datetime import date
from cloud.providers.base import CloudProviderInterface


class AWSProvider(CloudProviderInterface):

    def __init__(self, cloud_account):
        super().__init__(cloud_account)
        self.session = self._assume_role()

    def _assume_role(self):
        sts = boto3.client("sts")
        resp = sts.assume_role(
            RoleArn=self.cloud_account.role_arn,
            RoleSessionName="autopilot",
        )

        creds = resp["Credentials"]

        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

    def fetch_resources(self):
        ec2 = self.session.client("ec2")
        paginator = ec2.get_paginator("describe_instances")

        resources = []

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    resources.append({
                        "resource_id": instance["InstanceId"],
                        "resource_type": "ec2_instance",
                        "region": instance["Placement"]["AvailabilityZone"],
                        "state": instance["State"]["Name"],   # ✅ ADD
                        "cost_per_hour": 0,                   # (later pricing service)
                        "metadata": instance,
                    })

        return resources

    def fetch_costs(self, start_date: date, end_date: date):
        ce = self.session.client("ce")

        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start_date.isoformat(),
                "End": end_date.isoformat(),
            },
            Granularity="DAILY",
            Metrics=[
                "UnblendedCost",
                "UsageQuantity",
            ],
            GroupBy=[
                {
                    "Type": "DIMENSION",
                    "Key": "SERVICE",
                },
                {
                    "Type": "DIMENSION",
                    "Key": "RESOURCE_ID",
                },
                {
                    "Type": "DIMENSION",
                    "Key": "REGION",
                },
            ]
        )

        records = []

        for day in response["ResultsByTime"]:
            for group in day["Groups"]:

                cost = float(
                    group["Metrics"]["UnblendedCost"]["Amount"]
                )

                usage = float(
                    group["Metrics"]["UsageQuantity"]["Amount"]
                )

                records.append({
                    "service": group["Keys"][0],

                    "resource_id": (
                        group["Keys"][1]
                        if group["Keys"][1]
                        else None
                    ),

                    "region": (
                        group["Keys"][2]
                        if len(group["Keys"]) > 2
                        else "global"
                    ),

                    "date": day["TimePeriod"]["Start"],

                    "cost": cost,

                    "usage": usage,

                    "currency": "USD",
                })

        return records

    def fetch_metrics(self, resource_ids, metric_name, start_date, end_date):
        cw = self.session.client("cloudwatch")

        metrics = []

        for rid in resource_ids:
            resp = cw.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName=metric_name,
                Dimensions=[{"Name": "InstanceId", "Value": rid}],
                StartTime=start_date,
                EndTime=end_date,
                Period=3600,
                Statistics=["Average"],
            )

            datapoints = [
                {
                    "timestamp": dp["Timestamp"],
                    "value": dp["Average"],
                }
                for dp in resp["Datapoints"]
            ]

            metrics.append({
                "resource_id": rid,
                "datapoints": datapoints,
            })

        return metrics
    
    def execute_action(self, action):
        action.execute(self)

    def rollback(self, action):
        action.rollback(self)