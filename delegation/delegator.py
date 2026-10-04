import dataclasses
from delegation.models import DelegationDecision
from delegation.envelope_manager import EnvelopeManager
from delegation.capability_registry import AgentCapabilityRegistry
from delegation.misdelegation_detector import MisdelegationDetector
from delegation.escalation_controller import EscalationController

@dataclasses.dataclass
class DelegatorConfig:
    min_trust_threshold: float = 0.5
    max_load_threshold: float = 0.8
    escalation_policies: dict = dataclasses.field(default_factory=dict)

class AdaptiveDelegator:
    def __init__(self, config: DelegatorConfig, agents=None):
        self.config = config
        self.registry = AgentCapabilityRegistry()
        if agents:
            for a in agents:
                self.registry.register_agent(a)
        
        self.envelope_manager = EnvelopeManager(list(self.registry._agents.values()))
        self.detector = MisdelegationDetector(self.registry)
        self.escalator = EscalationController(config.escalation_policies)

    def delegate(self, intent: dict, closure_gap: float, context: dict) -> DelegationDecision:
        intent_id = intent.get("id", "unknown_intent")
        req_caps = intent.get("required_capabilities", [])
        
        # Find capable agents
        capable_agents = self.registry.find_capable_agents(req_caps, self.config.min_trust_threshold)
        candidate = self.registry.get_load_balanced_agent(capable_agents)

        if not candidate:
            self.escalator.create_escalation(intent, candidate or next(iter(self.registry._agents.values()), None), "No capable agent found")
            return DelegationDecision(intent_id, None, False, "No capable agent found", 1.0, [])

        # Check envelope
        env_check = self.envelope_manager.check_envelope(candidate, intent, closure_gap)
        
        # Check misdelegation
        misdel_report = self.detector.detect(intent, candidate, closure_gap)

        if self.escalator.should_escalate(intent, closure_gap, env_check) or misdel_report.is_misdelegated:
            reason = " | ".join(env_check.violations + misdel_report.risk_factors)
            self.escalator.create_escalation(intent, candidate, reason)
            
            # If misdelegation recommended another agent, we could retry, but for now we reject
            return DelegationDecision(
                task_intent_id=intent_id,
                assigned_agent_id=candidate.agent_id,
                is_delegated=False,
                reason=f"Delegation rejected: {reason}",
                risk_score=misdel_report.severity,
                envelope_violations=env_check.violations
            )

        # Success
        return DelegationDecision(
            task_intent_id=intent_id,
            assigned_agent_id=candidate.agent_id,
            is_delegated=True,
            reason="Delegation successful",
            risk_score=misdel_report.severity,
            envelope_violations=[]
        )
