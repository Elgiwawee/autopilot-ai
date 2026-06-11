# monitoring/services/gpu_service.py

from django.db.models import QuerySet
from cloud.models import CloudAccount, CloudResource


class GPUService:
    """
    Production-grade GPU inventory service
    """

    @staticmethod
    def _base_queryset(organization) -> QuerySet:
        """
        Returns base queryset of GPU resources for an organization.
        """

        active_accounts = CloudAccount.objects.filter(
            organization=organization,
            is_active=True,
        )

        return CloudResource.objects.filter(
            cloud_account__in=active_accounts,
            resource_type="gpu",
        ).select_related(
            "cloud_account", 
            "cloud_account__provider",
        )

    # ----------------------------------------------------
    # Public Methods
    # ----------------------------------------------------

    @classmethod
    def list(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
    ):
        qs = cls._base_queryset(organization)

        if cloud:
            qs = qs.filter(cloud_account__provider__code=cloud)

        if region:
            qs = qs.filter(region=region)

        return [
            cls._serialize(resource)
            for resource in qs
        ]

    @classmethod
    def count(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
    ) -> int:
        qs = cls._base_queryset(organization)

        if cloud:
            qs = qs.filter(cloud_account__provider__code=cloud)

        if region:
            qs = qs.filter(region=region)

        return qs.count()

    # ----------------------------------------------------
    # Internal serializer
    # ----------------------------------------------------

    @staticmethod
    def _serialize(resource):
        monthly_cost = float(resource.cost_per_hour or 0) * 730

        utilization = float(
            resource.metadata.get("gpu_utilization")
            or resource.metadata.get("utilization")
            or 0
        )

        return {
            "id": str(resource.id),

            # frontend fields
            "name": resource.external_id,
            "model": resource.metadata.get("model", "Unknown"),
            "utilization": utilization,
            "status": resource.state,
            "monthly_cost": round(monthly_cost, 2),

            # optional extra info
            "provider": resource.cloud_account.provider.name,
            "region": resource.region,
            "cost_per_hour": float(resource.cost_per_hour or 0),
            "memory_gb": resource.metadata.get("memory_gb"),
            "attached_to": resource.metadata.get("attached_to"),
            "last_seen": resource.last_seen,
        }