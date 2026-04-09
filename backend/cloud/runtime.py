# cloud/runtime.py

from cloud.providers.factory import get_provider
from cloud.control_planes.kubernetes import KubernetesControlPlane


def get_runtime_handler(target):
    """
    Unified runtime resolver.
    """

    # ✅ Kubernetes path
    if getattr(target, "is_kubernetes", False):
        return KubernetesControlPlane(target)

    # ✅ Cloud provider path
    return get_provider(target)