import dataclasses
from typing import List
from delegation.models import Agent, DelegationEnvelope

@dataclasses.dataclass
class EnvelopeCheckResult:
    is_within_envelope: bool
    violations: List[str]
    risk_assessment: str

class EnvelopeManager:
    def __init__(self, agents: List[Agent]):
        self.agents = {agent.agent_id: agent for agent in agents}

    def compute_envelope(self, agent: Agent, closure_gap: float) -> DelegationEnvelope:
        # Base envelope
        base = agent.delegation_envelope
        # Modulate limits based on trust and current load
        trust_factor = max(0.1, agent.trust_score)
        load_penalty = max(1.0, 1.0 + agent.current_load)
        
        return DelegationEnvelope(
            agent_id=agent.agent_id,
            authorized_domains=base.authorized_domains,
            max_closure_gap=base.max_closure_gap * trust_factor,
            max_impact_level=int(base.max_impact_level * trust_factor),
            requires_human_approval=trust_factor < 0.5 or closure_gap > base.max_closure_gap,
            time_budget_ms=base.time_budget_ms / load_penalty,
            escalation_policy=base.escalation_policy
        )

    def check_envelope(self, agent: Agent, intent: dict, closure_gap: float) -> EnvelopeCheckResult:
        envelope = agent.delegation_envelope
        violations = []
        
        domain = intent.get("domain", "")
        if domain and domain not in envelope.authorized_domains:
            violations.append(f"Domain '{domain}' not in authorized domains: {envelope.authorized_domains}")
            
        if closure_gap > envelope.max_closure_gap:
            violations.append(f"Closure gap {closure_gap:.2f} exceeds limit {envelope.max_closure_gap:.2f}")
            
        impact = intent.get("impact_level", 1)
        if impact > envelope.max_impact_level:
            violations.append(f"Impact level {impact} exceeds max {envelope.max_impact_level}")

        is_safe = len(violations) == 0
        risk = "HIGH" if len(violations) > 1 else "MEDIUM" if violations else "LOW"
        
        return EnvelopeCheckResult(
            is_within_envelope=is_safe,
            violations=violations,
            risk_assessment=risk
        )

    def adapt_envelope(self, agent: Agent, performance_history: List[float]):
        """Dynamically adjusts envelope based on agent performance (success rate 0.0 to 1.0)"""
        if not performance_history:
            return
            
        avg_perf = sum(performance_history) / len(performance_history)
        # Adapt limits
        if avg_perf > 0.8:
            agent.delegation_envelope.max_closure_gap *= 1.1
            agent.delegation_envelope.time_budget_ms *= 1.1
        elif avg_perf < 0.5:
            agent.delegation_envelope.max_closure_gap *= 0.8
            agent.delegation_envelope.requires_human_approval = True
