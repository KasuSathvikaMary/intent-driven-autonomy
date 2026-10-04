import re
from dataclasses import dataclass
from typing import List, Set
from .models import Intent

@dataclass
class Policy:
    policy_id: str
    name: str
    required_tools: Set[str]
    forbidden_actions: Set[str]
    audit_required: bool

class ProceduralValidator:
    def validate(self, intent: Intent, available_tools: List[str], policies: List[Policy]) -> float:
        avail_tools_set = set(available_tools)
        
        if not policies:
            # Without policies, procedural gap is high as we can't guarantee safety
            return 1.0
            
        policy_gaps = []
        for policy in policies:
            tool_gap = self._check_tool_coverage(policy.required_tools, avail_tools_set)
            compliance_gap = self._check_policy_compliance(intent, [policy])
            audit_gap = 0.0 if policy.audit_required else 0.5 # Encourage auditability
            
            policy_gap = (tool_gap * 0.4) + (compliance_gap * 0.5) + (audit_gap * 0.1)
            policy_gaps.append(policy_gap)
            
        return sum(policy_gaps) / len(policy_gaps)

    def _check_tool_coverage(self, required: Set[str], available: Set[str]) -> float:
        if not required:
            return 0.0
        missing = required - available
        return len(missing) / len(required)

    def _check_policy_compliance(self, intent: Intent, policies: List[Policy]) -> float:
        desc_words = set(re.findall(r'\b\w+\b', intent.description.lower()))
        for policy in policies:
            for action in policy.forbidden_actions:
                if action.lower() in desc_words:
                    return 1.0 # Total failure if forbidden action is mentioned
        return 0.0
