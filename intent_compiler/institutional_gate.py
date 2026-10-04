from dataclasses import dataclass
from typing import List
from .models import Intent

@dataclass
class AgentRole:
    role_id: str
    name: str
    authorized_domains: List[str]
    max_impact_level: int # 1 to 5
    requires_approval_above: int

class InstitutionalGate:
    def evaluate(self, intent: Intent, agent_role: AgentRole, domain: str) -> float:
        # 0.0 = fully clear, 1.0 = fully blocked
        gap = 0.0
        
        if domain not in agent_role.authorized_domains:
            gap += 0.5
            
        # Estimate intent impact from priority
        impact_level = min(max(intent.priority, 1), 5)
        
        if impact_level > agent_role.max_impact_level:
            gap += 0.4
            
        if impact_level >= agent_role.requires_approval_above:
            gap += 0.1 # Need approval, small gap indicating waiting state or friction
            
        return min(gap, 1.0)
