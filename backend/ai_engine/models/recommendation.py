from django.db import models

class Recommendation(models.Model):
    resource = models.ForeignKey(
        "cloud.CloudResource", on_delete=models.CASCADE
    )
    recommendation_type = models.CharField(max_length=64)
    expected_monthly_savings = models.DecimalField(
        max_digits=10, decimal_places=2
    )
    confidence = models.FloatField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
