# ai_engine/training/train_model.py

import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from ai_engine.models import ResourceFeature


MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")


def load_training_dataset():

    qs = ResourceFeature.objects.exclude(action_success=None).values(
        "cpu_avg",
        "memory_avg",
        "network_avg",
        "estimated_monthly_savings",
        "risk_score",
        "execution_time_seconds",
        "action_success",
    )

    df = pd.DataFrame(list(qs))

    if len(df) < 50:
        return None

    return df


def train_risk_model():

    df = load_training_dataset()

    if df is None:
        return

    X = df.drop(columns=["action_success"])
    y = df["action_success"]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
    )

    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)

    tmp_path = MODEL_PATH + ".tmp"

    joblib.dump(model, tmp_path)

    os.replace(tmp_path, MODEL_PATH)