from typing import Dict
from delegation.models import EscalationEvent, Agent
from delegation.envelope_manager import EnvelopeCheckResult

class EscalationController:
    def __init__(self, escalation_policies: Dict[str, dict]):
        self.policies = escalation_policies
        self.escalation_log: list[EscalationEvent] = []

    def should_escalate(self, intent: dict, closure_gap: float, envelope_check: EnvelopeCheckResult) -> bool:
        if not envelope_check.is_within_envelope:
            return True
        if intent.get("impact_level", 1) >= 4 and closure_gap > 0.8:
            return True
        return False

    def create_escalation(self, intent: dict, agent: Agent, reason: str) -> EscalationEvent:
        policy = self.policies.get(agent.delegation_envelope.escalation_policy, {})
        severity = policy.get("default_severity", 3)
        
        event = EscalationEvent(
            intent_id=intent.get("id", "unknown"),
            original_agent_id=agent.agent_id,
            escalation_reason=reason,
            severity=severity
        )
        self.escalation_log.append(event)
        return event

    def resolve_escalation(self, event_id: str, resolution: str):
        for event in self.escalation_log:
            if getattr(event, 'id', None) == event_id or f"{event.intent_id}-{event.original_agent_id}" == event_id:
                event.resolved = True
                event.resolution_note = resolution
                break
