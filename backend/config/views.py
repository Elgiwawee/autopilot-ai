# config/views.py

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """
    Kubernetes health endpoint.
    Verifies:
      - Django is running
      - PostgreSQL is reachable
      - Redis is reachable
    """

    db_status = "ok"
    redis_status = "ok"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception:
        db_status = "error"

    try:
        cache.set("health_check", "ok", timeout=5)
        cache.get("health_check")
    except Exception:
        redis_status = "error"

    overall = (
        "healthy"
        if db_status == "ok" and redis_status == "ok"
        else "unhealthy"
    )

    status_code = 200 if overall == "healthy" else 503

    return JsonResponse(
        {
            "status": overall,
            "database": db_status,
            "redis": redis_status,
        },
        status=status_code,
    )