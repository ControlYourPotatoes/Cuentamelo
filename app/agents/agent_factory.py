"""
Simple factory for creating character agents.
"""
from typing import Optional, Dict, List
import logging
import os

from app.ports.ai_provider import AIProviderPort
from app.ports.personality_port import PersonalityPort
from app.agents.base_character import BaseCharacterAgent
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.personalities.personality_factory import get_personality_by_id

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory class for creating and managing character agents.
    
    This class provides a centralized interface for agent creation and management,
    wrapping the existing factory functions to provide a class-based API.
    """
    
    def __init__(self):
        """Initialize the agent factory."""
        # Warn if running in mock mode outside of test context
        if os.environ.get("CUENTAMELO_AGENT_FACTORY_MODE") == "mock" and not os.environ.get("PYTEST_CURRENT_TEST"):
            logger.warning("AgentFactory is running in mock mode outside of test context! This should only be used for tests.")
        self._active_agents: Dict[str, BaseCharacterAgent] = {}
        self._custom_agent_creators = {
            "jovani_vazquez": create_jovani_vazquez,
            # Add other custom agents here as they're created
        }
    
    def create_agent(
        self,
        character_id: str,
        ai_provider: Optional[AIProviderPort] = None,
        personality: Optional[PersonalityPort] = None
    ) -> BaseCharacterAgent:
        """
        Create a character agent based on character ID.

        This factory method determines whether to use a custom agent
        or the enhanced BaseCharacterAgent based on the character ID.

        Args:
            character_id: The character's unique identifier
            ai_provider: Optional AI provider for the agent
            personality: Optional personality implementation

        Returns:
            BaseCharacterAgent: The created agent instance

        Raises:
            ValueError: If character_id is not recognized
        """
        # Check if this character has a custom agent implementation
        if character_id in self._custom_agent_creators:
            logger.info(f"Creating custom agent for character: {character_id}")
            agent = self._custom_agent_creators[character_id](
                ai_provider=ai_provider,
                personality=personality
            )
        else:
            # Default to enhanced BaseCharacterAgent
            logger.info(f"Creating standard agent for character: {character_id}")

            # Get personality if not provided
            if not personality:
                personality = get_personality_by_id(character_id)
                if not personality:
                    raise ValueError(f"No personality found for character: {character_id}")

            # Create standard agent using enhanced BaseCharacterAgent
            agent = BaseCharacterAgent(
                character_id=character_id,
                ai_provider=ai_provider,
                personality=personality
            )
        
        # Store the agent as active
        self._active_agents[character_id] = agent
        return agent
    
    def get_agent(self, character_id: str) -> Optional[BaseCharacterAgent]:
        """
        Get an existing agent by character ID.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            BaseCharacterAgent: The agent instance if found, None otherwise
        """
        return self._active_agents.get(character_id)
    
    def get_all_agents(self) -> Dict[str, BaseCharacterAgent]:
        """
        Get all active agents.
        
        Returns:
            Dict[str, BaseCharacterAgent]: Dictionary of all active agents
        """
        return self._active_agents.copy()
    
    def get_active_agents(self) -> List[str]:
        """
        Get list of active agent IDs.
        
        Returns:
            List[str]: List of active agent character IDs
        """
        return list(self._active_agents.keys())
    
    def is_custom_agent(self, character_id: str) -> bool:
        """Check if a character uses a custom agent."""
        return character_id in self._custom_agent_creators
    
    def list_custom_agents(self) -> List[str]:
        """Get list of characters that use custom agents."""
        return list(self._custom_agent_creators.keys())
    
    def register_custom_agent(self, character_id: str, creator_func):
        """
        Register a custom agent creator function.
        
        Args:
            character_id: The character's unique identifier
            creator_func: Function that creates the custom agent
        """
        self._custom_agent_creators[character_id] = creator_func
        logger.info(f"Registered custom agent creator for: {character_id}")


# Legacy function-based interface for backward compatibility
def create_agent(
    character_id: str,
    ai_provider: Optional[AIProviderPort] = None,
    personality: Optional[PersonalityPort] = None
) -> BaseCharacterAgent:
    """
    Create a character agent based on character ID.

    This factory function determines whether to use a custom agent
    or the enhanced BaseCharacterAgent based on the character ID.

    Args:
        character_id: The character's unique identifier
        ai_provider: Optional AI provider for the agent
        personality: Optional personality implementation

    Returns:
        BaseCharacterAgent: The created agent instance

    Raises:
        ValueError: If character_id is not recognized
    """
    # Registry of custom agent creators
    CUSTOM_AGENT_CREATORS = {
        "jovani_vazquez": create_jovani_vazquez,
        # Add other custom agents here as they're created
    }

    # Check if this character has a custom agent implementation
    if character_id in CUSTOM_AGENT_CREATORS:
        logger.info(f"Creating custom agent for character: {character_id}")
        return CUSTOM_AGENT_CREATORS[character_id](
            ai_provider=ai_provider,
            personality=personality
        )

    # Default to enhanced BaseCharacterAgent
    logger.info(f"Creating standard agent for character: {character_id}")

    # Get personality if not provided
    if not personality:
        personality = get_personality_by_id(character_id)
        if not personality:
            raise ValueError(f"No personality found for character: {character_id}")

    # Create standard agent using enhanced BaseCharacterAgent
    return BaseCharacterAgent(
        character_id=character_id,
        ai_provider=ai_provider,
        personality=personality
    )


def is_custom_agent(character_id: str) -> bool:
    """Check if a character uses a custom agent."""
    CUSTOM_AGENT_CREATORS = {
        "jovani_vazquez": create_jovani_vazquez,
    }
    return character_id in CUSTOM_AGENT_CREATORS


def list_custom_agents() -> list[str]:
    """Get list of characters that use custom agents."""
    CUSTOM_AGENT_CREATORS = {
        "jovani_vazquez": create_jovani_vazquez,
    }
    return list(CUSTOM_AGENT_CREATORS.keys()) 