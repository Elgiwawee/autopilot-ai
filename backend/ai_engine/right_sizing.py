# ai_engine/right_sizing.py
from ai_engine.risk_engine import compute_risk_score, classify_risk, predict_execution
from ai_engine.instance_families import smaller_instance
from ai_engine.utilization import utilization_profile
from ai_engine.resize_rules import resize_safe
from actions.models import ActionPlan


def estimate_savings(resource):
    # simple realistic fallback
    current = resource.cost_per_hour
    target = current * 0.7
    return (current - target) * 24 * 30


def generate_resize_plan(resource):
    instance_type = resource.metadata.get("InstanceType")

    if not instance_type:
        return None

    target = smaller_instance(instance_type)

    if not target:
        return None

    utilization = utilization_profile(resource)

    safe, reason = resize_safe(resource, utilization)
    if not safe:
        return None

    # ✅ RISK CALCULATION (MOVED BEFORE RETURN)
    cpu = utilization.get("cpu_avg") or 0
    memory = utilization.get("memory_avg") or 0
    network = utilization.get("network_avg") or 0

    risk_score = compute_risk_score(cpu=cpu, memory=memory, network=network)
    risk_level = classify_risk(risk_score)

    # ❌ Block dangerous
    if risk_level == "DANGEROUS":
        return None

    # ❌ ML prediction block
    if not predict_execution(risk_score):
        return None

    estimated_savings = estimate_savings(resource)

    return ActionPlan.objects.create(
        resource=resource,
        action_type="resize",
        target_instance=target,
        estimated_savings=estimated_savings,
        risk_level=risk_level.lower(),
        is_safe=True,
        explanation=(
            f"CPU avg: {cpu:.1f}%, "
            f"risk: {risk_level}. "
            f"Resize {instance_type} → {target}."
        ),
    )