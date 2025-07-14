# Agent Architecture Refactor Implementation Plan

## Project Context

### Current Architecture Overview

The Cuentamelo project currently has a hybrid agent architecture with:

- `BaseCharacterAgent` - Abstract base class with core functionality
- `JovaniVazquezAgent` - Character-specific implementation with custom logic
- Configuration-driven personality system (recently implemented)
- **Ports and Adapters Pattern** - PersonalityPort interface with concrete implementations

### Current Issues

1. **BaseCharacterAgent not optimized** for configuration-driven personalities
2. **Mixed Responsibilities**: Character agents contain both configuration-driven behavior and custom logic
3. **Inconsistent Patterns**: Some characters use config, others use hardcoded logic
4. **Scalability Concerns**: Adding new characters requires custom agent classes even for simple cases

### Target Architecture

```
Agent Hierarchy (Simplified):
├── BaseCharacterAgent (Enhanced - works with config-driven personalities)
│   └── JovaniVazquezAgent (Only for custom logic)
│
Ports and Adapters:
├── PersonalityPort (Interface)
│   ├── JovaniVazquezPersonality (Custom implementation)
│   └── ConfigurablePersonality (New - works with JSON configs)
```

## Implementation Plan

### Phase 1: Enhance BaseCharacterAgent for Configuration-Driven Personalities

#### 1.1 Update `app/agents/base_character.py`

```python
# Update the existing BaseCharacterAgent to work better with configuration-driven personalities

class BaseCharacterAgent(ABC):
    """
    Enhanced base class for Puerto Rican AI character agents.

    This class now works seamlessly with configuration-driven personalities
    while still supporting custom logic when needed.
    """

    def __init__(
        self,
        character_id: str,
        ai_provider: Optional[AIProviderPort] = None,
        personality: Optional[PersonalityPort] = None
    ):
        self.character_id = character_id

        # Load personality data - use provided personality or get from factory
        if personality:
            self.personality_data = personality
        else:
            self.personality_data = get_personality_by_id(character_id)

        if not self.personality_data:
            raise ValueError(f"No personality data found for character: {character_id}")

        # Inject AI provider dependency
        self.ai_provider = ai_provider

        # Get agent personality data for configuration
        agent_data = self.personality_data.get_agent_personality_data()

        # Character-specific configuration from agent personality data
        self.engagement_threshold = agent_data.engagement_threshold
        self.cooldown_minutes = agent_data.cooldown_minutes
        self.max_daily_interactions = agent_data.max_daily_interactions
        self.max_replies_per_thread = agent_data.max_replies_per_thread
        self.preferred_topics = set(agent_data.preferred_topics)

        # Performance tracking
        self.interaction_count = 0
        self.total_engagements = 0
        self.last_interaction_time: Optional[datetime] = None

    # Enhanced abstract methods with default implementations

    def calculate_engagement_probability(
        self,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        news_item: NewsItem = None
    ) -> float:
        """
        Calculate engagement probability using personality configuration.

        Default implementation uses personality's engagement boost calculation
        and applies standard conversation momentum logic.

        Override this method for custom engagement algorithms.
        """
        # Get base engagement boost from personality
        boosts = self.personality_data.calculate_engagement_boost(context)

        # Apply standard conversation momentum logic
        conversation_boost = self._calculate_conversation_momentum(conversation_history)

        # Apply topic relevance if news item provided
        topic_boost = 0.0
        if news_item and news_item.topics:
            topic_boost = self.personality_data.get_topic_relevance(news_item.topics) * 0.3

        # Calculate final probability
        base_probability = self.engagement_threshold
        final_probability = (
            base_probability +
            boosts.get("energy", 0.0) +
            boosts.get("pr_relevance", 0.0) +
            boosts.get("emotion", 0.0) +
            boosts.get("trending", 0.0) +
            conversation_boost +
            topic_boost
        )

        # Cap at 1.0
        final_probability = min(final_probability, 1.0)

        logger.info(
            f"{self.character_name} engagement calc: base={base_probability}, "
            f"energy={boosts.get('energy', 0.0)}, pr={boosts.get('pr_relevance', 0.0)}, "
            f"conversation={conversation_boost}, topic={topic_boost}, "
            f"final={final_probability}"
        )

        return final_probability

    def get_topic_relevance(self, topics: List[str]) -> float:
        """
        Calculate topic relevance using personality configuration.

        Default implementation delegates to personality.
        Override for custom topic relevance logic.
        """
        return self.personality_data.get_topic_relevance(topics)

    def get_character_specific_context(self, base_context: str) -> str:
        """
        Add character-specific context using personality configuration.

        Default implementation delegates to personality.
        Override for custom context enhancement logic.
        """
        return self.personality_data.get_character_context(base_context)

    def _calculate_conversation_momentum(self, conversation_history: Optional[List[ConversationMessage]]) -> float:
        """
        Calculate conversation momentum boost.

        Standard logic: More recent messages = higher engagement probability.
        Override for custom momentum calculation.
        """
        if not conversation_history or len(conversation_history) == 0:
            return 0.0

        # Look at last 5 messages
        recent_messages = conversation_history[-5:]

        if len(recent_messages) >= 4:
            return 0.2  # High momentum
        elif len(recent_messages) >= 2:
            return 0.1  # Medium momentum
        else:
            return 0.05  # Low momentum

    def _get_fallback_response(self, context: str) -> str:
        """
        Get fallback response using personality configuration.

        Default implementation uses personality fallback responses.
        Override for custom fallback logic.
        """
        import random
        responses = self.personality_data.get_fallback_responses()
        return random.choice(responses) if responses else f"[{self.character_name} response unavailable]"
```

