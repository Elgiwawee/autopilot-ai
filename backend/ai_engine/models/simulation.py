from django.db import models


class SimulationResult(models.Model):
    """
    Stores AI prediction results before executing an optimization.
    """

    action = models.CharField(max_length=100)

    resource_type = models.CharField(max_length=100)

    predicted_savings = models.FloatField()

    predicted_risk = models.FloatField()

    confidence = models.FloatField(default=0.5)

    parameters = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)