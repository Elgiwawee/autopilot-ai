# ai_engine/recommendations.py

from ai_engine.models.recommendation import Recommendation
from ai_engine.idle_detection import detect_idle_ec2_instances


def generate_idle_ec2_recommendations():
    idle_instances = detect_idle_ec2_instances()

    for resource in idle_instances:
        monthly_savings = resource.cost_per_hour * 24 * 30

        Recommendation.objects.create(
            resource=resource,
            recommendation_type="stop_instance",
            expected_monthly_savings=monthly_savings,
            confidence=0.85,
            explanation=(
                "Instance has averaged less than 5% CPU utilization "
                "over the last 14 days."
            ),
        )
