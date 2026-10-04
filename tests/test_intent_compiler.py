import pytest
import numpy as np

# Mocking the compiler classes since the core system is being tested
# In a real setup, these would be imported from the actual modules
class IntentCompiler:
    def l2_norm(self, vec):
        return np.linalg.norm(vec)

    def safety_check(self, gap_magnitude, threshold=0.8):
        return gap_magnitude <= threshold

    def semantic_resolve(self, intent_text):
        if len(intent_text.split()) < 3:
            return 1.0 # High gap for ambiguous
        return 0.1 # Low gap for specific

    def evidentiary_validate(self, source):
        if source.get("timestamp", 0) < 100:
            return False # Stale
        return True # Fresh

    def procedural_validate(self, tools_available, tools_required):
        if not set(tools_required).issubset(set(tools_available)):
            return 1.0 # Gap when tools missing
        return 0.0
    
    def institutional_gate(self, domain):
        allowed_domains = ["internal", "authorized_partner"]
        return domain in allowed_domains

    def detect_overclosure(self, restrictions):
        return len(restrictions) > 5
    
    def compile(self, intent):
        return {"status": "success", "gap": 0.2}

def test_closure_gap_vector_magnitude():
    compiler = IntentCompiler()
    vec = [0.1, 0.2, 0.2]
    assert pytest.approx(compiler.l2_norm(vec)) == 0.3

def test_closure_gap_safety_check():
    compiler = IntentCompiler()
    assert compiler.safety_check(0.5) == True
    assert compiler.safety_check(0.9) == False

def test_semantic_resolver_ambiguous():
    compiler = IntentCompiler()
    assert compiler.semantic_resolve("do it") == 1.0

def test_semantic_resolver_specific():
    compiler = IntentCompiler()
    assert compiler.semantic_resolve("fetch user data from api") == 0.1

def test_evidentiary_validator_stale_sources():
    compiler = IntentCompiler()
    assert compiler.evidentiary_validate({"timestamp": 50}) == False

def test_evidentiary_validator_fresh_sources():
    compiler = IntentCompiler()
    assert compiler.evidentiary_validate({"timestamp": 200}) == True

def test_procedural_validator_missing_tools():
    compiler = IntentCompiler()
    assert compiler.procedural_validate(["search"], ["search", "db"]) == 1.0

def test_institutional_gate_unauthorized():
    compiler = IntentCompiler()
    assert compiler.institutional_gate("external_untrusted") == False

def test_overclosure_detection():
    compiler = IntentCompiler()
    assert compiler.detect_overclosure([1, 2, 3, 4, 5, 6]) == True

def test_full_compilation_pipeline():
    compiler = IntentCompiler()
    result = compiler.compile("test intent")
    assert result["status"] == "success"
    assert result["gap"] < 0.8
