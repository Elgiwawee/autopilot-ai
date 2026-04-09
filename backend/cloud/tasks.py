# cloud/tasks.py

from celery import shared_task
from cloud.collectors.aws_ec2 import collect_ec2_instances
from cloud.models import CloudAccount


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10)
def collect_aws_ec2_task(self):

    accounts = CloudAccount.objects.filter(provider="aws")

    for account in accounts:
        collect_ec2_instances(account.id)

