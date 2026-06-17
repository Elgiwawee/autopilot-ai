# actions/executors/k8s_patch.py

def patch_requests(api, workload, cpu, mem):
    body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": workload.name,
                        "resources": {
                            "requests": {
                                "cpu": f"{cpu}",
                                "memory": f"{mem}Mi"
                            }
                        }
                    }]
                }
            }
        }
    }

    api.patch_namespaced_deployment(
        name=workload.name,
        namespace=workload.namespace,
        body=body
    )
