# actions/execution/services/runner.py

from cloud.executors.factory import get_cloud_executor
from cloud.kubernetes_engine.tasks.execution import execute_k8s_rightsizing


def run_execution(plan, decision):
    resource = plan.resource

    # ✅ KUBERNETES PATH
    if resource.resource_type in ["pod", "node", "cluster"]:
        execute_k8s_rightsizing.delay(plan.execution_record_id)
        return

    # ✅ DEFAULT CLOUD EXECUTION
    executor = get_cloud_executor(plan.cloud_account)

    executor.execute(
        target_type=plan.resource_type,
        namespace=plan.namespace,
        target_name=plan.resource_id,
        action=plan.action_type,
        parameters=plan.parameters,
    )