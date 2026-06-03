# cloud/kubernetes_engine/tasks/metrics.py

from celery import shared_task
from cloud.kubernetes_engine.client import KubernetesClient
from cloud.kubernetes_engine.metrics import (
    extract_requests,
    extract_usage,
)
from cloud.kubernetes_engine.models import PodMetrics

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 5},
)
def collect_pod_metrics(self, cloud_account_id, cluster_id):
    k8s = KubernetesClient()

    for ns in k8s.core.list_namespace().items:
        namespace = ns.metadata.name
        pods = k8s.core.list_namespaced_pod(namespace).items

        metrics = k8s.custom.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods",
        )

        usage_map = {
            m["metadata"]["name"]: extract_usage(m)
            for m in metrics.get("items", [])
        }

        for pod in pods:
            cpu_req, mem_req = extract_requests(pod)
            cpu_use, mem_use = usage_map.get(pod.metadata.name, (0, 0))

            PodMetrics.objects.update_or_create(
                cloud_account_id=cloud_account_id,
                cluster_id=cluster_id,
                namespace=namespace,
                pod=pod.metadata.name,
                defaults={
                    "cpu_request": cpu_req,
                    "cpu_usage_p95": cpu_use,
                    "memory_request": mem_req,
                    "memory_usage_p95": mem_use,
                    "sample_window": 1,
                },
            )
