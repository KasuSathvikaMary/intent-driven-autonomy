import dataclasses
from typing import List, Optional
from delegation.models import Agent

@dataclasses.dataclass
class MisdelegationReport:
    is_misdelegated: bool
    risk_factors: List[str]
    severity: float
    recommended_agent_id: Optional[str]

class MisdelegationDetector:
    def __init__(self, capability_registry=None):
        self.registry = capability_registry

    def detect(self, intent: dict, agent: Agent, closure_gap: float) -> MisdelegationReport:
        risk_factors = []
        severity = 0.0

        req_caps = intent.get("required_capabilities", [])
        missing_caps = [c for c in req_caps if c not in agent.capabilities]
        if missing_caps:
            risk_factors.append(f"Missing capabilities: {missing_caps}")
            severity += 0.5 * len(missing_caps)

        if agent.current_load > 0.8:
            risk_factors.append(f"Agent overloaded (load={agent.current_load:.2f})")
            severity += 0.3
            
        if agent.trust_score < 0.4:
            risk_factors.append(f"Low trust score ({agent.trust_score:.2f})")
            severity += 0.4

        if closure_gap > agent.delegation_envelope.max_closure_gap:
            risk_factors.append(f"Closure gap too high ({closure_gap} > {agent.delegation_envelope.max_closure_gap})")
            severity += 0.5

        is_misdelegated = severity >= 0.8 or len(missing_caps) > 0
        
        recommended = None
        if is_misdelegated and self.registry:
            # Try to find a better agent
            capable = self.registry.find_capable_agents(req_caps, min_trust=0.5)
            # Filter out overloaded ones
            capable = [a for a in capable if a.current_load < 0.6]
            if capable:
                recommended = self.registry.get_load_balanced_agent(capable).agent_id

        return MisdelegationReport(
            is_misdelegated=is_misdelegated,
            risk_factors=risk_factors,
            severity=min(1.0, severity),
            recommended_agent_id=recommended
        )
