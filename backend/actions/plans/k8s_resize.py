# actions/plans/k8s_resize.py

from actions.models import ActionPlan

def generate_resize_plan(workload, new_cpu, new_mem):
    return ActionPlan.objects.create(
        resource_type="k8s_workload",
        resource_id=workload.id,
        action_type="resize_requests",
        estimated_savings=calculate_k8s_savings(workload, new_cpu, new_mem),
        risk_level="low",
        is_safe=True,
        explanation=(
            f"Observed p95 CPU usage is {new_cpu/1.3:.2f} cores. "
            f"Requests reduced with 30% headroom."
        ),
    )
