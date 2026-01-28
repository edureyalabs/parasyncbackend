from typing import Dict
from living_agent import LivingAgent
from datetime import datetime, timedelta
from config import AGENT_CONFIG

class AgentManager:
    def __init__(self):
        self.active_agents: Dict[str, LivingAgent] = {}
    
    def _get_agent_key(self, user_id: str, agent_id: str) -> str:
        return f"{user_id}:{agent_id}"
    
    async def get_or_create_agent(self, user_id: str, agent_id: str) -> LivingAgent:
        key = self._get_agent_key(user_id, agent_id)
        
        if key not in self.active_agents:
            agent = LivingAgent(user_id, agent_id)
            await agent.initialize()
            self.active_agents[key] = agent
        else:
            self.active_agents[key].last_activity = datetime.now()
        
        return self.active_agents[key]
    
    async def shutdown_agent(self, user_id: str, agent_id: str):
        key = self._get_agent_key(user_id, agent_id)
        
        if key in self.active_agents:
            await self.active_agents[key].shutdown()
            del self.active_agents[key]
    
    async def cleanup_idle_agents(self):
        idle_threshold = datetime.now() - timedelta(seconds=AGENT_CONFIG["agent_idle_timeout"])
        
        keys_to_remove = []
        
        for key, agent in self.active_agents.items():
            if agent.last_activity < idle_threshold and not agent.active_tasks:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            await self.active_agents[key].shutdown()
            del self.active_agents[key]
    
    def get_active_agent_count(self) -> int:
        return len(self.active_agents)

agent_manager = AgentManager()