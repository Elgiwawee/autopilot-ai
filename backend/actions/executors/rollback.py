# actions/executors/rollback.py

def rollback_execution(execution, aws_client):
    payload = execution.rollback_payload

    aws_client.start_instances(
        InstanceIds=[payload["instance_id"]]
    )

    execution.state = "ROLLED_BACK"
    execution.finished_at = now()
    execution.save()
