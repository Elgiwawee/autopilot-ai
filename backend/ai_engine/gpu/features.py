# ai_engine/gpu/features.pyS

import numpy as np


def extract_features(metrics):
    """
    Build ML features from GPU metrics.

    Returns:

    [
        mean_utilization,
        p95_utilization,
        std_dev,
        min_utilization,
        max_utilization,
        mean_memory_percent,
        sample_count,
    ]
    """

    if not metrics:
        return [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

    utilizations = [
        float(m.utilization)
        for m in metrics
    ]

    memory_percent = []

    for m in metrics:

        if m.mem_total:

            memory_percent.append(
                (
                    m.mem_used /
                    m.mem_total
                ) * 100
            )

    return [

        np.mean(utilizations),

        np.percentile(
            utilizations,
            95,
        ),

        np.std(utilizations),

        np.min(utilizations),

        np.max(utilizations),

        np.mean(memory_percent)
        if memory_percent
        else 0,

        len(metrics),
    ]