#### 1.2 Create ConfigurablePersonality Adapter

```python
# Create app/models/personalities/configurable_personality.py

"""
Configurable personality implementation that works with JSON configuration.
"""
from typing import Dict, List, Optional, Any
import logging

from app.ports.personality_port import PersonalityPort, PersonalityTone, LanguageStyle
from app.models.personality import PersonalityData
from app.models.ai_personality_data import AIPersonalityData
from app.models.agent_personality_data import AgentPersonalityData
from app.services.personality_config_loader import PersonalityConfigLoader

logger = logging.getLogger(__name__)


class ConfigurablePersonality(PersonalityPort):
    """
    Configurable personality implementation.

    This adapter implements PersonalityPort using JSON configuration,
    making it suitable for most character types that don't require
    custom personality logic.
    """

    def __init__(self, character_id: str, config_loader: Optional[PersonalityConfigLoader] = None):
        # Load personality data from configuration
        self.config_loader = config_loader or PersonalityConfigLoader()
        self._config = self.config_loader.load_personality(character_id)
        self._personality_data = PersonalityData.create_from_config(self._config)

        # Cache for performance
        self._ai_data = None
        self._agent_data = None

    # Property implementations - delegate to personality data

    @property
    def character_id(self) -> str:
        return self._personality_data.character_id

    @property
    def character_name(self) -> str:
        return self._personality_data.character_name

    @property
    def character_type(self) -> str:
        return self._personality_data.character_type

    @property
    def personality_traits(self) -> str:
        return self._personality_data.personality_traits

    @property
    def language_style(self) -> LanguageStyle:
        return self._personality_data.language_style

    @property
    def engagement_threshold(self) -> float:
        return self._personality_data.engagement_threshold

    @property
    def cooldown_minutes(self) -> int:
        return self._personality_data.cooldown_minutes

    @property
    def max_daily_interactions(self) -> int:
        return self._personality_data.max_daily_interactions

    @property
    def max_replies_per_thread(self) -> int:
        return self._personality_data.max_replies_per_thread

    @property
    def topics_of_interest(self) -> List[str]:
        return self._personality_data.topics_of_interest

    @property
    def topic_weights(self) -> Dict[str, float]:
        return self._personality_data.topic_weights

    @property
    def preferred_topics(self) -> List[str]:
        return self._personality_data.preferred_topics

    @property
    def avoided_topics(self) -> List[str]:
        return self._personality_data.avoided_topics

    @property
    def signature_phrases(self) -> List[str]:
        return self._personality_data.signature_phrases

    @property
    def emoji_preferences(self) -> List[str]:
        return self._personality_data.emoji_preferences

    @property
    def base_energy_level(self) -> float:
        return self._personality_data.base_energy_level

    # Method implementations - use configuration data

    def get_topic_relevance(self, topics: List[str]) -> float:
        """Calculate topic relevance from configuration."""
        if not topics:
            return 0.2

        relevance_scores = []
        for topic in topics:
            topic_lower = topic.lower()

            # Check exact matches first
            if topic_lower in self.topic_weights:
                relevance_scores.append(self.topic_weights[topic_lower])
                continue

            # Check partial matches
            max_partial_score = 0.0
            for weighted_topic, weight in self.topic_weights.items():
                if weighted_topic in topic_lower or topic_lower in weighted_topic:
                    max_partial_score = max(max_partial_score, weight * 0.8)

            relevance_scores.append(max_partial_score if max_partial_score > 0 else 0.1)

        return max(relevance_scores) if relevance_scores else 0.2

    def get_emotional_context(self, content: str) -> str:
        """Determine emotional context from configuration."""
        content_lower = content.lower()

        # Use energy level and tone preferences from config
        if self.base_energy_level > 0.7:
            return "excited"
        elif self.base_energy_level < 0.3:
            return "calm"
        else:
            return "neutral"

    def should_engage_in_controversy(self, content: str) -> bool:
        """Determine controversy engagement from configuration."""
        content_lower = content.lower()

        # Check avoided topics
        for topic in self.avoided_topics:
            if topic.lower() in content_lower:
                return False

        # Default to engaging if not clearly avoided
        return True

    def get_response_template(self, response_type: str) -> str:
        """Get response template from configuration."""
        return self._personality_data.response_templates.get(response_type, "")

    def get_example_responses(self, topic: str) -> List[str]:
        """Get example responses from configuration."""
        return self._personality_data.example_responses.get(topic, [])

    def get_character_context(self, base_context: str) -> str:
        """Add character context from configuration."""
        # Add personality traits and background
        context_parts = [
            base_context,
            f"Character: {self.character_name}",
            f"Personality: {self.personality_traits}",
            f"Background: {self._personality_data.background}"
        ]

        # Add signature phrases if available
        if self.signature_phrases:
            context_parts.append(f"Signature phrases: {', '.join(self.signature_phrases[:3])}")

        return "\n".join(context_parts)

    def get_fallback_responses(self) -> List[str]:
        """Get fallback responses from configuration."""
        responses = []

        # Use signature phrases as fallbacks
        if self.signature_phrases:
            responses.extend(self.signature_phrases)

        # Add generic responses
        responses.extend([
            f"¡Hola! {self.character_name} aquí.",
            f"Interesante punto de vista.",
            f"Gracias por compartir eso."
        ])

        return responses

    def calculate_engagement_boost(self, content: str) -> Dict[str, float]:
        """Calculate engagement boost from configuration."""
        content_lower = content.lower()
        boosts = {
            "energy": 0.0,
            "pr_relevance": 0.0,
            "emotion": 0.0,
            "trending": 0.0
        }

        # Energy boost based on base energy level
        boosts["energy"] = self.base_energy_level * 0.3

        # Puerto Rico relevance
        pr_keywords = ["puerto rico", "pr", "borinquen", "boricua"]
        for keyword in pr_keywords:
            if keyword in content_lower:
                boosts["pr_relevance"] = 0.2
                break

        # Topic relevance
        topic_relevance = self.get_topic_relevance([word for word in content_lower.split()])
        boosts["emotion"] = topic_relevance * 0.2

        # Trending keywords
        trending_keywords = ["trending", "viral", "breaking", "#", "@"]
        for keyword in trending_keywords:
            if keyword in content_lower:
                boosts["trending"] = 0.1
                break

        return boosts

    def get_personality_data(self) -> 'PersonalityData':
        """Get full personality data."""
        return self._personality_data

    def get_ai_personality_data(self) -> 'AIPersonalityData':
        """Get AI personality data."""
        if self._ai_data is None:
            self._ai_data = AIPersonalityData.create_from_config(self._config)
        return self._ai_data

    def get_agent_personality_data(self) -> 'AgentPersonalityData':
        """Get agent personality data."""
        if self._agent_data is None:
            self._agent_data = AgentPersonalityData.create_from_config(self._config)
        return self._agent_data


def create_configurable_personality(character_id: str) -> ConfigurablePersonality:
    """Factory function to create configurable personality."""
    return ConfigurablePersonality(character_id)
```

