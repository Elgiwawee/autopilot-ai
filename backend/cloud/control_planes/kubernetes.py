# cloud/control_planes/kubernetes.py
from cloud.control_planes.base import ControlPlane


class KubernetesControlPlane(ControlPlane):

    def __init__(self, resource):
        self.resource = resource
        self.client = self._build_client()

    def _build_client(self):
        # TODO: implement kube auth
        return {}

    def execute_action(self, action):
        # route action types
        return action.execute(self)