# cloud/kubernetes_engine/recommender.py

def recommend_resources(metrics):
    cpu = max(metrics["cpu_p95"] * 1.25, 0.1)
    memory = max(metrics["memory_p95"] * 1.30, 128)

    return {
        "type": "resize_pod",
        "cpu": round(cpu, 2),
        "memory": int(memory),
        "risk_score": 0.15,
        "confidence": metrics["stability"],
    }



def recommend_gpu(metrics):
    recommendations = []

    mem_ratio = (
        metrics.gpu_memory_used_mb_p95
        / metrics.gpu_memory_requested_mb
    )

    if metrics.gpu_utilization_p95 < 30 and mem_ratio < 0.5:
        recommendations.append({
            "type": "scale_down_gpu_node",
            "risk_score": 0.25,
            "confidence": 0.8,
        })

    if mem_ratio < 0.55:
        recommendations.append({
            "type": "reduce_gpu_memory_request",
            "risk_score": 0.1,
            "confidence": 0.9,
        })

    return recommendations


def generate_recommendations(metrics):
    recs = []

    if metrics["resource_type"] == "pod":
        recs.append(recommend_resources(metrics))

    if metrics["resource_type"] == "gpu":
        recs.extend(recommend_gpu(metrics))

    return recs
