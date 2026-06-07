# actions/services/action_service.py

from actions.models import ActionExecution


class ActionService:

    @staticmethod
    def _base_queryset(organization):
        return (
            ActionExecution.objects.filter(
                optimization__cloud_account__organization=organization
            )
            .select_related(
                "optimization",
                "optimization__cloud_account",
                "optimization__cloud_account__provider",
            )
        )

    @classmethod
    def recent(cls, organization, cloud=None, region=None, limit=10):
        qs = cls._base_queryset(organization)

        if cloud:
            qs = qs.filter(
                optimization__cloud_account__provider__code=cloud
            )

        if region:
            qs = qs.filter(
                optimization__cloud_account__region=region
            )

        qs = qs.order_by("-executed_at")[:limit]

        return [
            {
                "id": str(a.id),
                "status": a.status,
                "executed_at": a.executed_at,
                "cloud": (
                    a.optimization.cloud_account.provider.code
                    if a.optimization
                    else None
                ),
                "resource_id": (
                    a.optimization.resource_id
                    if a.optimization
                    else None
                ),
                "action_type": (
                    a.optimization.action_type
                    if a.optimization
                    else None
                ),
            }
            for a in qs
        ]