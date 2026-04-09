# ai_engine/optimizer/strategy_selector.py

import random

from ai_engine.models.strategy import OptimizationStrategy


class StrategySelector:

    def select_strategy(self, resource_type):

        strategies = OptimizationStrategy.objects.filter(
            resource_type=resource_type,
            enabled=True
        )

        if not strategies.exists():
            return None

        # prioritize highest reward
        strategies = strategies.order_by("-avg_reward")

        # exploration
        if random.random() < 0.15:
            return random.choice(list(strategies))

        return strategies.first()