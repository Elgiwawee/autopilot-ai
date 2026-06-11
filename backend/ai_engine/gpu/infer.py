# ai_engine/gpu/infer.py

from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).parent / "gpu_model.pkl"

_model = None


def load_model():
    global _model

    if _model is None:
        if MODEL_PATH.exists():
            _model = joblib.load(MODEL_PATH)

    return _model


def gpu_decision(features):
    """
    Returns:
        prediction,
        confidence
    """

    model = load_model()

    if model is None:
        return "UNKNOWN", 0.0

    prediction = model.predict([features])[0]

    probabilities = model.predict_proba([features])[0]

    confidence = max(probabilities)

    return prediction, confidence