from actions.models import (
    OptimizationPlan,
    ExecutionPlan,
)

for opt in OptimizationPlan.objects.all():

    if ExecutionPlan.objects.filter(
        legacy_optimization_id=opt.id
    ).exists():
        continue

    ExecutionPlan.objects.create(
        legacy_optimization_id=opt.id,

        cloud_account=opt.cloud_account,

        resource_type=opt.resource_type,

        provider_resource_id=opt.resource_id,

        action=opt.action_type,

        current_state=opt.current_state,

        proposed_state=opt.proposed_state,

        estimated_monthly_savings=opt.estimated_monthly_savings,

        confidence=opt.confidence,

        status=opt.status.lower(),

        created_at=opt.created_at,
    )