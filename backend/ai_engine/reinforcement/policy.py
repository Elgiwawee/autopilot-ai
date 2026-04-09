# ai_engine/reinforcement/policy.py

import random
from ai_engine.models.action_learning import ActionLearning


class OptimizationPolicy:

    def should_execute(
        self,
        action,
        risk_score,
        estimated_savings,
    ):

        # hard safety checks
        if risk_score > 0.7:
            return False

        if estimated_savings < 5:
            return False

        # retrieve learning stats
        try:
            stats = ActionLearning.objects.get(action=action)
        except ActionLearning.DoesNotExist:
            return True  # allow first execution

        # avoid bad strategies
        if stats.avg_reward < -1:
            return False

        # exploration logic
        if random.random() < stats.exploration_rate:
            return True

        return stats.avg_reward >= 0