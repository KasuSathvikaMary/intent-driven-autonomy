import dataclasses
import time
from typing import List, Optional

@dataclasses.dataclass
class DelegationEnvelope:
    agent_id: str
    authorized_domains: List[str]
    max_closure_gap: float
    max_impact_level: int
    requires_human_approval: bool
    time_budget_ms: float
    escalation_policy: str

@dataclasses.dataclass
class Agent:
    agent_id: str
    name: str
    capabilities: List[str]
    trust_score: float  # 0.0 to 1.0
    current_load: float # 0.0 to 1.0
    delegation_envelope: DelegationEnvelope

@dataclasses.dataclass
class DelegationDecision:
    task_intent_id: str
    assigned_agent_id: Optional[str]
    is_delegated: bool
    reason: str
    risk_score: float
    envelope_violations: List[str]

@dataclasses.dataclass
class EscalationEvent:
    intent_id: str
    original_agent_id: str
    escalation_reason: str
    severity: int # 1-5
    timestamp: float = dataclasses.field(default_factory=time.time)
    resolved: bool = False
