# ai_engine/reinforcement/reward_engine.py

from billing.models import SavingsEvent


def compute_reward(action_id):
    """
    Compute reinforcement reward using actual savings.
    """

    event = (
        SavingsEvent.objects
        .filter(action_id=action_id)
        .order_by("-occurred_at")
        .first()
    )

    if not event:
        return -0.2  # no savings → small penalty

    savings = float(event.savings_amount)

    confidence_bonus = event.confidence * 0.1

    reward = (savings / 100) + confidence_bonus

    return reward