from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

from drift_engine.models import MacroIntent

@dataclass
class SLAPrediction:
    kpi_name: str
    current_value: float
    sla_threshold: float
    predicted_breach_time: Optional[float]
    confidence: float
    trend_direction: str

class SLABreachPredictor:
    def __init__(self, prediction_horizon: int = 50):
        self.prediction_horizon = prediction_horizon

    def _exponential_smoothing(self, data: List[float], alpha: float) -> List[float]:
        result = [data[0]]
        for i in range(1, len(data)):
            result.append(alpha * data[i] + (1 - alpha) * result[i - 1])
        return result

    def predict_breach(self, intent: MacroIntent, kpi_history: Dict[str, List[float]]) -> List[SLAPrediction]:
        predictions = []
        
        for kpi, threshold in intent.sla_thresholds.items():
            if kpi not in kpi_history or len(kpi_history[kpi]) < 2:
                continue
                
            history = kpi_history[kpi]
            smoothed = self._exponential_smoothing(history, 0.3)
            current_value = smoothed[-1]
            
            x = np.arange(len(smoothed))
            y = np.array(smoothed)
            slope, intercept = np.polyfit(x, y, 1)
            
            trend_direction = "UP" if slope > 0 else "DOWN" if slope < 0 else "FLAT"
            
            predicted_time = None
            if slope != 0:
                steps_to_breach = (threshold - current_value) / slope
                if 0 < steps_to_breach <= self.prediction_horizon:
                    predicted_time = steps_to_breach
            
            confidence = 1.0 - (min(abs(steps_to_breach), self.prediction_horizon) / self.prediction_horizon) if predicted_time else 0.0
            if confidence < 0: confidence = 0.0
                
            predictions.append(SLAPrediction(
                kpi_name=kpi,
                current_value=current_value,
                sla_threshold=threshold,
                predicted_breach_time=predicted_time,
                confidence=confidence,
                trend_direction=trend_direction
            ))
            
        return predictions
