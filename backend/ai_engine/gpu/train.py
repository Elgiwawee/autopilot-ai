# ai_engine/gpu/train.py

from pathlib import Path

import joblib

from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).parent / "gpu_model.pkl"


def train(X, y):
    """
    Train GPU recommendation model.
    """

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X, y)

    joblib.dump(
        model,
        MODEL_PATH,
    )

    return model