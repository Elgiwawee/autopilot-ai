from decimal import Decimal

from cloud.models import CloudAccount, CloudResource


class CostService:
    """
    Enterprise Cost Service.

    Responsible for aggregating cloud spend.

    Current source:
        CloudResource.cost_per_hour

    Future source:
        AWS Cost Explorer
        Azure Cost Management
        GCP Billing Export

    Everything else in Autopilot should obtain
    cloud spending through this service.
    """

    HOURS_PER_MONTH = Decimal("730")


    @classmethod
    def get_resource_monthly_cost(cls, resource):

        return Decimal(resource.cost_per_hour) * cls.HOURS_PER_MONTH


    @classmethod
    def get_account_monthly_cost(cls, cloud_account):

        total = Decimal("0")

        resources = CloudResource.objects.filter(
            cloud_account=cloud_account
        )

        for resource in resources:

            total += cls.get_resource_monthly_cost(resource)

        return total


    @classmethod
    def get_organization_monthly_cost(cls, organization):

        total = Decimal("0")

        accounts = CloudAccount.objects.filter(
            organization=organization
        )

        for account in accounts:

            total += cls.get_account_monthly_cost(account)

        return total


    @classmethod
    def get_provider_monthly_cost(
        cls,
        organization,
        provider,
    ):

        total = Decimal("0")

        accounts = CloudAccount.objects.filter(
            organization=organization,
            provider=provider,
        )

        for account in accounts:

            total += cls.get_account_monthly_cost(account)

        return total