# cloud/kubernetes_engine/profiler.py

import numpy as np

def compute_p95(samples):
    return np.percentile(samples, 95)


def profile_pod(cpu_samples, mem_samples):
    return {
        "cpu_p95": compute_p95(cpu_samples),
        "memory_p95": compute_p95(mem_samples),
        "stability": 1 - (np.std(cpu_samples) / max(cpu_samples)),
    }
