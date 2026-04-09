# ai_engine/autopilot/circuit_breaker.py

from django.core.cache import cache

FAIL_LIMIT = 5
WINDOW_SECONDS = 300  # 5 min


def _key(org_id):
    return f"autopilot:failures:{org_id}"


def record_failure(org_id):
    key = _key(org_id)
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=WINDOW_SECONDS)


def reset_failures(org_id):
    cache.delete(_key(org_id))


def circuit_breaker_open(org_id):
    return cache.get(_key(org_id), 0) >= FAIL_LIMIT