# ai_engine/tasks/k8s_analysis.py

from celery import shared_task
from cloud.kubernetes_engine.models import PodMetrics
from cloud.kubernetes_engine.recommender import generate_recommendations
from cloud.models import CloudResource
from actions.models import ExecutionPlan

@shared_task
def analyze_k8s_resources(cluster_id):
    metrics = PodMetrics.objects.filter(cluster_id=cluster_id)

    for m in metrics:
        recs = generate_recommendations({
            "resource_type": "pod",
            "cpu_p95": m.cpu_usage_p95_millicores,
            "memory_p95": m.memory_usage_p95_mb,
            "stability": 0.9,
        })

        for rec in recs:

            resource = CloudResource.objects.filter(
                external_id=m.workload_name
            ).first()

            if not resource:
                continue

            ExecutionPlan.objects.create(
                resource=resource,
                cloud_account=resource.cloud_account,
                organization=resource.cloud_account.organization,
                action=rec["type"],
                confidence=rec["confidence"],
                risk_score=rec["risk_score"],
                status="planned",
            )
