# ai_engine/optimizer/strategy_selector.py

import random

from ai_engine.models.strategy import OptimizationStrategy


class StrategySelector:

    def select_strategy(self, resource_type):

        strategies = list(
            OptimizationStrategy.objects.filter(
                resource_type=resource_type,
                enabled=True,
                avg_reward__gte=0,
            ).order_by("-avg_reward")
        )

        if not strategies:
            return None

        # 15% exploration
        if random.random() < 0.15:
            return random.choice(strategies)

        # 85% exploitation (best known strategy)
        return strategies[0]