### Phase 2: Update Personality Factory

#### 2.1 Update `app/models/personalities/personality_factory.py`

```python
# Update the existing personality factory to support both custom and configurable personalities

from typing import Optional
from app.ports.personality_port import PersonalityPort
from app.models.personalities.jovani_vazquez_personality import create_jovani_personality
from app.models.personalities.configurable_personality import create_configurable_personality

def get_personality_by_id(character_id: str) -> Optional[PersonalityPort]:
    """
    Get personality implementation by character ID.

    This factory function determines whether to use a custom personality
    implementation or a configurable one based on the character ID.
    """
    # Registry of custom personality creators
    CUSTOM_PERSONALITIES = {
        "jovani_vazquez": create_jovani_personality,
        # Add other custom personalities here as they're created
    }

    # Check if this character has a custom personality implementation
    if character_id in CUSTOM_PERSONALITIES:
        return CUSTOM_PERSONALITIES[character_id]()

    # Default to configurable personality
    try:
        return create_configurable_personality(character_id)
    except Exception as e:
        # Fallback to None if config loading fails
        logger.warning(f"Failed to load configurable personality for {character_id}: {e}")
        return None

def is_custom_personality(character_id: str) -> bool:
    """Check if a character uses a custom personality implementation."""
    CUSTOM_PERSONALITIES = {
        "jovani_vazquez": create_jovani_personality,
    }
    return character_id in CUSTOM_PERSONALITIES

def list_custom_personalities() -> list[str]:
    """Get list of characters that use custom personalities."""
    CUSTOM_PERSONALITIES = {
        "jovani_vazquez": create_jovani_personality,
    }
    return list(CUSTOM_PERSONALITIES.keys())
```

