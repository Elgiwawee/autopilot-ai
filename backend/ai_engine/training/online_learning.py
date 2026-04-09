# ai_engine/training/online_learning.py

from ai_engine.ml.risk_model import load_online_model
from ai_engine.features.feature_builder import build_feature_row


def update_online_model(plan, utilization, decision, outcome):
    """
    Update incremental model after every execution.
    """

    model = load_online_model()

    feature_dict = build_feature_row(
        plan,
        utilization,
        decision,
        outcome,
    )

    features = [
        feature_dict["cpu_avg"],
        feature_dict["memory_avg"],
        feature_dict["network_avg"],
        feature_dict["estimated_monthly_savings"],
        feature_dict["risk_score"],
        feature_dict["execution_time_seconds"],
    ]

    label = 1 if outcome.success else 0

    model.partial_train(features, label)

    model.save()