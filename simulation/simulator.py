import dataclasses
from typing import List, Callable, Optional, Dict
from simulation.network_intents import TelemetryIntent, AnalyticsIntent, APIGatewayIntent
from simulation.fault_injector import FaultInjector, FaultScenario, FaultType

@dataclasses.dataclass
class SimulatorConfig:
    time_step: float = 1.0
    total_duration: float = 100.0
    enable_faults: bool = True
    fault_scenarios: List[FaultScenario] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class SimulationResult:
    kpi_history: List[Dict[str, dict]]
    drift_events: List[str]
    causal_reports: List[str]
    sla_breaches: int

class NetworkSimulator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.time = 0.0
        
        # Instantiate network topology
        self.telemetry = TelemetryIntent(queue_capacity=5000)
        self.analytics = AnalyticsIntent(self.telemetry)
        self.gateway = APIGatewayIntent(self.analytics)
        
        self.fault_injector = FaultInjector()
        if self.config.enable_faults:
            for fs in self.config.fault_scenarios:
                self.fault_injector.schedule_fault(fs)

    def step(self) -> Dict[str, dict]:
        # Apply active faults
        active_faults = self.fault_injector.get_active_faults(self.time)
        
        # Reset transient faults
        self.telemetry.fault_severity = 0.0
        
        for fault in active_faults:
            if fault.target_intent == "telemetry" and fault.fault_type == FaultType.QUEUE_BACKPRESSURE:
                self.telemetry.inject_backpressure_fault(fault.severity)
                
        # Advance simulation
        self.telemetry.step(self.config.time_step)
        self.analytics.step(self.config.time_step)
        self.gateway.step(self.config.time_step)
        
        # Collect KPIs
        kpis = {
            "time": self.time,
            "telemetry": self.telemetry.generate_kpis(),
            "analytics": self.analytics.generate_kpis(),
            "gateway": self.gateway.generate_kpis()
        }
        
        self.time += self.config.time_step
        return kpis

    def run(self, callback: Optional[Callable[[Dict], None]] = None) -> SimulationResult:
        history = []
        sla_breaches = 0
        
        while self.time < self.config.total_duration:
            kpis = self.step()
            history.append(kpis)
            
            if kpis["gateway"]["sla_compliance"] < 0.8:
                sla_breaches += 1
                
            if callback:
                callback(kpis)
                
        return SimulationResult(
            kpi_history=history,
            drift_events=[], # to be integrated with drift engine
            causal_reports=[], 
            sla_breaches=sla_breaches
        )
