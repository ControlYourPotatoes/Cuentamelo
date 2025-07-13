"""
AI Provider Port - Interface for AI personality generation services.
This abstracts away the specific AI provider (Claude, OpenAI, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.conversation import ConversationMessage
from app.models.personality import PersonalityData


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
        personality_data: PersonalityData,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        target_topic: Optional[str] = None,
        thread_context: Optional[str] = None,
        is_new_thread: bool = True
    ) -> AIResponse:
        """
        Generate a character response based on personality and context.
        
        Args:
            personality_data: Complete personality configuration for the character
            context: Content to respond to
            conversation_history: Previous conversation messages
            target_topic: Specific topic to focus on
            thread_context: Context from existing thread (if replying)
            is_new_thread: Whether this is a new thread or reply
        """
        pass
    
    @abstractmethod
    async def generate_news_reaction(
        self,
        personality_data: PersonalityData,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> AIResponse:
        """Generate a character's reaction to news."""
        pass
    
    @abstractmethod
    async def validate_personality_consistency(
        self,
        personality_data: PersonalityData,
        generated_content: str
    ) -> bool:
        """Validate that content maintains character consistency."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the AI provider is available."""
        pass 