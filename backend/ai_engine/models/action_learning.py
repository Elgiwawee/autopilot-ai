from django.db import models


class ActionLearning(models.Model):
    """
    Stores reinforcement learning statistics per action type.
    """

    action = models.CharField(max_length=100, unique=True)

    executions = models.IntegerField(default=0)

    total_reward = models.FloatField(default=0)

    avg_reward = models.FloatField(default=0)

    exploration_rate = models.FloatField(default=0.1)

    updated_at = models.DateTimeField(auto_now=True)

    def update_reward(self, reward: float):

        self.executions += 1
        self.total_reward += reward
        self.avg_reward = self.total_reward / self.executions

        # adjust exploration dynamically
        if self.avg_reward > 2:
            self.exploration_rate = 0.05
        elif self.avg_reward < 0:
            self.exploration_rate = 0.25
        else:
            self.exploration_rate = 0.1

        self.save(update_fields=[
            "executions",
            "total_reward",
            "avg_reward",
            "exploration_rate",
            "updated_at",
        ])