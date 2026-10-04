import re
from .models import Intent

class SemanticResolver:
    def __init__(self):
        self.vague_terms = {'optimize', 'improve', 'fix', 'better', 'fast', 'soon', 'good'}

    def resolve(self, intent: Intent) -> float:
        ambiguity_score = self._check_ambiguity(intent.description)
        criteria_score = self._check_acceptance_criteria(intent.description)
        quantifiability_score = self._check_quantifiability(intent.description)
        
        # Calculate a weighted average for the semantic gap.
        # 0.0 means fully resolved (no gap), 1.0 means fully ambiguous (max gap).
        gap = (ambiguity_score * 0.4) + (criteria_score * 0.3) + (quantifiability_score * 0.3)
        return min(max(gap, 0.0), 1.0)

    def _check_ambiguity(self, description: str) -> float:
        words = set(re.findall(r'\b\w+\b', description.lower()))
        overlap = words.intersection(self.vague_terms)
        if not words:
            return 1.0
        # More vague terms increase ambiguity
        ratio = len(overlap) / len(words)
        return min(ratio * 10, 1.0) # Scale up to make a few vague terms impactful

    def _check_acceptance_criteria(self, description: str) -> float:
        # Check if the description contains terms indicating criteria
        criteria_indicators = ['must', 'should', 'required', 'criteria', 'when', 'if', 'ensure']
        lower_desc = description.lower()
        if any(indicator in lower_desc for indicator in criteria_indicators):
            return 0.1 # Very low gap
        return 0.8 # High gap

    def _check_quantifiability(self, description: str) -> float:
        # Check if there are numbers or percentages which usually denote quantifiability
        has_numbers = bool(re.search(r'\d+', description))
        has_percent = '%' in description or 'percent' in description.lower()
        
        if has_numbers and has_percent:
            return 0.0
        if has_numbers:
            return 0.3
        return 0.9 # Lack of numbers usually means less quantifiable
