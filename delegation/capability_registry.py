from typing import List, Optional
from delegation.models import Agent

class AgentCapabilityRegistry:
    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def find_capable_agents(self, required_capabilities: List[str], min_trust: float) -> List[Agent]:
        capable = []
        for agent in self._agents.values():
            if agent.trust_score >= min_trust:
                # Check if agent has all required capabilities
                if all(cap in agent.capabilities for cap in required_capabilities):
                    capable.append(agent)
        return capable

    def get_load_balanced_agent(self, capable_agents: List[Agent]) -> Optional[Agent]:
        if not capable_agents:
            return None
        # Sort by load and pick the one with least load. If tie, use trust score.
        return min(capable_agents, key=lambda a: (a.current_load, -a.trust_score))

    def update_trust_score(self, agent_id: str, task_success: bool):
        agent = self.get_agent(agent_id)
        if not agent:
            return
            
        # Bayesian trust update (simplified)
        alpha, beta = 2.0, 2.0 # prior
        # Map current trust score to an equivalent number of successes out of total
        total = 10.0
        successes = agent.trust_score * total
        
        if task_success:
            successes += 1.0
        total += 1.0
        
        agent.trust_score = successes / total
        agent.trust_score = max(0.0, min(1.0, agent.trust_score))
