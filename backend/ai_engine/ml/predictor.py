# ai_engine/ml/predictor.py

from ai_engine.ml.risk_model import load_risk_model, load_online_model


FEATURE_ORDER = [
    "cpu_avg",
    "memory_avg",
    "network_avg",
    "estimated_monthly_savings",
    "risk_score",
    "execution_time_seconds",
]


def predict_execution(feature_dict):

    features = [feature_dict.get(f, 0) for f in FEATURE_ORDER]
    # 1️⃣ Try online model first
    online_model = load_online_model()

    if online_model and online_model.is_initialized:

        prediction = online_model.predict(features)

        return bool(prediction)

    # 2️⃣ fallback to anomaly model
    anomaly_model = load_risk_model()

    if anomaly_model:

        score = anomaly_model.score(features)

        return score < 0.5

    # 3️⃣ default safe behavior
    return True