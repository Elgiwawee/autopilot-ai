# actions/services/decision_service.py

from actions.models import Decision

from ai_engine.risk_engine import (
    compute_risk_score,
    classify_risk,
)
from billing.baseline.engine import BaselineEngine
from django.utils import timezone
from ai_engine.utilization import utilization_profile
from ai_engine.ml.predictor import predict_execution
from ai_engine.reinforcement.policy import OptimizationPolicy
from ai_engine.simulator.simulation_service import SimulationService
from ai_engine.spot.model import allow_spot

def make_decision(plan):
    """
    Decide whether an action plan can be executed automatically.
    Combines:
    - Rule-based risk engine
    - ML prediction
    - RL policy decision
    """

    resource = plan.resource

    # =========================================
    # 1️⃣ COLLECT UTILIZATION METRICS
    # =========================================
    utilization = utilization_profile(resource)

    cpu = utilization.get("cpu_avg") or 0
    memory = utilization.get("memory_avg") or 0
    network = utilization.get("network_avg") or 0

    # =========================================
    # 2️⃣ RULE-BASED RISK ENGINE
    # =========================================
    risk_score = compute_risk_score(cpu=cpu)
    risk_level = classify_risk(risk_score)


    baseline, confidence, explanations = BaselineEngine().compute(
        cloud_account=plan.resource.cloud_account,
        service=plan.resource.service,
        resource_id=plan.resource.id,
        target_date=timezone.now().date(),
    )

    estimated_savings = baseline or plan.estimated_monthly_savings or 0
    # =========================================
    # 3️⃣ BUILD ML FEATURES
    # =========================================
    features = {
        "cpu_avg": cpu,
        "memory_avg": memory,
        "network_avg": network,
        "estimated_monthly_savings": estimated_savings,
        "risk_score": risk_score,
        "execution_time_seconds": 5,
    }

    # =========================================
    # 4️⃣ ML PREDICTION
    # =========================================
    ml_allows = predict_execution(features)

    # =========================================
    # 5️⃣ RL POLICY DECISION (🔥 NEW)
    # =========================================
    policy = OptimizationPolicy()

    action = getattr(
        plan,
        "action_type",
        None,
    ) or getattr(
        plan,
        "action",
        None,
    )

    rl_allows = policy.should_execute(
        action=action,
        risk_score=risk_score,
        estimated_savings = baseline or plan.estimated_monthly_savings or 0,
    )

    # =========================================
    # 6️⃣ FINAL DECISION LOGIC
    # =========================================
    auto_execute = (
        risk_level == "SAFE"   # rule safety
        and ml_allows          # ML approval
        and rl_allows          # RL policy approval
    )

        # =========================================
    # 🔮 3️⃣ PRE-EXECUTION SIMULATION (NEW)
    # =========================================
    simulation = SimulationService().run(
        action=plan.action_type,
        resource_type=plan.resource.resource_type,
        parameters={}
    )

    predicted_risk = simulation.predicted_risk
    predicted_savings = simulation.predicted_savings
    confidence = simulation.confidence

    # =========================================
    # 7️⃣ SAVE DECISION
    # =========================================
    final_risk_score = (
        risk_score + predicted_risk
    ) / 2

    decision = Decision.objects.create(
        plan=plan,
        risk_score=final_risk_score,
        risk_level=risk_level,
        auto_execute_allowed=auto_execute,
        reason=(
            f"risk={risk_score:.2f}, "
            f"level={risk_level}, "
            f"ml={ml_allows}, "
            f"rl={rl_allows}, "
            f"simulated_risk={predicted_risk:.2f}, "
            f"simulated_savings={predicted_savings:.2f}, "
            f"confidence={confidence:.2f}"
        ),
    )

    if action == "use_spot_instance":
        if not allow_spot(probability=0.03):
            decision.auto_execute_allowed = False
            decision.reason += " | Spot prediction rejected."
            decision.save(
                update_fields=[
                    "auto_execute_allowed",
                    "reason",
                ]
            )
        
    return decision