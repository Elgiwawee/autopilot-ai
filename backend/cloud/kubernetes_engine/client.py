# cloud/kubernetes_engine/client.py

import os
import tempfile

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


class KubernetesClient:
    """
    Production Kubernetes client.

    Supports:
        • Customer clusters (kubeconfig stored in DB)
        • Explicit kubeconfig path
        • Running inside Kubernetes
        • Local development (~/.kube/config)
    """

    def __init__(self, cluster=None, kubeconfig_path=None):
        self._temp_file = None

        try:

            # -------------------------------------------------
            # Explicit kubeconfig file
            # -------------------------------------------------
            if kubeconfig_path:
                config.load_kube_config(
                    config_file=kubeconfig_path
                )

            # -------------------------------------------------
            # Customer cluster
            # -------------------------------------------------
            elif cluster and cluster.kubeconfig:

                self._temp_file = tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".yaml",
                    delete=False,
                )

                self._temp_file.write(cluster.kubeconfig)
                self._temp_file.flush()

                config.load_kube_config(
                    config_file=self._temp_file.name
                )

            # -------------------------------------------------
            # Autopilot running inside Kubernetes
            # -------------------------------------------------
            else:
                try:
                    config.load_incluster_config()

                # -------------------------------------------------
                # Local development fallback
                # -------------------------------------------------
                except ConfigException:
                    config.load_kube_config()

            self.core = client.CoreV1Api()
            self.apps = client.AppsV1Api()
            self.batch = client.BatchV1Api()
            self.networking = client.NetworkingV1Api()
            self.storage = client.StorageV1Api()
            self.custom = client.CustomObjectsApi()

        finally:

            if self._temp_file:
                self._temp_file.close()

                try:
                    os.remove(self._temp_file.name)
                except FileNotFoundError:
                    pass