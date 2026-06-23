import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build

from cloud.models import (
    CloudAccount,
    CloudResource,
)

from cloud.utils.json import json_safe

from cloud.cost.gcp_cost import (
    calculate_gcp_hourly_cost,
)

from ai_engine.tasks.detector_tasks import (
    scan_cloud_for_opportunities,
)

logger = logging.getLogger(__name__)


def collect_gcp_instances(
    cloud_account_id,
):
    """
    Collect Compute Engine instances from all zones
    and sync them into CloudResource.

    Mirrors AWS collector behavior.
    """

    cloud_account = (
        CloudAccount.objects
        .select_related(
            "provider",
            "gcp",
        )
        .get(id=cloud_account_id)
    )

    provider = cloud_account.provider
    gcp = cloud_account.gcp

    credentials = (
        service_account.Credentials
        .from_service_account_info(
            gcp.service_account_json
        )
    )

    compute = build(
        "compute",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )

    project_id = gcp.project_id

    zones_request = compute.zones().list(
        project=project_id
    )

    while zones_request is not None:

        zones_response = zones_request.execute()

        for zone in zones_response.get(
            "items",
            [],
        ):

            zone_name = zone["name"]

            region = "-".join(
                zone_name.split("-")[:-1]
            )

            try:

                request = (
                    compute.instances().list(
                        project=project_id,
                        zone=zone_name,
                    )
                )

                response = request.execute()

                for instance in response.get(
                    "items",
                    [],
                ):

                    instance_id = str(
                        instance["id"]
                    )

                    machine_type = (
                        instance["machineType"]
                        .split("/")[-1]
                    )

                    state = (
                        instance.get(
                            "status",
                            "UNKNOWN",
                        )
                        .lower()
                    )

                    # ---------------------------------
                    # GPU Detection
                    # ---------------------------------

                    guest_accelerators = (
                        instance.get(
                            "guestAccelerators",
                            []
                        )
                    )

                    resource_type = (
                        "gpu"
                        if guest_accelerators
                        else "vm"
                    )

                    # ---------------------------------
                    # Cost
                    # ---------------------------------

                    hourly_cost = (
                        calculate_gcp_hourly_cost(
                            machine_type=machine_type,
                            region=region,
                        )
                    )

                    # ---------------------------------
                    # Metadata
                    # ---------------------------------

                    metadata = json_safe(
                        instance
                    )

                    metadata[
                        "machine_type"
                    ] = machine_type

                    metadata[
                        "zone"
                    ] = zone_name

                    metadata[
                        "region"
                    ] = region

                    metadata[
                        "instance_name"
                    ] = instance.get("name")

                    metadata[
                        "labels"
                    ] = instance.get(
                        "labels",
                        {}
                    )

                    metadata[
                        "tags"
                    ] = instance.get(
                        "tags",
                        {}
                    )

                    metadata[
                        "creation_timestamp"
                    ] = instance.get(
                        "creationTimestamp"
                    )

                    interfaces = (
                        instance.get(
                            "networkInterfaces",
                            []
                        )
                    )

                    if interfaces:

                        metadata[
                            "private_ip"
                        ] = (
                            interfaces[0]
                            .get("networkIP")
                        )

                        access_configs = (
                            interfaces[0]
                            .get(
                                "accessConfigs",
                                []
                            )
                        )

                        if access_configs:

                            metadata[
                                "public_ip"
                            ] = (
                                access_configs[0]
                                .get("natIP")
                            )

                    metadata[
                        "guest_accelerators"
                    ] = guest_accelerators

                    # ---------------------------------
                    # Save Resource
                    # ---------------------------------

                    CloudResource.objects.update_or_create(
                        cloud_account=cloud_account,
                        external_id=instance_id,
                        defaults={
                            "provider": provider,
                            "name": instance.get(
                                "name"
                            ),
                            "resource_type": resource_type,
                            "region": region,
                            "state": state,
                            "cost_per_hour": hourly_cost,
                            "metadata": metadata,
                        },
                    )

            except Exception:

                logger.exception(
                    "Failed scanning GCP zone %s",
                    zone_name,
                )

        zones_request = (
            compute.zones().list_next(
                previous_request=zones_request,
                previous_response=zones_response,
            )
        )

    logger.info(
        "Completed GCP inventory sync for account %s",
        cloud_account.id,
    )

    scan_cloud_for_opportunities.delay(
        cloud_account.id
    )