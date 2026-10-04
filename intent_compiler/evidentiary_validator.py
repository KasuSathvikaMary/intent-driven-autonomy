import time
from dataclasses import dataclass
from typing import List
from .models import Intent

@dataclass
class ContextSource:
    source_id: str
    data: dict
    timestamp: float
    reliability_score: float # 0.0 to 1.0
    is_corrupted: bool = False

class EvidentiaryValidator:
    def validate(self, intent: Intent, context_sources: List[ContextSource]) -> float:
        if not context_sources:
            return 1.0 # Max gap if no context sources
        
        # Max age of 1 hour (3600 seconds)
        max_age_seconds = 3600.0
        
        freshness_gap = sum(self._check_freshness(src, max_age_seconds) for src in context_sources) / len(context_sources)
        reliability_gap = self._check_reliability(context_sources)
        corruption_gap = sum(1.0 if src.is_corrupted else 0.0 for src in context_sources) / len(context_sources)
        
        total_gap = (freshness_gap * 0.3) + (reliability_gap * 0.4) + (corruption_gap * 0.3)
        return min(max(total_gap, 0.0), 1.0)

    def _check_freshness(self, source: ContextSource, max_age_seconds: float) -> float:
        age = time.time() - source.timestamp
        if age < 0:
            return 1.0 # Invalid timestamp in the future
        if age >= max_age_seconds:
            return 1.0
        return age / max_age_seconds

    def _check_reliability(self, sources: List[ContextSource]) -> float:
        if not sources:
            return 1.0
        avg_reliability = sum(src.reliability_score for src in sources) / len(sources)
        return 1.0 - avg_reliability # Gap is inverse of reliability
