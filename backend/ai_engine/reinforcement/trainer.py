# ai_engine/reinforcement/trainer.py

from ai_engine.reinforcement.reward_engine import compute_reward
from ai_engine.models.action_learning import ActionLearning
from ai_engine.models.strategy import OptimizationStrategy
from ai_engine.optimizer.strategy_generator import StrategyGenerator

class RLTrainer:

    def update(self, action_id):

        reward = compute_reward(action_id)

        obj, _ = ActionLearning.objects.get_or_create(
            action=action_id
        )

        obj.update_reward(reward)

        # =============================
        # 🔥 STRATEGY EVOLUTION
        # =============================
        if reward > 3:
            StrategyGenerator().generate_from_success(
                action_type=action_id,
                resource_type="compute"
            )

        return {
            "reward": reward,
            "avg_reward": obj.avg_reward,
            "exploration_rate": obj.exploration_rate,
        }