### Phase 3: Simplify JovaniVazquezAgent

#### 3.1 Update `app/agents/jovani_vazquez.py`

```python
"""
Jovani Vázquez AI Character Agent
Energetic Puerto Rican influencer with high engagement and entertaining personality.
"""
from typing import Dict, List, Optional, Any
import re
import logging
from datetime import datetime

from app.agents.base_character import BaseCharacterAgent
from app.models.conversation import ConversationMessage, NewsItem, AgentDecision
from app.models.personalities.jovani_vazquez_personality import create_jovani_personality
from app.ports.personality_port import PersonalityPort

logger = logging.getLogger(__name__)


class JovaniVazquezAgent(BaseCharacterAgent):
    """
    Jovani Vázquez AI Character Agent

    Personality: Energetic Puerto Rican influencer, slightly provocative but entertaining
    Language: Spanglish (Spanish/English mix) with local expressions
    Engagement: High (70% reply rate), quick responses (1-5 minutes)
    Topics: Entertainment, lifestyle, social issues, youth culture

    Custom Logic:
    - Enhanced conversation momentum detection
    - Character-specific engagement algorithms
    - Specialized controversy handling
    """

    def __init__(self, ai_provider=None, personality: Optional[PersonalityPort] = None):
        # Use provided personality or create default
        self.personality = personality or create_jovani_personality()

        super().__init__(
            character_id=self.personality.character_id,
            ai_provider=ai_provider,
            personality=self.personality
        )

    def calculate_engagement_probability(
        self,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        news_item: Optional[NewsItem] = None
    ) -> float:
        """
        Calculate Jovani's engagement probability with custom logic.

        Jovani has enhanced conversation momentum detection and
        character-specific engagement patterns.
        """
        base_probability = 0.4  # Jovani's baseline engagement

        # Get engagement boosts from personality
        boosts = self.personality.calculate_engagement_boost(context)

        # Topic relevance based on news item
        topic_boost = 0.0
        if news_item and news_item.topics:
            topic_boost = self.personality.get_topic_relevance(news_item.topics) * 0.3

        # Enhanced conversation momentum for Jovani
        conversation_boost = self._calculate_jovani_conversation_momentum(conversation_history)

        # Calculate final probability
        final_probability = (
            base_probability +
            boosts["energy"] +
            boosts["pr_relevance"] +
            topic_boost +
            conversation_boost +
            boosts["emotion"] +
            boosts["trending"]
        )

        # Cap at 1.0
        final_probability = min(final_probability, 1.0)

        logger.info(
            f"Jovani engagement calc: base={base_probability}, "
            f"energy={boosts['energy']}, pr={boosts['pr_relevance']}, topic={topic_boost}, "
            f"conversation={conversation_boost}, emotion={boosts['emotion']}, "
            f"trending={boosts['trending']}, final={final_probability}"
        )

        return final_probability

    def get_topic_relevance(self, topics: List[str]) -> float:
        """Calculate topic relevance for Jovani."""
        return self.personality.get_topic_relevance(topics)

    def get_character_specific_context(self, base_context: str) -> str:
        """Add Jovani-specific context and perspective."""
        return self.personality.get_character_context(base_context)

    def _get_fallback_response(self, context: str) -> str:
        """Override with Jovani-specific fallback responses."""
        import random
        responses = self.personality.get_fallback_responses()
        return random.choice(responses)

    def should_engage_in_controversy(self, context: str) -> bool:
        """
        Determine if Jovani should engage with potentially controversial content.

        Jovani is generally open to discussing social issues but avoids heavy politics.
        """
        return self.personality.should_engage_in_controversy(context)

    def get_emotional_context_for_news(self, news_item: NewsItem) -> str:
        """
        Determine emotional context for news reactions.

        Jovani's emotional responses are based on topic relevance and content type.
        """
        if not news_item:
            return "neutral"

        content = f"{news_item.headline} {news_item.content}"
        return self.personality.get_emotional_context(content)

    def _calculate_jovani_conversation_momentum(self, conversation_history: Optional[List[ConversationMessage]]) -> float:
        """
        Jovani-specific conversation momentum calculation.

        Jovani loves active conversations and gets more excited with more participants.
        """
        if not conversation_history or len(conversation_history) == 0:
            return 0.0

        # Look at last 5 messages
        recent_messages = conversation_history[-5:]

        # Count unique participants in recent messages
        unique_participants = set()
        for msg in recent_messages:
            if msg.character_id:
                unique_participants.add(msg.character_id)

        # Jovani gets more excited with more participants
        if len(recent_messages) >= 4 and len(unique_participants) >= 3:
            return 0.3  # High momentum with multiple participants
        elif len(recent_messages) >= 3 and len(unique_participants) >= 2:
            return 0.2  # Medium momentum with multiple participants
        elif len(recent_messages) >= 2:
            return 0.1  # Low momentum
        else:
            return 0.05  # Minimal momentum


def create_jovani_vazquez(ai_provider=None, personality: Optional[PersonalityPort] = None) -> JovaniVazquezAgent:
    """Factory function to create Jovani Vázquez agent."""
    return JovaniVazquezAgent(ai_provider=ai_provider, personality=personality)


# Character information for external access
JOVANI_CHARACTER_INFO = {
    "character_id": "jovani_vazquez",
    "character_name": "Jovani Vázquez",
    "description": "Energetic Puerto Rican influencer",
    "personality_type": "entertainer",
    "engagement_style": "high_energy",
    "primary_topics": ["entertainment", "culture", "lifestyle", "social_media"],
    "language_style": "spanglish",
    "response_speed": "fast",
    "controversy_tolerance": "moderate",
    "agent_type": "custom"  # Indicates this uses custom agent logic
}
```

