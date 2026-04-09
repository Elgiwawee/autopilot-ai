# cloud/services/gpu_metrics.py

from datetime import timedelta, date
from cloud.providers.factory import get_provider


def get_gpu_utilization(cloud_account, resource_ids):
    provider = get_provider(cloud_account)

    end = date.today()
    start = end - timedelta(days=1)

    metrics = provider.fetch_metrics(
        resource_ids=resource_ids,
        metric_name="CPUUtilization",
        start_date=start,
        end_date=end,
    )

    utilization = {}

    for m in metrics:
        rid = m.get("resource_id")

        # 🔥 HANDLE MULTI-PROVIDER FORMATS
        datapoints = m.get("datapoints") or m.get("metrics") or []

        values = []

        for p in datapoints:
            if isinstance(p, dict):
                if "value" in p:
                    values.append(p["value"])
                elif "Average" in p:
                    values.append(p["Average"])
            else:
                # Azure metric objects
                try:
                    values.append(p.average)
                except Exception:
                    continue

        utilization[rid] = (
            sum(values) / len(values) if values else 0
        )

    return utilization
