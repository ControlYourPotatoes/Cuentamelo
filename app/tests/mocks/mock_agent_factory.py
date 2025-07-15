"""
Mock AgentFactory for testing.
"""
from typing import Optional, Dict, List
from app.ports.ai_provider import AIProviderPort
from app.ports.personality_port import PersonalityPort
from app.agents.base_character import BaseCharacterAgent

class MockAgentFactory:
    def __init__(self):
        self._active_agents: Dict[str, BaseCharacterAgent] = {}
    def create_agent(self, character_id: str, ai_provider: Optional[AIProviderPort] = None, personality: Optional[PersonalityPort] = None) -> BaseCharacterAgent:
        # Return a dummy BaseCharacterAgent or a stub
        return BaseCharacterAgent(character_id=character_id, ai_provider=ai_provider, personality=personality)
    def get_agent(self, character_id: str) -> Optional[BaseCharacterAgent]:
        return self._active_agents.get(character_id)
    def get_all_agents(self) -> Dict[str, BaseCharacterAgent]:
        return self._active_agents.copy()
    def get_active_agents(self) -> List[str]:
        return list(self._active_agents.keys())
    def is_custom_agent(self, character_id: str) -> bool:
        return False
    def list_custom_agents(self) -> List[str]:
        return []
    def register_custom_agent(self, character_id: str, creator_func):
        pass 