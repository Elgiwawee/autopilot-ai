# actions/services/action_service.py

from actions.models import ActionExecution


class ActionService:

    @staticmethod
    def _base_queryset(organization):
        return (
            ActionExecution.objects.filter(
                plan__cloud_account__organization=organization
            )
            .select_related(
                "plan",
                "plan__cloud_account",
            )
        )

    @classmethod
    def recent(cls, organization, cloud=None, region=None, limit=10):
        qs = cls._base_queryset(organization)

        if cloud:
            qs = qs.filter(
                plan__cloud_account__provider__code=cloud
            )

        if region:
            qs = qs.filter(
                plan__cloud_account__region=region
            )

        qs = qs.order_by("-executed_at")[:limit]

        return [
            {
                "id": str(a.id),
                "status": a.status,
                "executed_at": a.executed_at,
                "cloud": (
                    a.plan.cloud_account.provider.code
                    if a.plan
                    else None
                ),
                "resource_id": (
                    a.plan.provider_resource_id
                    if a.plan
                    else None
                ),
                "action_type": (
                    a.plan.action
                    if a.plan
                    else None
                ),
            }
            for a in qs
        ]