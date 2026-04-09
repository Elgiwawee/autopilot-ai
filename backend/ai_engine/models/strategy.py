from django.db import models


class OptimizationStrategy(models.Model):
    """
    Represents a learned optimization strategy.
    """

    name = models.CharField(max_length=200)

    action_type = models.CharField(max_length=100)

    resource_type = models.CharField(max_length=100)

    parameters = models.JSONField(default=dict)

    success_rate = models.FloatField(default=0)

    avg_reward = models.FloatField(default=0)

    executions = models.IntegerField(default=0)

    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def update_metrics(self, reward: float):

        self.executions += 1

        self.avg_reward = (
            (self.avg_reward * (self.executions - 1)) + reward
        ) / self.executions

        if reward > 0:
            success = 1
        else:
            success = 0

        self.success_rate = (
            (self.success_rate * (self.executions - 1)) + success
        ) / self.executions

        self.save(
            update_fields=[
                "executions",
                "avg_reward",
                "success_rate",
                "updated_at",
            ]
        )