from dataclasses import dataclass
from typing import Dict, List, Optional
import math
import numpy as np

@dataclass
class KPIStats:
    mean: float
    std: float
    min: float
    max: float
    trend: str

class KPIMonitor:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._history: Dict[str, Dict[str, List[float]]] = {}
        self._baselines: Dict[str, Dict[str, float]] = {}

    def update(self, intent_id: str, kpi_name: str, value: float):
        if intent_id not in self._history:
            self._history[intent_id] = {}
        if kpi_name not in self._history[intent_id]:
            self._history[intent_id][kpi_name] = []
        
        hist = self._history[intent_id][kpi_name]
        hist.append(value)
        if len(hist) > self.window_size:
            hist.pop(0)

        if intent_id not in self._baselines:
            self._baselines[intent_id] = {}
        if kpi_name not in self._baselines[intent_id]:
            self._baselines[intent_id][kpi_name] = value

    def get_deviation(self, intent_id: str, kpi_name: str) -> float:
        if intent_id not in self._history or kpi_name not in self._history[intent_id]:
            return 0.0
        hist = self._history[intent_id][kpi_name]
        if not hist:
            return 0.0
        baseline = self._baselines.get(intent_id, {}).get(kpi_name, hist[0])
        current_value = hist[-1]
        if baseline == 0:
            return 0.0 if current_value == 0 else float("inf")
        return ((current_value - baseline) / abs(baseline)) * 100.0

    def get_statistics(self, intent_id: str, kpi_name: str) -> KPIStats:
        if intent_id not in self._history or kpi_name not in self._history[intent_id]:
            return KPIStats(0.0, 0.0, 0.0, 0.0, "FLAT")
        hist = self._history[intent_id][kpi_name]
        if not hist:
            return KPIStats(0.0, 0.0, 0.0, 0.0, "FLAT")
        
        arr = np.array(hist)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        min_v = float(np.min(arr))
        max_v = float(np.max(arr))
        
        trend = "FLAT"
        if len(hist) > 1:
            x = np.arange(len(hist))
            slope, _ = np.polyfit(x, arr, 1)
            if slope > 0.01:
                trend = "UP"
            elif slope < -0.01:
                trend = "DOWN"
                
        return KPIStats(mean=mean, std=std, min=min_v, max=max_v, trend=trend)
