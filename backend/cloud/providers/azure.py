# cloud/providers/azure.py
from datetime import date
from cloud.providers.base import CloudProviderInterface

try:
    from azure.identity import ClientSecretCredential
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.costmanagement import CostManagementClient
    from azure.monitor.query import MetricsQueryClient
except ImportError:
    # Prevent Django startup crash if Azure SDK is missing
    ClientSecretCredential = None
    ComputeManagementClient = None
    CostManagementClient = None
    MetricsQueryClient = None


class AzureProvider(CloudProviderInterface):

    def __init__(self, cloud_account):
        super().__init__(cloud_account)

        if not ClientSecretCredential:
            raise RuntimeError(
                "Azure SDKs not installed. Install Azure dependencies to use AzureProvider."
            )

        self.credential = self._authenticate()
        self.metrics_client = MetricsQueryClient(self.credential)

    def _authenticate(self):
        return ClientSecretCredential(
            tenant_id=self.cloud_account.tenant_id,
            client_id=self.cloud_account.client_id,
            client_secret=self.cloud_account.client_secret,
        )

    def fetch_resources(self):
        compute = ComputeManagementClient(
            self.credential,
            self.cloud_account.subscription_id,
        )

        resources = []

        for vm in compute.virtual_machines.list_all():
            resources.append({
                "resource_id": vm.id,
                "resource_type": "virtual_machine",
                "region": vm.location,
                "metadata": vm.as_dict(),
                "state": vm.provisioning_state,
                "cost_per_hour": 0,
            })

        return resources

    def fetch_costs(self, start_date: date, end_date: date):
        cost_client = CostManagementClient(self.credential)

        scope = f"/subscriptions/{self.cloud_account.subscription_id}"

        query = {
            "type": "Usage",
            "timeframe": "Custom",
            "timePeriod": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat(),
            },
            "dataset": {
                "granularity": "Daily",
                "aggregation": {
                    "totalCost": {"name": "Cost", "function": "Sum"}
                },
            },
        }

        result = cost_client.query.usage(scope, query)

        records = []
        for row in result.rows:
            records.append({
                "service": "azure_compute", 
                "resource_id": None,# Azure Cost Management doesn't break down by service in the same way as AWS, so we use a generic service name
                "date": row[0],
                "cost": float(row[1]),
            })

        return records

    def fetch_metrics(self, resource_ids, start_date, end_date):
        metrics = []

        for rid in resource_ids:
            response = self.metrics_client.query_resource(
                resource_uri=rid,
                metric_names=["Percentage CPU"],
                timespan=(start_date, end_date),
                granularity="PT1H",
            )

            metrics.append({
                "resource_id": rid,
                "metrics": response.metrics,
            })

        return metrics

    def execute_action(self, action):
        action.execute(self)

    def rollback(self, action):
        action.rollback(self)
