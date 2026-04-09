# ai_engine/services/recommendation_service.py

from cloud.models import CloudResource
from ai_engine.planner import generate_action_plans
from billing.models import CostSnapshot


def generate_recommendations(
    account,
    metrics,
    resources=None,
    gpu_usage=None,
):

    # ---------------------------------
    # FALLBACK: LOAD RESOURCES
    # ---------------------------------
    if resources is None:
        resources = CloudResource.objects.filter(
            cloud_account=account
        )

    plans = []

    # ---------------------------------
    # CORE + COST-AWARE AI
    # ---------------------------------
    for resource in resources:

        # ✅ Fetch last 7 days cost for THIS resource
        costs = CostSnapshot.objects.filter(
            cloud_account=account,
            resource_id=resource.external_id
        ).order_by("-date")[:7]

        avg_cost = (
            sum(float(c.cost) for c in costs) / len(costs)
            if costs else 0
        )

        # 🔥 EXISTING PLANNER
        plans.extend(generate_action_plans(resource))

        # ---------------------------------
        # 💰 COST-BASED AI RULE (NEW)
        # ---------------------------------
        if avg_cost > 50 and resource.state == "running":
            plans.append({
                "type": "HIGH_COST_RESOURCE",
                "resource": resource,
                "reason": f"High avg daily cost: ${avg_cost:.2f}"
            })

    # ---------------------------------
    # 🔥 GPU AI MODULE (YOUR $$$ FEATURE)
    # ---------------------------------
    if gpu_usage:
        for resource in resources:

            if resource.resource_type != "gpu":
                continue

            rid = resource.external_id
            gpu_util = gpu_usage.get(rid, 0)

            if gpu_util < 10:
                plans.append({
                    "type": "STOP_IDLE_GPU",
                    "resource": resource,
                    "reason": f"Low GPU utilization ({gpu_util:.2f}%)"
                })

    return plans

#plug in many AI modules later
"""
generate_idle_ec2_recommendations()
generate_rightsize_ec2()
generate_k8s_binpacking()
generate_spot_rebalance()
generate_gpu_idle_detection()
"""
