# cloud/services/accounts.pyS

from uuid import UUID

from cloud.models import CloudAccount


def get_active_cloud_accounts(organization):
    """
    Accepts either:
      - Organization instance
      - UUID
      - string UUID

    Returns active cloud accounts.
    """

    if isinstance(organization, (str, UUID)):
        lookup = {"organization_id": organization}
    else:
        lookup = {"organization": organization}

    return (
        CloudAccount.objects.filter(
            **lookup,
            is_active=True,
        )
        .select_related("provider")
    )