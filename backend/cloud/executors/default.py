from cloud.providers.factory import get_provider


class DefaultExecutor:

    def __init__(self, cloud_account):
        self.provider = get_provider(cloud_account)

    def execute(self, action):
        self.provider.execute_action(action)

    def rollback(self, action):
        self.provider.rollback(action)