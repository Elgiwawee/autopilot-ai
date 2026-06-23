# actions/services/optimizer.py

from actions.models import ExecutionPlan


def list_optimizations(organization, cloud=None, status=None):
    qs = ExecutionPlan.objects.filter(
        cloud_account__organization=organization
    ).select_related(
        "cloud_account",
        "cloud_account__provider",
        "resource",
    ).order_by("-created_at")

    if status:
        qs = qs.filter(status=status)

    if cloud:
        qs = qs.filter(
            cloud_account__provider__code=cloud
        )

    results = []

    for opt in qs:
        title = build_title(opt)
        description = build_description(opt)

        resource_name = getattr(opt.resource, "name", None)
        resource_label = (
            resource_name
            or opt.target_name
            or opt.provider_resource_id
            or ""
        )

        results.append({
            "id": str(opt.id),
            "title": title,
            "description": description,
            "resource": f"{opt.resource_type} ({resource_label})",
            "savings": float(opt.estimated_monthly_savings or 0),
            "cloud": opt.cloud_account.provider.code,
            "action": opt.action,
            "confidence": float(opt.confidence or 0),
            "status": opt.status,
        })

    return results


def build_title(opt):
    action = (opt.action or "").upper()

    if action == "TERMINATE":
        return "Terminate idle resource"
    if action == "RIGHTSIZE":
        return "Rightsize resource"
    if action == "SPOT":
        return "Switch to spot instance"
    if action == "RECOMMEND":
        return "Recommendation only"

    return "Optimization recommendation"


def build_description(opt):
    action = (opt.action or "").upper()

    if action == "TERMINATE":
        return f"{opt.resource_type} appears idle and can be safely terminated"
    if action == "RIGHTSIZE":
        return f"{opt.resource_type} is over-provisioned and can be downsized"
    if action == "SPOT":
        return f"Move {opt.resource_type} to spot instance to reduce cost"
    if action == "RECOMMEND":
        return "This is an informational recommendation only"

    return "Optimization available"