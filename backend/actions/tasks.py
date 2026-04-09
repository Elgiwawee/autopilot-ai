# actions/tasks.py

from celery import shared_task
from django.utils.timezone import now

from cloud.models import CloudAccount
from actions.models import ActionExecution

from ai_engine.tasks.detector_tasks import scan_cloud_for_opportunities

from actions.executors.aws_ec2 import stop_ec2_instance

from cloud.tasks import collect_aws_ec2_task


@shared_task
def run_optimizer_scan():
    accounts = CloudAccount.objects.filter(is_active=True)

    for acc in accounts:

        if acc.provider.code == "aws":
            collect_aws_ec2_task.delay(acc.id)  # 🚀 async

        scan_cloud_for_opportunities.delay(acc.id)


# -----------------------------------
# 🔥 2. EXECUTION TASK
# -----------------------------------
@shared_task(bind=True, max_retries=3)
def execute_action(self, action_execution_id):
    execution = ActionExecution.objects.get(id=action_execution_id)
    opt = execution.action_plan

    execution.status = "executing"
    execution.save()

    try:
        # 🔥 ACTION ROUTER
        if opt.action_type == "TERMINATE":
            stop_ec2_instance(
                opt.resource_id,
                credentials=opt.cloud_account.credentials  # adapt this
            )

        # future:
        # elif opt.action_type == "RIGHTSIZE": ...
        # elif opt.action_type == "SPOT": ...

        execution.status = "success"
        execution.executed_at = now()
        execution.save()

    except Exception as e:
        execution.status = "failed"
        execution.error_message = str(e)
        execution.save()
        raise