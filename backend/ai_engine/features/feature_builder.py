from ai_engine.models import ResourceFeature


def build_feature_row(plan, utilization, decision, outcome=None):

    cpu = utilization.get("cpu_avg") or 0
    memory = utilization.get("memory_avg") or 0
    network = utilization.get("network_avg") or 0

    return {
        "resource_id": str(plan.resource.id),
        "resource_type": plan.resource.resource_type,

        "cpu_avg": cpu,
        "memory_avg": memory,
        "network_avg": network,

        "estimated_monthly_savings": plan.estimated_monthly_savings or 0,

        "risk_score": decision.risk_score,

        "execution_time_seconds": 5,

        "action_success": outcome.success if outcome else None,
    }


def store_resource_features(plan, utilization, decision, outcome=None):

    ResourceFeature.objects.create(
        resource_id=str(plan.resource.id),
        resource_type=plan.resource.resource_type,

        cpu_avg=utilization.get("cpu_avg") or 0,
        memory_avg=utilization.get("memory_avg") or 0,
        network_avg=utilization.get("network_avg") or 0,

        estimated_monthly_savings=plan.estimated_savings or 0,

        risk_score=decision.risk_score,

        execution_time_seconds=5,

        action_success=(outcome.success if outcome else None),
    )