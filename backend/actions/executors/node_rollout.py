# actions/executors/node_rollout.py

import time
from kubernetes.client import V1Eviction
from kubernetes.client.rest import ApiException

ROLL_OUT_TIMEOUT = 1800  # 30 minutes
CHECK_INTERVAL = 10      # seconds
MAX_UNAVAILABLE_NODES = 1


def safe_nodegroup_migration(
    *,
    k8s,
    old_nodegroup: str,
    new_nodegroup: str,
    namespace_blacklist=None,
):
    """
    Safely migrate workloads from old nodegroup to new one.
    """

    namespace_blacklist = namespace_blacklist or ["kube-system"]

    def create_nodegroup(nodegroup_name):
        """
        Delegates to cloud provider (EKS / GKE / AKS).
        """
        # This should call your CloudProvider.execute_action(...)
        print(f"[+] Creating nodegroup: {nodegroup_name}")

    
    def wait_for_nodegroup_ready(k8s, nodegroup):
        start = time.time()

        while time.time() - start < ROLL_OUT_TIMEOUT:
            nodes = get_nodes_by_group(k8s, nodegroup)

            if nodes and all(is_node_ready(n) for n in nodes):
                return

            time.sleep(CHECK_INTERVAL)

        raise TimeoutError("New nodegroup did not become ready in time")


def get_nodes_by_group(k8s, nodegroup):
    nodes = k8s.core.list_node().items

    return [
        n for n in nodes
        if n.metadata.labels.get("nodegroup") == nodegroup
    ]


def is_node_ready(node):
    for cond in node.status.conditions:
        if cond.type == "Ready" and cond.status == "True":
            return True
    return False


def cordon_nodes(k8s, nodes):
    for node in nodes:
        body = {"spec": {"unschedulable": True}}
        k8s.core.patch_node(node.metadata.name, body)


def drain_nodes_safely(
    k8s,
    nodes,
    namespace_blacklist,
):
    for node in nodes:
        drain_single_node(
            k8s,
            node.metadata.name,
            namespace_blacklist,
        )


def drain_single_node(k8s, node_name, namespace_blacklist):
    pods = k8s.core.list_pod_for_all_namespaces(
        field_selector=f"spec.nodeName={node_name}"
    ).items

    evictable = [
        p for p in pods
        if p.metadata.namespace not in namespace_blacklist
        and not is_mirror_pod(p)
        and not is_daemonset_pod(p)
    ]

    if len(evictable) > MAX_UNAVAILABLE_NODES:
        evictable = evictable[:MAX_UNAVAILABLE_NODES]

    for pod in evictable:
        evict_pod(k8s, pod)

    wait_for_pods_gone(k8s, node_name)


def is_daemonset_pod(pod):
    owners = pod.metadata.owner_references or []
    return any(o.kind == "DaemonSet" for o in owners)


def is_mirror_pod(pod):
    return "kubernetes.io/config.mirror" in (
        pod.metadata.annotations or {}
    )


def evict_pod(k8s, pod):
    eviction = V1Eviction(
        metadata={"name": pod.metadata.name, "namespace": pod.metadata.namespace}
    )

    try:
        k8s.core.create_namespaced_pod_eviction(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            body=eviction,
        )
    except ApiException as e:
        if e.status != 404:
            raise


def wait_for_pods_gone(k8s, node_name):
    start = time.time()

    while time.time() - start < ROLL_OUT_TIMEOUT:
        pods = k8s.core.list_pod_for_all_namespaces(
            field_selector=f"spec.nodeName={node_name}"
        ).items

        if not pods:
            return

        time.sleep(CHECK_INTERVAL)

    raise TimeoutError(f"Node {node_name} did not drain in time")


def verify_cluster_health(k8s):
    pods = k8s.core.list_pod_for_all_namespaces().items

    failed = [
        p for p in pods
        if p.status.phase not in ("Running", "Succeeded")
    ]

    if failed:
        raise RuntimeError("Cluster health degraded after node migration")


def delete_nodegroup(nodegroup):
    print(f"[✓] Deleting old nodegroup: {nodegroup}")