### Phase 4: Create Simple Agent Factory

#### 4.1 Create `app/agents/agent_factory.py`

```python
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
```

### Phase 5: Update Dependency Container

#### 5.1 Update `app/services/dependency_container.py`

```python
# Add to existing imports
from app.agents.agent_factory import AgentFactory, create_agent

class DependencyContainer:
    def __init__(self):
        # ... existing initialization ...

        # Register agent factory
        self.agent_factory = AgentFactory

        # Register agent creation method
        self.create_agent = create_agent

    def get_agent(self, character_id: str) -> BaseCharacterAgent:
        """
        Get or create a character agent.

        Args:
            character_id: The character's unique identifier

        Returns:
            BaseCharacterAgent: The character agent instance
        """
        # Check if agent already exists in cache
        cache_key = f"agent_{character_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Create new agent
        agent = self.create_agent(
            character_id=character_id,
            ai_provider=self.get_ai_provider(),
            personality=self.get_personality(character_id)
        )

        # Cache the agent
        self._cache[cache_key] = agent

        return agent
```

### Phase 6: Update Tests

#### 6.1 Create `tests/test_agent_factory.py`

```python
"""
Tests for the agent factory and agent creation.
"""
import pytest
from unittest.mock import Mock, patch

from app.agents.agent_factory import AgentFactory, create_agent, is_custom_agent
from app.agents.configurable_character_agent import ConfigurableCharacterAgent
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

        assert isinstance(agent, ConfigurableCharacterAgent)
        assert agent.character_id == "unknown_character"

    def test_is_custom_agent(self):
        """Test custom agent detection."""
        assert is_custom_agent("jovani_vazquez") is True
        assert is_custom_agent("unknown_character") is False

    def test_get_agent_type(self):
        """Test agent type detection."""
        assert AgentFactory.get_agent_type("jovani_vazquez") == "custom"
        assert AgentFactory.get_agent_type("unknown_character") == "configurable"

    def test_list_custom_agents(self):
        """Test listing custom agents."""
        custom_agents = AgentFactory.list_custom_agents()
        assert "jovani_vazquez" in custom_agents
        assert len(custom_agents) >= 1

    def test_register_custom_agent(self):
        """Test registering a custom agent."""
        def create_test_agent(ai_provider=None, personality=None):
            return Mock(spec=ConfigurableCharacterAgent)

        AgentFactory.register_custom_agent("test_character", create_test_agent)

        assert "test_character" in AgentFactory.CUSTOM_AGENT_CREATORS
        assert AgentFactory.get_agent_type("test_character") == "custom"
```

