from sklearn.ensemble import RandomForestClassifier


model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
)


def train_gpu_model(X, y):
    """
    Train GPU optimization model.
    """

    model.fit(X, y)

    return model


def gpu_action_decision(
    prediction,
    p95,
):
    """
    Translate ML prediction into
    optimization action.
    """

    if prediction == "OVERPROVISIONED":

        if p95 < 20:
            return "TERMINATE"

        if p95 < 40:
            return "DOWNGRADE_GPU"

    if prediction == "UNDERPROVISIONED":
        return "UPGRADE_GPU"

    return "NO_ACTION"