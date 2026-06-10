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
            {
                "instance_factor": 0.5,
                "memory_factor": 0.5,
            },
            {
                "instance_factor": 0.75,
                "memory_factor": 0.75,
            },
            {
                "spot_candidate": True,
            },
            {
                "gp3_conversion": True,
            },
        ]

        parameters = random.choice(mutations)

        strategy = OptimizationStrategy.objects.create(
            name=(
                f"{action_type}_"
                f"{resource_type}_"
                f"{random.randint(100000,999999)}"
            ),
            action_type=action_type,
            resource_type=resource_type,
            parameters=parameters,
        )

        return strategy