#### 6.2 Create `tests/test_configurable_character_agent.py`

```python
"""
Tests for the configurable character agent.
"""
import pytest
from unittest.mock import Mock, patch

from app.agents.configurable_character_agent import ConfigurableCharacterAgent, create_configurable_agent
from app.models.conversation import ConversationMessage, NewsItem
from app.ports.ai_provider import AIProviderPort
from app.ports.personality_port import PersonalityPort


class TestConfigurableCharacterAgent:
    """Test the configurable character agent."""

    @pytest.fixture
    def mock_personality(self):
        """Create a mock personality."""
        personality = Mock(spec=PersonalityPort)
        personality.character_id = "test_character"
        personality.character_name = "Test Character"
        personality.character_type = "test"
        personality.engagement_threshold = 0.5
        personality.calculate_engagement_boost.return_value = {
            "energy": 0.1,
            "pr_relevance": 0.2,
            "emotion": 0.1,
            "trending": 0.0
        }
        personality.get_topic_relevance.return_value = 0.8
        personality.get_character_context.return_value = "Enhanced context"
        personality.get_fallback_responses.return_value = ["Fallback 1", "Fallback 2"]
        return personality

    @pytest.fixture
    def agent(self, mock_personality):
        """Create a configurable agent for testing."""
        return ConfigurableCharacterAgent(
            character_id="test_character",
            personality=mock_personality
        )

    def test_calculate_engagement_probability(self, agent, mock_personality):
        """Test engagement probability calculation."""
        context = "Test content"

        probability = agent.calculate_engagement_probability(context)

        # Should call personality's calculate_engagement_boost
        mock_personality.calculate_engagement_boost.assert_called_once_with(context)

        # Should return reasonable probability
        assert 0.0 <= probability <= 1.0

    def test_calculate_engagement_probability_with_news(self, agent, mock_personality):
        """Test engagement probability with news item."""
        context = "Test content"
        news_item = NewsItem(
            id="test_news",
            headline="Test Headline",
            content="Test content",
            topics=["entertainment"]
        )

        probability = agent.calculate_engagement_probability(context, news_item=news_item)

        # Should call personality's get_topic_relevance
        mock_personality.get_topic_relevance.assert_called_once_with(["entertainment"])

        # Should return reasonable probability
        assert 0.0 <= probability <= 1.0

    def test_calculate_engagement_probability_with_conversation(self, agent):
        """Test engagement probability with conversation history."""
        context = "Test content"
        conversation_history = [
            ConversationMessage(
                character_id="other_character",
                character_name="Other Character",
                content="Message 1",
                message_type="character_post"
            ),
            ConversationMessage(
                character_id="another_character",
                character_name="Another Character",
                content="Message 2",
                message_type="character_reply"
            )
        ]

        probability = agent.calculate_engagement_probability(context, conversation_history)

        # Should return higher probability due to conversation momentum
        assert probability > 0.5

    def test_get_topic_relevance(self, agent, mock_personality):
        """Test topic relevance delegation."""
        topics = ["entertainment", "music"]

        relevance = agent.get_topic_relevance(topics)

        mock_personality.get_topic_relevance.assert_called_once_with(topics)
        assert relevance == 0.8

    def test_get_character_specific_context(self, agent, mock_personality):
        """Test character context delegation."""
        base_context = "Base context"

        enhanced_context = agent.get_character_specific_context(base_context)

        mock_personality.get_character_context.assert_called_once_with(base_context)
        assert enhanced_context == "Enhanced context"

    def test_get_fallback_response(self, agent, mock_personality):
        """Test fallback response generation."""
        context = "Test context"

        response = agent._get_fallback_response(context)

        mock_personality.get_fallback_responses.assert_called_once()
        assert response in ["Fallback 1", "Fallback 2"]

    def test_conversation_momentum_calculation(self, agent):
        """Test conversation momentum calculation."""
        # No conversation history
        momentum = agent._calculate_conversation_momentum(None)
        assert momentum == 0.0

        # Empty conversation history
        momentum = agent._calculate_conversation_momentum([])
        assert momentum == 0.0

        # Single message
        conversation = [ConversationMessage(
            character_id="test",
            character_name="Test",
            content="Test",
            message_type="character_post"
        )]
        momentum = agent._calculate_conversation_momentum(conversation)
        assert momentum == 0.05

        # Multiple messages
        conversation = [
            ConversationMessage(character_id="test", character_name="Test", content="Test", message_type="character_post"),
            ConversationMessage(character_id="test2", character_name="Test2", content="Test2", message_type="character_reply"),
            ConversationMessage(character_id="test3", character_name="Test3", content="Test3", message_type="character_reply"),
            ConversationMessage(character_id="test4", character_name="Test4", content="Test4", message_type="character_reply")
        ]
        momentum = agent._calculate_conversation_momentum(conversation)
        assert momentum == 0.2


class TestConfigurableAgentFactory:
    """Test the configurable agent factory function."""

    def test_create_configurable_agent(self):
        """Test creating configurable agent."""
        ai_provider = Mock(spec=AIProviderPort)
        personality = Mock(spec=PersonalityPort)

        agent = create_configurable_agent(
            character_id="test_character",
            ai_provider=ai_provider,
            personality=personality
        )

        assert isinstance(agent, ConfigurableCharacterAgent)
        assert agent.character_id == "test_character"
        assert agent.ai_provider == ai_provider
        assert agent.personality_data == personality
```

