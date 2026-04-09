# cloud/kubernetes_engine/observer.py

def observe_canary(
    *,
    metrics_before: dict,
    metrics_after: dict,
    policy,
):
    """
    Returns a deterministic verdict.
    NO side effects.
    """

    baseline_errors = metrics_before.get("errors", 0)
    current_errors = metrics_after.get("errors", 0)

    baseline_latency = metrics_before.get("latency_ms", 0)
    current_latency = metrics_after.get("latency_ms", 0)

    error_rate_increase = (
        (current_errors - baseline_errors) / max(baseline_errors, 1)
    )

    latency_increase = (
        (current_latency - baseline_latency) / max(baseline_latency, 1)
    )

    if error_rate_increase > policy.max_error_increase:
        return {
            "success": False,
            "reason": "Error rate regression",
            "error_rate_increase": error_rate_increase,
            "latency_increase": latency_increase,
        }

    if latency_increase > policy.max_latency_increase:
        return {
            "success": False,
            "reason": "Latency regression",
            "error_rate_increase": error_rate_increase,
            "latency_increase": latency_increase,
        }

    return {
        "success": True,
        "reason": "Canary healthy",
        "error_rate_increase": error_rate_increase,
        "latency_increase": latency_increase,
    }
