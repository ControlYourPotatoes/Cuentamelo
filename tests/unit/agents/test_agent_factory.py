"""
Tests for the agent factory and agent creation.
"""
import pytest
from unittest.mock import Mock, patch

from app.agents.agent_factory import create_agent, is_custom_agent, list_custom_agents
from app.agents.base_character import BaseCharacterAgent
from app.agents.jovani_vazquez import JovaniVazquezAgent
from app.ports.ai_provider import AIProviderPort
from app.ports.personality_port import PersonalityPort


class TestAgentFactory:
    """Test the agent factory functionality."""

    def test_create_jovani_agent(self):
        """Test creating Jovani agent returns custom agent."""
        ai_provider = Mock(spec=AIProviderPort)

        agent = create_agent("jovani_vazquez", ai_provider=ai_provider)

        assert isinstance(agent, JovaniVazquezAgent)
        assert agent.character_id == "jovani_vazquez"

    def test_create_unknown_agent(self):
        """Test creating unknown agent returns configurable agent."""
        ai_provider = Mock(spec=AIProviderPort)

        agent = create_agent("unknown_character", ai_provider=ai_provider)

        assert isinstance(agent, BaseCharacterAgent)
        assert agent.character_id == "unknown_character"

    def test_is_custom_agent(self):
        """Test custom agent detection."""
        assert is_custom_agent("jovani_vazquez") is True
        assert is_custom_agent("unknown_character") is False

    def test_list_custom_agents(self):
        """Test listing custom agents."""
        custom_agents = list_custom_agents()
        assert "jovani_vazquez" in custom_agents
        assert len(custom_agents) >= 1

    def test_create_agent_with_personality(self):
        """Test creating agent with provided personality."""
        ai_provider = Mock(spec=AIProviderPort)
        personality = Mock(spec=PersonalityPort)
        personality.character_id = "test_character"

        agent = create_agent("test_character", ai_provider=ai_provider, personality=personality)

        assert isinstance(agent, BaseCharacterAgent)
        assert agent.character_id == "test_character"

    def test_create_agent_no_personality_found(self):
        """Test error handling when no personality is found."""
        with pytest.raises(ValueError, match="No personality found for character"):
            create_agent("nonexistent_character") 