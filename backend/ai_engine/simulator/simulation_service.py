# ai_engine/simulator/simulation_service.py

from ai_engine.models.simulation import SimulationResult
from ai_engine.simulator.risk_simulator import RiskSimulator


class SimulationService:

    def run(self, action, resource_type, parameters):

        simulator = RiskSimulator()

        result = simulator.simulate(
            action,
            resource_type,
            parameters
        )

        sim = SimulationResult.objects.create(
            action=action,
            resource_type=resource_type,
            predicted_savings=result["predicted_savings"],
            predicted_risk=result["predicted_risk"],
            confidence=result["confidence"],
            parameters=parameters,
        )

        return sim