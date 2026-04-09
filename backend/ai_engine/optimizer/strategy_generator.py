# ai_engine/optimizer/strategy_generator.py

import random

from ai_engine.models.strategy import OptimizationStrategy


class StrategyGenerator:
    """
    Generates new optimization strategies based on past successes.
    """

    def generate_from_success(self, action_type, resource_type):

        # small mutation variations
        mutations = [
            {"cpu_reduction": 1},
            {"cpu_reduction": 2},
            {"memory_reduction": "10%"},
            {"memory_reduction": "20%"},
        ]

        parameters = random.choice(mutations)

        strategy = OptimizationStrategy.objects.create(
            name=f"{action_type}_{resource_type}_variant",
            action_type=action_type,
            resource_type=resource_type,
            parameters=parameters,
        )

        return strategy