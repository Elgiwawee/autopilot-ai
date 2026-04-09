# actions/services/optimizer.py

from actions.models import OptimizationPlan


def list_optimizations(organization, cloud=None):
    qs = OptimizationPlan.objects.filter(
        cloud_account__organization=organization,
        status="PLANNED",
    ).select_related("cloud_account")

    if cloud:
        qs = qs.filter(cloud_account__provider=cloud)

    results = []

    for opt in qs:
        # 🔥 Human readable mapping
        title = build_title(opt)
        description = build_description(opt)

        results.append({
            "id": str(opt.id),

            # ✅ UI FRIENDLY
            "title": title,
            "description": description,
            "resource": f"{opt.resource_type} ({opt.resource_id})",
            "savings": float(opt.estimated_monthly_savings),

            # ✅ EXTRA DATA (future use)
            "cloud": opt.cloud_account.provider,
            "action": opt.action_type,
            "confidence": opt.confidence,
            "status": opt.status,
        })

    return results


# -----------------------------
# HELPERS (VERY IMPORTANT)
# -----------------------------

def build_title(opt):
    if opt.action_type == "TERMINATE":
        return "Terminate idle resource"
    elif opt.action_type == "RIGHTSIZE":
        return "Rightsize resource"
    elif opt.action_type == "SPOT":
        return "Switch to spot instance"
    return "Optimization recommendation"


def build_description(opt):
    if opt.action_type == "TERMINATE":
        return f"{opt.resource_type} appears idle and can be safely terminated"
    elif opt.action_type == "RIGHTSIZE":
        return f"{opt.resource_type} is over-provisioned and can be downsized"
    elif opt.action_type == "SPOT":
        return f"Move {opt.resource_type} to spot instance to reduce cost"
    return "Optimization available"