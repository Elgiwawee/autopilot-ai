# ai_engine/chaos/simulator.py

import random


FAILURE_SCENARIOS = {
    "resize": ["cpu_spike", "memory_pressure"],
    "spot": ["node_loss", "interruption"],
    "stop_instance": ["downtime"],
}


def simulate_failure(action_type):
    return random.choice(FAILURE_SCENARIOS.get(action_type, ["none"]))


def confidence_after_simulation(success_rate, failures):
    penalty = len(failures) * 0.05
    return max((success_rate - penalty) * 100, 0)