### Phase 7: Update Documentation

#### 7.1 Create `docs/agent_architecture.md`

```markdown
# Agent Architecture Documentation

## Overview

The Cuentamelo project uses a hybrid agent architecture that supports both configuration-driven and custom character agents.

## Agent Hierarchy
```

BaseCharacterAgent (Abstract)
├── ConfigurableCharacterAgent (New - handles 80% of cases)
└── CustomCharacterAgent (New - for complex logic)
└── JovaniVazquezAgent (Refactored - only custom logic)

````

## When to Use Each Agent Type

### ConfigurableCharacterAgent

Use for characters that:
- Can be fully defined by personality configuration
- Don't require custom engagement algorithms
- Use standard conversation momentum logic
- Don't have complex behavioral patterns

**Example Usage:**
```python
from app.agents.agent_factory import create_agent

# Creates a configurable agent automatically
agent = create_agent("simple_character_id")
````

### CustomCharacterAgent

Use for characters that:

- Require custom engagement algorithms
- Have specialized decision-making logic
- Need complex behavioral patterns
- Require character-specific response generation

**Example Usage:**

```python
from app.agents.jovani_vazquez import create_jovani_vazquez

# Creates a custom agent with Jovani's specific logic
agent = create_jovani_vazquez()
```

## Creating New Characters

### Simple Character (Configurable)

1. Create JSON configuration in `configs/personalities/`
2. Use the agent factory:
   ```python
   agent = create_agent("new_character_id")
   ```

### Complex Character (Custom)

1. Create JSON configuration in `configs/personalities/`
2. Create personality implementation in `app/models/personalities/`
3. Create custom agent class extending `CustomCharacterAgent`
4. Register with agent factory:

   ```python
   from app.agents.agent_factory import AgentFactory

   def create_custom_agent(ai_provider=None, personality=None):
       return CustomAgent(ai_provider=ai_provider, personality=personality)

   AgentFactory.register_custom_agent("custom_character_id", create_custom_agent)
   ```

## Migration Guide

### From Old Agent Classes

1. **Simple agents**: Replace with `ConfigurableCharacterAgent`
2. **Complex agents**: Extend `CustomCharacterAgent` instead of `BaseCharacterAgent`
3. **Update imports**: Use agent factory for creation

### Example Migration

**Before:**

```python
class OldCharacterAgent(BaseCharacterAgent):
    def calculate_engagement_probability(self, context, ...):
        # Simple delegation to personality
        return self.personality.calculate_engagement_boost(context)
