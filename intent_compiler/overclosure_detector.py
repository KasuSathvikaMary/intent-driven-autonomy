from dataclasses import dataclass
from typing import List
from .models import ClosureGapVector

@dataclass
class OverclosureReport:
    is_overclosed: bool
    risk_score: float
    gap_violations: List[str]
    recommended_actions: List[str]

class OverclosureDetector:
    def detect(self, closure_gap: ClosureGapVector, compilation_time_ms: float, time_budget_ms: float) -> OverclosureReport:
        is_overclosed = False
        violations = []
        actions = []
        
        # High gaps combined with fast compilation time indicates overclosure (skipping validation to save time)
        avg_gap = (closure_gap.semantic + closure_gap.evidentiary + closure_gap.procedural + closure_gap.institutional) / 4.0
        
        if avg_gap > 0.5 and compilation_time_ms < (time_budget_ms * 0.1):
            is_overclosed = True
            violations.append("High average gap resolved suspiciously quickly")
            actions.append("Force deeper semantic and evidentiary validation")
            
        if closure_gap.institutional > 0.8:
            is_overclosed = True
            violations.append("Critical institutional gap bypassed")
            actions.append("Require manual executive override")
            
        if closure_gap.procedural > 0.7:
            violations.append("High procedural gap")
            actions.append("Review tool requirements and policy compliance")
            if avg_gap > 0.6:
                is_overclosed = True
                
        risk_score = avg_gap * (1.0 if is_overclosed else 0.5)
        
        return OverclosureReport(
            is_overclosed=is_overclosed,
            risk_score=min(risk_score, 1.0),
            gap_violations=violations,
            recommended_actions=actions
        )
