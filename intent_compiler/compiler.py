import time
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .models import Intent, ClosureGapVector, CompilationResult, IntentStatus, DeviceConfig
from .semantic_resolver import SemanticResolver
from .evidentiary_validator import EvidentiaryValidator, ContextSource
from .procedural_validator import ProceduralValidator, Policy
from .institutional_gate import InstitutionalGate, AgentRole
from .overclosure_detector import OverclosureDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompilerConfig:
    semantic_threshold: float
    evidentiary_threshold: float
    procedural_threshold: float
    institutional_threshold: float
    time_budget_ms: float
    strict_mode: bool

@dataclass
class CompilationContext:
    context_sources: List[ContextSource]
    available_tools: List[str]
    policies: List[Policy]
    agent_role: AgentRole
    target_domain: str

class IntentCompiler:
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.semantic_resolver = SemanticResolver()
        self.evidentiary_validator = EvidentiaryValidator()
        self.procedural_validator = ProceduralValidator()
        self.institutional_gate = InstitutionalGate()
        self.overclosure_detector = OverclosureDetector()

    def compile(self, intent: Intent, context: CompilationContext) -> CompilationResult:
        start_time = time.time()
        intent.status = IntentStatus.COMPILING
        logger.info(f"Starting compilation for intent {intent.id}")
        
        warnings = []
        
        # 1. Evaluate gaps
        semantic_gap = self.semantic_resolver.resolve(intent)
        evidentiary_gap = self.evidentiary_validator.validate(intent, context.context_sources)
        procedural_gap = self.procedural_validator.validate(intent, context.available_tools, context.policies)
        institutional_gap = self.institutional_gate.evaluate(intent, context.agent_role, context.target_domain)
        
        gap_vector = ClosureGapVector(
            semantic=semantic_gap,
            evidentiary=evidentiary_gap,
            procedural=procedural_gap,
            institutional=institutional_gap
        )
        
        # 2. Check Overclosure
        compilation_time_ms = (time.time() - start_time) * 1000
        overclosure_report = self.overclosure_detector.detect(gap_vector, compilation_time_ms, self.config.time_budget_ms)
        
        if overclosure_report.is_overclosed:
            warnings.append(f"Overclosure detected: Risk {overclosure_report.risk_score}")
            warnings.extend(overclosure_report.gap_violations)
            
        # 3. Determine if actionable
        is_actionable = True
        
        if gap_vector.semantic > self.config.semantic_threshold:
            warnings.append("Semantic gap exceeds threshold")
            is_actionable = False
            
        if gap_vector.evidentiary > self.config.evidentiary_threshold:
            warnings.append("Evidentiary gap exceeds threshold")
            is_actionable = False
            
        if gap_vector.procedural > self.config.procedural_threshold:
            warnings.append("Procedural gap exceeds threshold")
            is_actionable = False
            
        if gap_vector.institutional > self.config.institutional_threshold:
            warnings.append("Institutional gap exceeds threshold")
            is_actionable = False
            
        if self.config.strict_mode and overclosure_report.is_overclosed:
            warnings.append("Strict mode enforced: Overclosure blocked compilation")
            is_actionable = False
            
        # 4. Generate compiled config
        compiled_config = {}
        if is_actionable:
            compiled_config = {
                "execution_strategy": "default",
                "policies_applied": [p.policy_id for p in context.policies],
                "domain": context.target_domain,
                "priority_adjusted": intent.priority,
            }
            intent.status = IntentStatus.COMPILED
            logger.info(f"Intent {intent.id} successfully compiled.")
        else:
            intent.status = IntentStatus.REJECTED
            logger.warning(f"Intent {intent.id} rejected due to unacceptable gaps.")
            
        final_time_ms = (time.time() - start_time) * 1000
        
        return CompilationResult(
            intent=intent,
            closure_gap=gap_vector,
            compiled_config=compiled_config,
            warnings=warnings,
            compilation_time_ms=final_time_ms,
            is_actionable=is_actionable
        )
