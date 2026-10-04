from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import time

class IntentHealth(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    FAILED = "FAILED"

class DriftType(Enum):
    GRADUAL = "GRADUAL"
    SUDDEN = "SUDDEN"
    INCREMENTAL = "INCREMENTAL"

@dataclass
class MacroIntent:
    intent_id: str
    name: str
    kpi_baselines: Dict[str, float]
    kpi_current: Dict[str, float]
    dependencies: List[str]
    sla_thresholds: Dict[str, float]
    status: IntentHealth

@dataclass
class DriftEvent:
    intent_id: str
    kpi_name: str
    baseline_value: float
    current_value: float
    deviation_pct: float
    drift_type: DriftType
    timestamp: float
    severity: str

@dataclass
class CausalLink:
    source_intent: str
    target_intent: str
    mechanism: str
    strength: float
    lag_seconds: float

@dataclass
class RootCauseReport:
    root_intent_id: str
    root_kpi: str
    affected_intents: List[str]
    causal_chain: List[CausalLink]
    confidence: float
    timestamp: float
