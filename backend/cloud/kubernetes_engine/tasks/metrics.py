# cloud/kubernetes_engine/tasks/metrics.py

from celery import shared_task
from django.db import transaction
from kubernetes.client.exceptions import ApiException
from cloud.kubernetes_engine.models import KubernetesCluster, PodMetrics
from cloud.kubernetes_engine.client import KubernetesClient
from cloud.kubernetes_engine.metrics import (
    extract_requests,
    extract_usage,
)


@shared_task
def collect_all_cluster_metrics():
    """
    Wrapper task executed by Celery Beat.
    Discovers every connected Kubernetes cluster and
    queues an individual metrics collection task.
    """

    clusters = (
        KubernetesCluster.objects
        .select_related("cloud_account")
        .filter(is_active=True)
    )

    for cluster in clusters:
        collect_pod_metrics.delay(
            cluster.cloud_account.id,
            cluster.id,
        )


@shared_task(
    bind=True,
    autoretry_for=(ApiException,ConnectionError,TimeoutError,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 5},
)
def collect_pod_metrics(self, cloud_account_id, cluster_id):
    """
    Collect metrics for one Kubernetes cluster.
    """

    cluster = (
        KubernetesCluster.objects
        .select_related("cloud_account")
        .filter(
            id=cluster_id,
            cloud_account_id=cloud_account_id,
            is_active=True,
        )
        .first()
    )

    if cluster is None:
        return
    # If your KubernetesClient accepts a cluster, pass it here.
    # Otherwise adapt this constructor to your implementation.
    k8s = KubernetesClient(cluster=cluster)

    namespaces = k8s.core.list_namespace().items

    for ns in namespaces:
        namespace = ns.metadata.name

        pods = k8s.core.list_namespaced_pod(namespace).items

        try:
            metrics = k8s.custom.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
            )

            usage_map = {
                item["metadata"]["name"]: extract_usage(item)
                for item in metrics.get("items", [])
            }

        except Exception:
            usage_map = {}

        with transaction.atomic():
            for pod in pods:
                cpu_req, mem_req = extract_requests(pod)
                cpu_use, mem_use = usage_map.get(
                    pod.metadata.name,
                    (0, 0),
                )

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