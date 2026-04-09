# ai_engine/resize_rules.py

def resize_safe(resource, utilization):
    cpu_avg = utilization.get("cpu_avg")
    cpu_max = utilization.get("cpu_max")

    if cpu_avg is None:
        return False, "No CPU data"

    if cpu_max and cpu_max > 70:
        return False, "High CPU spikes"

    if cpu_avg > 35:
        return False, "CPU too high"

    # optional safety
    if hasattr(resource, "uptime_hours") and resource.uptime_hours < 24:
        return False, "Instance too new"

    return True, "Safe to downsize"