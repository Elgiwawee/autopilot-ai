from cloud.executors.factory import get_cloud_executor


class DefaultExecutor:
    """
    Backwards-compatible wrapper.

    Prefer get_cloud_executor(cloud_account) directly.
    """

    def __init__(self, cloud_account):
        self.executor = get_cloud_executor(cloud_account)

    def execute(self, action, **kwargs):
        return self.executor.execute(action=action, **kwargs)

    def rollback(self, action, **kwargs):
        return self.executor.rollback(action=action, **kwargs)