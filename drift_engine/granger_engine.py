from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import scipy.stats as stats

@dataclass
class GrangerResult:
    is_causal: bool
    f_statistic: float
    p_value: float
    optimal_lag: int

class GrangerCausalityEngine:
    def __init__(self, max_lag: int = 10, significance_level: float = 0.05):
        self.max_lag = max_lag
        self.significance_level = significance_level

    def _lag_matrix(self, series: np.ndarray, lag: int) -> Tuple[np.ndarray, np.ndarray]:
        n = len(series)
        X = np.zeros((n - lag, lag))
        for i in range(lag):
            X[:, i] = series[lag - i - 1: n - i - 1]
        Y = series[lag:]
        return X, Y

    def test_causality(self, x: List[float], y: List[float]) -> GrangerResult:
        if len(x) != len(y) or len(x) <= self.max_lag + 2:
            return GrangerResult(False, 0.0, 1.0, 0)
            
        nx = np.array(x)
        ny = np.array(y)
        
        best_lag = 1
        best_p = 1.0
        best_f = 0.0
        
        for lag in range(1, self.max_lag + 1):
            if len(ny) <= lag + 2:
                break
                
            X_y, Y_u = self._lag_matrix(ny, lag)
            X_x, _ = self._lag_matrix(nx, lag)
            
            X_unrestricted = np.column_stack((np.ones(len(Y_u)), X_y, X_x))
            coeffs_u, residuals_u, _, _ = np.linalg.lstsq(X_unrestricted, Y_u, rcond=None)
            ssr_u = np.sum((Y_u - X_unrestricted @ coeffs_u) ** 2)
            
            X_restricted = np.column_stack((np.ones(len(Y_u)), X_y))
            coeffs_r, residuals_r, _, _ = np.linalg.lstsq(X_restricted, Y_u, rcond=None)
            ssr_r = np.sum((Y_u - X_restricted @ coeffs_r) ** 2)
            
            n = len(Y_u)
            df_r = lag
            df_u = n - (2 * lag + 1)
            
            if df_u > 0 and ssr_u > 0:
                f_stat = ((ssr_r - ssr_u) / df_r) / (ssr_u / df_u)
                p_val = 1 - stats.f.cdf(f_stat, df_r, df_u)
                
                if p_val < best_p:
                    best_p = p_val
                    best_f = f_stat
                    best_lag = lag
                    
        is_causal = best_p < self.significance_level
        return GrangerResult(bool(is_causal), float(best_f), float(best_p), best_lag)

    def build_causality_matrix(self, kpi_series: Dict[str, List[float]]) -> Dict[str, Dict[str, GrangerResult]]:
        keys = list(kpi_series.keys())
        matrix = {k: {} for k in keys}
        for i, k1 in enumerate(keys):
            for j, k2 in enumerate(keys):
                if i != j:
                    matrix[k1][k2] = self.test_causality(kpi_series[k1], kpi_series[k2])
        return matrix
