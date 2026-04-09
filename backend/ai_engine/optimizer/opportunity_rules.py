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

            # Detect underutilized instance
            if avg_cpu < 15:

                opportunities.append({
                    "resource_id": m["resource_id"],
                    "resource_type": "compute",
                    "action_type": "RESIZE_INSTANCE",
                    "estimated_savings": 50,
                })

        return opportunities