```

**After:**

```python
# No custom class needed - use ConfigurableCharacterAgent
agent = create_agent("character_id")
```

## Testing

- `tests/test_agent_factory.py` - Agent factory tests
- `tests/test_configurable_character_agent.py` - Configurable agent tests
- `tests/test_jovani_vazquez.py` - Custom agent tests (existing)

## Performance Considerations

- Configurable agents are lightweight and fast
- Custom agents may have additional overhead
- Agent factory caches agent instances
- Personality data is cached by the config loader

```

## Implementation Checklist

### Phase 1: Enhance BaseCharacterAgent
- [ ] Update `app/agents/base_character.py` with default implementations
- [ ] Remove abstract method requirements for common operations
- [ ] Add conversation momentum calculation
- [ ] Update tests for enhanced base class

### Phase 2: Create ConfigurablePersonality
- [ ] Create `app/models/personalities/configurable_personality.py`
- [ ] Implement PersonalityPort interface using JSON configs
- [ ] Add comprehensive tests
- [ ] Update personality factory

### Phase 3: Simplify JovaniVazquezAgent
- [ ] Update to extend enhanced `BaseCharacterAgent`
- [ ] Remove duplicated code that's now in base class
- [ ] Keep only Jovani-specific custom logic
- [ ] Update tests

### Phase 4: Create Simple Agent Factory
- [ ] Create `app/agents/agent_factory.py`
- [ ] Implement simple factory function
- [ ] Add registry for custom agents
- [ ] Create convenience functions

### Phase 5: Update Dependency Container
- [ ] Update `app/services/dependency_container.py`
- [ ] Add agent factory integration
- [ ] Add agent caching
- [ ] Update service registration

### Phase 6: Testing
- [ ] Create `tests/test_agent_factory.py`
- [ ] Create `tests/test_configurable_personality.py`
- [ ] Update existing agent tests
- [ ] Add integration tests

### Phase 7: Documentation
- [ ] Create `docs/agent_architecture.md`
- [ ] Update README files
- [ ] Add migration guide
- [ ] Document best practices

## Success Criteria

✅ **Configuration-Driven**: 80% of characters use enhanced BaseCharacterAgent
✅ **Custom Logic Support**: Complex characters can have custom behavior
✅ **Ports and Adapters**: Clean separation using PersonalityPort interface
✅ **Easy Scaling**: Adding new characters is simple
✅ **Backward Compatible**: Existing code continues to work
✅ **Well Tested**: Comprehensive test coverage
✅ **Well Documented**: Clear documentation for developers

## Files to Create/Modify

### New Files
- `app/models/personalities/configurable_personality.py`
- `app/agents/agent_factory.py`
- `tests/test_agent_factory.py`
- `tests/test_configurable_personality.py`
- `docs/agent_architecture.md`

### Modified Files
- `app/agents/base_character.py` (enhance with default implementations)
- `app/agents/jovani_vazquez.py` (simplify to only custom logic)
- `app/models/personalities/personality_factory.py` (add configurable support)
- `app/services/dependency_container.py` (add agent factory)
- `tests/test_jovani_vazquez.py` (update)

This implementation plan provides a complete roadmap for refactoring the agent architecture to support both configuration-driven and custom character agents while maintaining clean separation of concerns and easy scalability.
```
