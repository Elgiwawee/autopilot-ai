# actions/executors/ec2.py

from django.utils.timezone import now
from audit.services.writer import write_audit_log

def execute_stop(execution, aws_client):
    execution.state = "EXECUTING"
    execution.started_at = now()
    execution.save()

    try:
        aws_client.stop_instances(
            InstanceIds=[execution.rollback_payload["instance_id"]]
        )

        execution.after_state = fetch_instance_state(...)
        execution.state = "VERIFIED"

    except Exception as e:
        execution.error = str(e)
        execution.state = "FAILED"

    execution.save()



    write_audit_log(
        organization=execution.optimization.cloud_account.organization,
        actor="AUTOPILOT",
        action=execution.optimization.action_type,
        resource_id=execution.optimization.resource_id,
        status="SUCCESS",
        metadata={
            "cloud": execution.optimization.cloud_account.provider.code,
        },
    )
