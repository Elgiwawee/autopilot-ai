from actions.models import ExecutionPlan
from ai_engine.optimizer.strategy_selector import StrategySelector
from ai_engine.simulator.simulation_service import SimulationService

class PlanBuilder:
    """
    Responsible for generating execution plans using AI strategies.
    """

    def build_plan(
        self,
        cloud_account,
        resource_type,
        resource_id,
        action_type,
        namespace=None,
    ):

        # 1️⃣ SELECT AI STRATEGY
        selector = StrategySelector()

        strategy = selector.select_strategy(resource_type=resource_type)

        if strategy:
            parameters = strategy.parameters
        else:
            parameters = {}

        # 2️⃣ RUN RISK SIMULATION
        simulator = SimulationService()

        sim = simulator.run(
            action=action_type,
            resource_type=resource_type,
            parameters=parameters
        )

        # 3️⃣ SAFETY FILTER
        if sim.predicted_risk > 0.7:
            return None

        # 4️⃣ CREATE EXECUTION PLAN
        plan = ExecutionPlan.objects.create(
            cloud_account=cloud_account,
            target_type=resource_type,
            target_name=resource_id,
            namespace=namespace,
            action=action_type,
            parameters=parameters,
            estimated_monthly_savings=sim.predicted_savings,
            risk_score=sim.predicted_risk,
            confidence=sim.confidence,
            status="planned",
        )

        return plan