import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
import time

class IntentStatus(Enum):
    RECEIVED = auto()
    COMPILING = auto()
    COMPILED = auto()
    REJECTED = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class ClosureGapVector:
    semantic: float
    evidentiary: float
    procedural: float
    institutional: float

    def magnitude(self) -> float:
        return math.sqrt(
            self.semantic**2 +
            self.evidentiary**2 +
            self.procedural**2 +
            self.institutional**2
        )

    def is_safe(self, threshold: float) -> bool:
        return (
            self.semantic <= threshold and
            self.evidentiary <= threshold and
            self.procedural <= threshold and
            self.institutional <= threshold
        )

@dataclass
class Intent:
    id: str
    description: str
    source: str
    priority: int
    timestamp: float = field(default_factory=time.time)
    status: IntentStatus = IntentStatus.RECEIVED

@dataclass
class DeviceConfig:
    device_id: str
    config_type: str
    parameters: Dict[str, Any]
    policy_refs: List[str]

@dataclass
class CompilationResult:
    intent: Intent
    closure_gap: ClosureGapVector
    compiled_config: Dict[str, Any]
    warnings: List[str]
    compilation_time_ms: float
    is_actionable: bool
