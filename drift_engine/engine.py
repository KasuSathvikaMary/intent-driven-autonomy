from dataclasses import dataclass
from typing import Dict, List, Optional
import time

from drift_engine.models import MacroIntent, DriftEvent, DriftType, IntentHealth, RootCauseReport
from drift_engine.kpi_monitor import KPIMonitor, KPIStats
from drift_engine.drift_detector import EnsembleDriftDetector
from drift_engine.causal_analyzer import CausalCoAnalyzer
from drift_engine.sla_predictor import SLABreachPredictor, SLAPrediction

@dataclass
class DriftEngineConfig:
    monitoring_interval_ms: int = 1000
    drift_sensitivity: float = 0.5
    causality_max_lag: int = 10
    prediction_horizon: int = 50
    sla_check_interval: int = 10

@dataclass
class SystemHealthReport:
    healthy_intents: int
    degraded_intents: int
    critical_intents: int
    failed_intents: int
    active_drifts: int

class DriftEngine:
    def __init__(self, intents: List[MacroIntent], config: DriftEngineConfig):
        self.intents = {intent.intent_id: intent for intent in intents}
        self.config = config
        self.kpi_monitor = KPIMonitor()
        self.detectors: Dict[str, Dict[str, EnsembleDriftDetector]] = {}
        self.causal_analyzer = CausalCoAnalyzer(intents)
        self.sla_predictor = SLABreachPredictor(prediction_horizon=config.prediction_horizon)
        self.recent_events: List[DriftEvent] = []

    def _get_detector(self, intent_id: str, kpi_name: str) -> EnsembleDriftDetector:
        if intent_id not in self.detectors:
            self.detectors[intent_id] = {}
        if kpi_name not in self.detectors[intent_id]:
            self.detectors[intent_id][kpi_name] = EnsembleDriftDetector()
        return self.detectors[intent_id][kpi_name]

    def ingest_kpi(self, intent_id: str, kpi_name: str, value: float):
        self.kpi_monitor.update(intent_id, kpi_name, value)
        detector = self._get_detector(intent_id, kpi_name)
        verdict = detector.update(value)
        
        if intent_id in self.intents:
            self.intents[intent_id].kpi_current[kpi_name] = value
            
        if verdict.is_drift:
            baseline = self.intents[intent_id].kpi_baselines.get(kpi_name, value) if intent_id in self.intents else value
            dev = self.kpi_monitor.get_deviation(intent_id, kpi_name)
            
            event = DriftEvent(
                intent_id=intent_id,
                kpi_name=kpi_name,
                baseline_value=baseline,
                current_value=value,
                deviation_pct=dev,
                drift_type=DriftType.GRADUAL if dev < 20 else DriftType.SUDDEN,
                timestamp=time.time(),
                severity="HIGH" if abs(dev) > 20 else "MEDIUM"
            )
            self.recent_events.append(event)
            
            if intent_id in self.intents:
                self.intents[intent_id].status = IntentHealth.DEGRADED

    def check_drift(self) -> List[DriftEvent]:
        events = list(self.recent_events)
        self.recent_events.clear()
        return events

    def analyze_causality(self, events: List[DriftEvent]) -> RootCauseReport:
        return self.causal_analyzer.trace_root_cause(events)

    def predict_breaches(self) -> List[SLAPrediction]:
        all_predictions = []
        for intent in self.intents.values():
            if intent.intent_id in self.kpi_monitor._history:
                preds = self.sla_predictor.predict_breach(intent, self.kpi_monitor._history[intent.intent_id])
                all_predictions.extend(preds)
        return all_predictions

    def get_system_health(self) -> SystemHealthReport:
        counts = {
            IntentHealth.HEALTHY: 0,
            IntentHealth.DEGRADED: 0,
            IntentHealth.CRITICAL: 0,
            IntentHealth.FAILED: 0
        }
        for intent in self.intents.values():
            counts[intent.status] += 1
            
        return SystemHealthReport(
            healthy_intents=counts[IntentHealth.HEALTHY],
            degraded_intents=counts[IntentHealth.DEGRADED],
            critical_intents=counts[IntentHealth.CRITICAL],
            failed_intents=counts[IntentHealth.FAILED],
            active_drifts=len(self.recent_events)
        )
