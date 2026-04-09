# cloud/kubernetes_engine/canary.py

def canary_patch(
    k8s,
    deployment,
    new_resources,
    ratio=0.2,
):
    replicas = deployment.spec.replicas or 1
    canary_replicas = max(1, int(replicas * ratio))

    containers_patch = []

    for c in deployment.spec.template.spec.containers:
        containers_patch.append({
            "name": c.name,
            "resources": {
                "requests": new_resources,
                "limits": new_resources,
            },
        })

    patch = {
        "spec": {
            "replicas": canary_replicas,
            "template": {
                "spec": {
                    "containers": containers_patch
                }
            }
        }
    }

    k8s.apps.patch_namespaced_deployment(
        name=deployment.metadata.name,
        namespace=deployment.metadata.namespace,
        body=patch,
    )
