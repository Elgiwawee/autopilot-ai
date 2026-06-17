# ai_engine/planner.py

import logging

from ai_engine.right_sizing import generate_resize_plan
from ai_engine.storage.zombie import (
    is_zombie,
    generate_delete_plan,
)
from ai_engine.storage.gp3_rules import (
    gp2_to_gp3_candidate,
)
from ai_engine.storage.planner import (
    generate_gp3_plan,
)

logger = logging.getLogger(__name__)


def generate_action_plans(resource):
    """
    Runs all recommendation engines for a resource.

    Every planner is isolated so that failure in one
    module does not stop the others.

    Returns:
        list[ActionPlan]
    """

    plans = []

    # -----------------------------------
    # EC2 RIGHTSIZING
    # -----------------------------------

    try:

        resize = generate_resize_plan(resource)

        if resize:
            plans.append(resize)

    except Exception:

        logger.exception(
            "Rightsizing planner failed for %s",
            getattr(resource, "external_id", resource.pk),
        )

    # -----------------------------------
    # EBS ANALYSIS
    # -----------------------------------

    if resource.resource_type == "ebs":

        # Zombie volumes

        try:

            if is_zombie(resource):

                plan = generate_delete_plan(resource)

                if plan:
                    plans.append(plan)

        except Exception:

            logger.exception(
                "Zombie planner failed for %s",
                getattr(resource, "external_id", resource.pk),
            )

        # GP2 -> GP3 migration

        try:

            if gp2_to_gp3_candidate(resource):

                plan = generate_gp3_plan(resource)

                if plan:
                    plans.append(plan)

        except Exception:

            logger.exception(
                "GP3 planner failed for %s",
                getattr(resource, "external_id", resource.pk),
            )

    return plans


# Plugin system letter
""""
PLANNERS = [
    generate_resize_plan,
    generate_delete_plan,
    generate_gp3_plan,
    generate_snapshot_plan,
    generate_idle_gpu_plan,
    generate_nat_gateway_plan,
    generate_rds_plan,
    generate_spot_plan,
]
"""