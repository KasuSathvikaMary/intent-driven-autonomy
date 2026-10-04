from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

from drift_engine.models import MacroIntent, DriftEvent, CausalLink, RootCauseReport
from drift_engine.granger_engine import GrangerCausalityEngine

@dataclass
class CausalGraph:
    nodes: List[str]
    edges: List[Tuple[str, str, float]]
    adjacency_matrix: np.ndarray

class CausalCoAnalyzer:
    def __init__(self, intents: List[MacroIntent]):
        self.intents = {intent.intent_id: intent for intent in intents}
        self.granger = GrangerCausalityEngine()

    def build_scm(self, kpi_history: Dict[str, List[float]]) -> CausalGraph:
        matrix = self.granger.build_causality_matrix(kpi_history)
        nodes = list(kpi_history.keys())
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        edges = []
        
        for i, src in enumerate(nodes):
            for j, dst in enumerate(nodes):
                if i != j:
                    res = matrix[src].get(dst)
                    if res and res.is_causal:
                        adj_matrix[i, j] = 1.0 - res.p_value
                        edges.append((src, dst, 1.0 - res.p_value))
                        
        return CausalGraph(nodes=nodes, edges=edges, adjacency_matrix=adj_matrix)

    def detect_co_drift(self, drift_events: List[DriftEvent]) -> List[CausalLink]:
        links = []
        events_by_time = sorted(drift_events, key=lambda x: x.timestamp)
        
        for i in range(len(events_by_time)):
            for j in range(i + 1, len(events_by_time)):
                e1 = events_by_time[i]
                e2 = events_by_time[j]
                
                lag = e2.timestamp - e1.timestamp
                if 0 < lag < 3600:
                    link = CausalLink(
                        source_intent=e1.intent_id,
                        target_intent=e2.intent_id,
                        mechanism=f"Temporal sequence {e1.kpi_name} -> {e2.kpi_name}",
                        strength=0.8 * (1 - (lag / 3600.0)),
                        lag_seconds=lag
                    )
                    links.append(link)
        return links

    def trace_root_cause(self, drift_events: List[DriftEvent]) -> RootCauseReport:
        if not drift_events:
            return RootCauseReport("unknown", "unknown", [], [], 0.0, 0.0)
            
        links = self.detect_co_drift(drift_events)
        
        earliest_event = min(drift_events, key=lambda x: x.timestamp)
        affected = list({e.intent_id for e in drift_events if e.intent_id != earliest_event.intent_id})
        
        confidence = 0.5 + (0.1 * len(links))
        confidence = min(0.99, confidence)
        
        return RootCauseReport(
            root_intent_id=earliest_event.intent_id,
            root_kpi=earliest_event.kpi_name,
            affected_intents=affected,
            causal_chain=links,
            confidence=confidence,
            timestamp=earliest_event.timestamp
        )
