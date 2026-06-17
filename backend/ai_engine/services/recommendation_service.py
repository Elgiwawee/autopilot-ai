# ai_engine/services/recommendation_service.py

from cloud.models import CloudResource
from billing.models import CostSnapshot
from actions.models import ActionPlan
from ai_engine.planner import generate_action_plans


def generate_recommendations(
    account,
    metrics,
    resources=None,
    gpu_usage=None,
):
    """
    Generate recommendation objects for a cloud account.

    Returns a list of ActionPlan instances.
    """

    if resources is None:
        resources = CloudResource.objects.filter(
            cloud_account=account
        )

    recommendations = []

    for resource in resources:

        # -----------------------------------
        # Existing planner modules
        # -----------------------------------

        recommendations.extend(
            generate_action_plans(resource)
        )

        # -----------------------------------
        # Cost-aware recommendation
        # -----------------------------------

        costs = (
            CostSnapshot.objects
            .filter(
                cloud_account=account,
                resource_id=resource.external_id,
            )
            .order_by("-date")[:7]
        )

        avg_cost = (
            sum(float(c.cost) for c in costs) / len(costs)
            if costs else 0
        )

        if (
            avg_cost > 50
            and resource.state == "running"
        ):

            recommendations.append(
                ActionPlan.objects.create(
                    resource=resource,
                    action_type="HIGH_COST_REVIEW",
                    estimated_savings=avg_cost * 30,
                    risk_level="low",
                    is_safe=True,
                    explanation=(
                        f"Average daily cost "
                        f"${avg_cost:.2f}. "
                        "Recommend review for "
                        "possible optimization."
                    ),
                )
            )

        # -----------------------------------
        # GPU idle detection
        # -----------------------------------

        if (
            gpu_usage
            and resource.resource_type == "gpu"
        ):

            gpu_util = gpu_usage.get(
                resource.external_id,
                0,
            )

            if gpu_util < 10:

                recommendations.append(
                    ActionPlan.objects.create(
                        resource=resource,
                        action_type="STOP_IDLE_GPU",
                        estimated_savings=avg_cost * 30,
                        risk_level="medium",
                        is_safe=False,
                        explanation=(
                            f"GPU utilization only "
                            f"{gpu_util:.2f}%."
                        ),
                    )
                )

    return recommendations


"""
Future AI modules:

generate_idle_ec2_recommendations()
generate_rightsize_ec2()
generate_k8s_binpacking()
generate_spot_rebalance()
generate_gpu_idle_detection()
generate_idle_rds_detection()
generate_idle_nat_gateway_detection()
generate_unused_elb_detection()
generate_orphaned_ip_detection()
"""