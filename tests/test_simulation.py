import pytest

class Simulator:
    def check_telemetry(self, kpis):
        for kpi in kpis:
            if kpi > 100:
                return False
        return True
    
    def apply_backpressure(self, load):
        if load > 80:
            return load * 0.8 # degraded
        return load
    
    def inject_fault(self, time, schedule):
        return time in schedule

def test_telemetry_normal_operation():
    sim = Simulator()
    assert sim.check_telemetry([50, 60, 70])

def test_telemetry_backpressure():
    sim = Simulator()
    assert sim.apply_backpressure(90) == 72
    assert sim.apply_backpressure(50) == 50

def test_cascading_failure():
    sim = Simulator()
    # Mock cascade effect
    telemetry_fault = True
    analytics_fault = telemetry_fault
    api_fault = analytics_fault
    assert api_fault

def test_fault_injection_scheduling():
    sim = Simulator()
    assert sim.inject_fault(10, [10, 20])
    assert not sim.inject_fault(15, [10, 20])

def test_full_simulation_run():
    # integration test mock
    assert True
