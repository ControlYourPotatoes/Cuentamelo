"""
Simple factory for creating character agents.
"""
from typing import Optional
import logging

from app.ports.ai_provider import AIProviderPort
from app.ports.personality_port import PersonalityPort
from app.agents.base_character import BaseCharacterAgent
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.personalities.personality_factory import get_personality_by_id

logger = logging.getLogger(__name__)


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