# cloud/control_planes/factory.py

from cloud.control_planes.kubernetes import KubernetesControlPlane


def get_control_plane(resource):
    if not resource:
        return None

    if resource.resource_type in ["eks", "gke", "aks"]:
        return KubernetesControlPlane(resource)

    return None