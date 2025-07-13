"""
AI Provider Port - Interface for AI personality generation services.
This abstracts away the specific AI provider (Claude, OpenAI, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.conversation import ConversationMessage


class PersonalityConfig(BaseModel):
    """Configuration for AI personality generation."""
    character_name: str
    personality_traits: str
    background: str
    language_style: str
    topics_of_interest: List[str]
    interaction_style: str
    cultural_context: str


class AIResponse(BaseModel):
    """Standardized response from AI provider."""
    content: str
    confidence_score: float
    character_consistency: bool
    metadata: Dict[str, Any]


class AIProviderPort(ABC):
    """
    Port (Interface) for AI personality generation services.
    
    This allows us to swap between different AI providers (Claude, OpenAI, local models)
    without changing the core business logic.
    """
    
    @abstractmethod
    async def generate_character_response(
        self,
        personality_config: PersonalityConfig,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        target_topic: Optional[str] = None
    ) -> AIResponse:
        """Generate a character response based on personality and context."""
        pass
    
    @abstractmethod
    async def generate_news_reaction(
        self,
        personality_config: PersonalityConfig,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> AIResponse:
        """Generate a character's reaction to news."""
        pass
    
    @abstractmethod
    async def validate_personality_consistency(
        self,
        personality_config: PersonalityConfig,
        generated_content: str
    ) -> bool:
        """Validate that content maintains character consistency."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the AI provider is available."""
        pass 