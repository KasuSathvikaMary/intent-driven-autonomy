import pytest

class DelegationEnvelope:
    def check_bounds(self, agent_caps, required_caps):
        return set(required_caps).issubset(set(agent_caps))
    
    def match_capability(self, agents, required_caps):
        capable_agents = []
        for agent in agents:
            if set(required_caps).issubset(set(agent["caps"])):
                capable_agents.append(agent["id"])
        return capable_agents
    
    def update_trust(self, current_trust, success, alpha=0.1):
        if success:
            return current_trust + alpha * (1 - current_trust)
        else:
            return current_trust - alpha * current_trust
    
    def detect_misdelegation(self, agent_history):
        fail_rate = agent_history.count("fail") / len(agent_history) if agent_history else 0
        return fail_rate > 0.5
    
    def trigger_escalation(self, violation_count):
        return violation_count >= 3
    
    def load_balance(self, agents):
        return min(agents, key=lambda x: x["load"])["id"]

def test_envelope_within_bounds():
    env = DelegationEnvelope()
    assert env.check_bounds(["search", "read", "write"], ["search"])

def test_envelope_violation():
    env = DelegationEnvelope()
    assert not env.check_bounds(["read"], ["write"])

def test_capability_matching():
    env = DelegationEnvelope()
    agents = [{"id": "A1", "caps": ["search"]}, {"id": "A2", "caps": ["write", "search"]}]
    assert env.match_capability(agents, ["search", "write"]) == ["A2"]

def test_trust_score_update():
    env = DelegationEnvelope()
    assert env.update_trust(0.5, True) == 0.55
    assert env.update_trust(0.5, False) == 0.45

def test_misdelegation_detection():
    env = DelegationEnvelope()
    assert env.detect_misdelegation(["fail", "fail", "success"])
    assert not env.detect_misdelegation(["success", "success", "fail"])

def test_escalation_trigger():
    env = DelegationEnvelope()
    assert env.trigger_escalation(3)
    assert not env.trigger_escalation(2)

def test_load_balancing():
    env = DelegationEnvelope()
    agents = [{"id": "A1", "load": 10}, {"id": "A2", "load": 2}]
    assert env.load_balance(agents) == "A2"
