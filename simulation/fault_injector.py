import dataclasses
from enum import Enum, auto
from typing import List

class FaultType(Enum):
    QUEUE_BACKPRESSURE = auto()
    LATENCY_SPIKE = auto()
    THROUGHPUT_DROP = auto()
    CASCADE_FAILURE = auto()
    RANDOM_NOISE = auto()

@dataclasses.dataclass
class FaultScenario:
    name: str
    target_intent: str
    fault_type: FaultType
    severity: float
    start_time: float
    duration: float

class FaultInjector:
    def __init__(self):
        self.scenarios: List[FaultScenario] = []

    def schedule_fault(self, scenario: FaultScenario):
        self.scenarios.append(scenario)

    def get_active_faults(self, current_time: float) -> List[FaultScenario]:
        return [
            s for s in self.scenarios 
            if s.start_time <= current_time < (s.start_time + s.duration)
        ]

    def create_cascade_scenario(self) -> List[FaultScenario]:
        return [
            FaultScenario("Telemetry_Backpressure", "telemetry", FaultType.QUEUE_BACKPRESSURE, 0.8, 10.0, 30.0),
            FaultScenario("Analytics_Latency", "analytics", FaultType.LATENCY_SPIKE, 0.9, 15.0, 25.0)
        ]
