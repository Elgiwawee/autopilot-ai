# cloud/providers/gcp.py
from datetime import date
from cloud.providers.base import CloudProviderInterface
from google.oauth2 import service_account
from google.cloud import compute_v1
from google.cloud import monitoring_v3
from google.cloud import bigquery


class GCPProvider(CloudProviderInterface):

    def __init__(self, cloud_account):
        super().__init__(cloud_account)
        self.credentials = self._load_credentials()
        self.project_id = cloud_account.project_id

    def _load_credentials(self):
        return service_account.Credentials.from_service_account_info(
            self.cloud_account.service_account_json
        )


    def fetch_resources(self):
        client = compute_v1.InstancesClient(credentials=self.credentials)

        resources = []

        request = compute_v1.AggregatedListInstancesRequest(
            project=self.project_id
        )

        for zone, response in client.aggregated_list(request=request):
            if not response.instances:
                continue

            for instance in response.instances:
                resources.append({
                    "resource_id": instance.id,
                    "resource_type": "gce_instance",
                    "region": zone,
                    "metadata": instance.to_dict(),
                    "state": instance.status,
                    "cost_per_hour": 0,
                })

        return resources


    def fetch_costs(self, start_date: date, end_date: date):
        bq = bigquery.Client(
            credentials=self.credentials,
            project=self.project_id,
        )

        query = f"""
        SELECT
            service.description AS service,
            resource.name AS resource_id,
            DATE(usage_start_time) AS date,
            SUM(cost) AS cost
        FROM `{self.cloud_account.billing_table}`
        WHERE DATE(usage_start_time)
              BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY service, resource_id, date
        """

        records = []

        for row in bq.query(query).result():
            records.append({
                "service": row.service,
                "resource_id": row.resource_id,
                "date": row.date,
                "cost": float(row.cost),
            })

        return records


    def fetch_metrics(self, resource_ids, start_date, end_date):
        client = monitoring_v3.MetricServiceClient(
            credentials=self.credentials
        )

        metrics = []

        interval = monitoring_v3.TimeInterval(
            start_time=start_date,
            end_time=end_date,
        )

        for rid in resource_ids:
            request = monitoring_v3.ListTimeSeriesRequest(
                name=f"projects/{self.project_id}",
                filter=(
                    'metric.type="compute.googleapis.com/instance/cpu/utilization" '
                    f'AND resource.label.instance_id="{rid}"'
                ),
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            )

            series = client.list_time_series(request=request)
            metrics.append({
                "resource_id": rid,
                "datapoints": [p.value.double_value for s in series for p in s.points],
            })

        return metrics


    def execute_action(self, action):
        action.execute(self)

    def rollback(self, action):
        action.rollback(self)

  # Uses BigQuery 