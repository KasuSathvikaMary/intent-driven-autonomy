import math
import random

class TelemetryIntent:
    def __init__(self, queue_capacity: int = 1000):
        self.queue_capacity = queue_capacity
        self.queue_depth = 0.0
        self.arrival_rate = 100.0  # msgs per sec
        self.service_rate = 120.0  # msgs per sec (normal)
        self.fault_severity = 0.0

    def inject_backpressure_fault(self, severity: float):
        self.fault_severity = min(1.0, max(0.0, severity))
        # Severity degrades service rate
        self.service_rate = 120.0 * (1.0 - self.fault_severity * 0.8)

    def step(self, dt: float):
        # M/M/1 queue approximation
        arrivals = self.arrival_rate * dt
        services = self.service_rate * dt
        
        self.queue_depth += arrivals - services
        if self.queue_depth < 0:
            self.queue_depth = 0
        if self.queue_depth > self.queue_capacity:
            self.queue_depth = self.queue_capacity

    def generate_kpis(self) -> dict[str, float]:
        # Little's law: L = lambda * W => W = L / lambda
        latency = (self.queue_depth / self.arrival_rate) if self.arrival_rate > 0 else 0.0
        throughput = min(self.arrival_rate, self.service_rate)
        error_rate = (self.queue_depth / self.queue_capacity) * 0.1 # errors increase as queue fills
        return {
            "queue_depth": self.queue_depth,
            "throughput": throughput,
            "latency": latency,
            "error_rate": error_rate
        }

class AnalyticsIntent:
    def __init__(self, telemetry: TelemetryIntent):
        self.telemetry = telemetry
        self.inference_throughput = 50.0
        self.base_latency = 0.05
        
    def step(self, dt: float):
        pass # state is derived mostly from telemetry

    def generate_kpis(self) -> dict[str, float]:
        telemetry_kpis = self.telemetry.generate_kpis()
        
        # If telemetry latency is high, analytics latency spikes due to starvation/batching issues
        tel_latency = telemetry_kpis["latency"]
        model_latency = self.base_latency + tel_latency * 1.5
        
        # Accuracy degrades if telemetry has errors
        accuracy = 0.95 - (telemetry_kpis["error_rate"] * 0.5)
        
        inference_throughput = self.inference_throughput
        if telemetry_kpis["throughput"] < self.inference_throughput:
            inference_throughput = telemetry_kpis["throughput"]

        return {
            "inference_throughput": inference_throughput,
            "model_latency": model_latency,
            "accuracy": max(0.0, accuracy),
            "queue_wait": tel_latency
        }

class APIGatewayIntent:
    def __init__(self, analytics: AnalyticsIntent):
        self.analytics = analytics
        self.request_rate = 200.0
        
    def step(self, dt: float):
        pass # derived state

    def generate_kpis(self) -> dict[str, float]:
        analytics_kpis = self.analytics.generate_kpis()
        
        # Gateway latency includes analytics latency
        response_latency = 0.02 + analytics_kpis["model_latency"]
        
        # Errors propagate
        error_rate = 0.01
        if analytics_kpis["accuracy"] < 0.9:
            error_rate += (0.9 - analytics_kpis["accuracy"])
            
        sla_compliance = 1.0
        if response_latency > 0.5:
            sla_compliance -= 0.5
        if error_rate > 0.05:
            sla_compliance -= 0.5
            
        return {
            "response_latency": response_latency,
            "request_rate": self.request_rate,
            "error_rate": error_rate,
            "sla_compliance": max(0.0, sla_compliance)
        }
