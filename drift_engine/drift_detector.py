from dataclasses import dataclass
from typing import List, Optional
import math
import numpy as np

@dataclass
class DriftVerdict:
    is_drift: bool
    detectors_triggered: List[str]
    confidence: float

class CUSUMDetector:
    def __init__(self, threshold: float = 5.0, drift: float = 0.5):
        self.threshold = threshold
        self.drift = drift
        self.mean = 0.0
        self.std = 1.0
        self.count = 0
        self.g_pos = 0.0
        self.g_neg = 0.0

    def update(self, value: float) -> bool:
        self.count += 1
        if self.count == 1:
            self.mean = value
            self.std = 1.0
            return False

        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        variance = (self.std ** 2 * (self.count - 2) + delta * delta2) / (self.count - 1) if self.count > 1 else 1.0
        self.std = math.sqrt(variance) if variance > 0 else 1.0

        normalized_value = (value - self.mean) / self.std

        self.g_pos = max(0.0, self.g_pos + normalized_value - self.drift)
        self.g_neg = max(0.0, self.g_neg - normalized_value - self.drift)

        if self.g_pos > self.threshold or self.g_neg > self.threshold:
            self.reset()
            return True
        return False

    def reset(self):
        self.g_pos = 0.0
        self.g_neg = 0.0

class ADWINDetector:
    def __init__(self, delta: float = 0.002):
        self.delta = delta
        self.window = []
        self.width = 0

    def update(self, value: float) -> bool:
        self.window.append(value)
        self.width += 1
        
        if self.width < 10:
            return False

        for i in range(1, self.width - 1):
            w0 = self.window[:i]
            w1 = self.window[i:]
            n0 = len(w0)
            n1 = len(w1)
            mu0 = np.mean(w0)
            mu1 = np.mean(w1)
            
            m = 1.0 / (1.0 / n0 + 1.0 / n1)
            epsilon = math.sqrt((1.0 / (2.0 * m)) * math.log(4.0 * self.width / self.delta))
            
            if abs(mu0 - mu1) > epsilon:
                self.window = w1
                self.width = len(w1)
                return True
        return False

class PageHinkleyDetector:
    def __init__(self, min_instances: int = 30, delta: float = 0.005, threshold: float = 50.0, alpha: float = 0.9999):
        self.min_instances = min_instances
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self.x_mean = 0.0
        self.count = 0
        self.sum = 0.0

    def update(self, value: float) -> bool:
        self.count += 1
        if self.count == 1:
            self.x_mean = value
            return False
            
        self.x_mean = self.x_mean + (value - self.x_mean) / self.count
        self.sum = self.alpha * self.sum + (value - self.x_mean - self.delta)
        
        if self.sum > self.threshold and self.count > self.min_instances:
            self.sum = 0.0
            self.count = 0
            self.x_mean = 0.0
            return True
        return False

class EnsembleDriftDetector:
    def __init__(self):
        self.cusum = CUSUMDetector()
        self.adwin = ADWINDetector()
        self.ph = PageHinkleyDetector()

    def update(self, value: float) -> DriftVerdict:
        results = {
            "CUSUM": self.cusum.update(value),
            "ADWIN": self.adwin.update(value),
            "PageHinkley": self.ph.update(value)
        }
        
        triggered = [name for name, res in results.items() if res]
        score = len(triggered) / 3.0
        
        return DriftVerdict(
            is_drift=score > 0.33,
            detectors_triggered=triggered,
            confidence=score
        )
