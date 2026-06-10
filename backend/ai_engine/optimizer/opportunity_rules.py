# ai_engine/optimizer/opportunity_rules.py

class OpportunityRules:
    """
    Detect inefficiencies using real monitoring metrics.
    """

    def detect_compute_opportunities(self, metrics):

        opportunities = []

        for m in metrics:

            values = m["values"]

            if not values:
                continue

            avg_cpu = sum(values) / len(values)

            # Very underutilized -> terminate candidate
            if avg_cpu < 5:

                opportunities.append({
                    "resource_id": m["resource_id"],
                    "resource_type": "compute",
                    "action_type": "TERMINATE",
                    "estimated_savings": 100,
                })

            # Moderately underutilized -> rightsize
            elif avg_cpu < 20:

                opportunities.append({
                    "resource_id": m["resource_id"],
                    "resource_type": "compute",
                    "action_type": "RIGHTSIZE",
                    "estimated_savings": 50,
                })

            # High utilization -> recommend scale review
            elif avg_cpu > 85:

                opportunities.append({
                    "resource_id": m["resource_id"],
                    "resource_type": "compute",
                    "action_type": "RECOMMEND",
                    "estimated_savings": 0,
                })

        return opportunities