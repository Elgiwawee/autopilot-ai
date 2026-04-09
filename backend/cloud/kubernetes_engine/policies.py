#

from django.apps import apps
from audit.services.writer import write_audit_log

class PolicyViolation(Exception):
    pass



def get_models():
    Policy = apps.get_model("actions", "Policy")
    PolicyDecision = apps.get_model("actions", "PolicyDecision")
    return Policy, PolicyDecision


def policy_allows(action, policy):
    rules = policy.rules or {}

    if action.risk_score > rules.get("max_risk", 1.0):
        return False

    if action.type not in rules.get("allowed_actions", []):
        return False

    if action.replicas < rules.get("min_replicas", 1):
        return False

    return True



def policy_matches(plan, policy):
    scope = policy.scope or {}

    if "namespace" in scope:
        if (
            plan.namespace not in scope["namespace"]
            and "*" not in scope["namespace"]
        ):
            return False

    if "cluster_id" in scope:
        if plan.cluster_id not in scope["cluster_id"]:
            return False

    if "environment" in scope:
        if plan.environment not in scope["environment"]:
            return False

    return True



def enforce_policies(plan):
    Policy, PolicyDecision = get_models()

    policies = Policy.objects.filter(
        cloud_account=plan.cloud_account,
        enabled=True
    )

    for policy in policies:
        if not policy_matches(plan, policy):
            continue

        allowed = policy_allows(plan, policy)

        PolicyDecision.objects.create(
            execution_plan=plan,
            policy=policy,
            decision="allow" if allowed else "deny",
            reason="passed" if allowed else "policy rule violation",
        )

        if not allowed:
            write_audit_log(
                organization=plan.cloud_account.organization,
                actor="POLICY_ENGINE",
                action=plan.action_type,
                resource_id=plan.resource_id,
                status="DENIED",
                metadata={"policy_id": policy.id},
            )
            raise PolicyViolation(
                f"Execution blocked by policy: {policy.name or policy.id}"
            )
