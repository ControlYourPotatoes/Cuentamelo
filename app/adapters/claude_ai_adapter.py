"""
Claude AI Adapter - Implements AIProviderPort using Anthropic Claude API.
This is the "adapter" that connects our port to the external Claude service.
"""
from typing import List, Dict, Any, Optional
import logging

from app.ports.ai_provider import AIProviderPort, PersonalityConfig, AIResponse
from app.models.conversation import ConversationMessage
from app.tools.claude_client import ClaudeClient, PersonalityPrompt

logger = logging.getLogger(__name__)


class ClaudeAIAdapter(AIProviderPort):
    """
    Adapter that implements AIProviderPort using Claude API.
    
    This demonstrates the Adapter pattern by:
    - Implementing the standard AIProviderPort interface
    - Translating between our domain models and Claude's API
    - Handling Claude-specific logic and error handling
    """
    
    def __init__(self, claude_client: Optional[ClaudeClient] = None):
        """
        Initialize with dependency injection.
        
        Args:
            claude_client: Injected Claude client (for testing/flexibility)
        """
        self.claude_client = claude_client or ClaudeClient()
    
    async def generate_character_response(
        self,
        personality_config: PersonalityConfig,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        target_topic: Optional[str] = None
    ) -> AIResponse:
        """Generate character response using Claude API."""
        try:
            # Convert our domain model to Claude's format
            claude_prompt = self._convert_to_claude_prompt(personality_config)
            
            # Convert conversation history to Claude format
            claude_history = []
            if conversation_history:
                claude_history = [
                    {
                        "speaker": msg.character_name,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in conversation_history[-10:]  # Last 10 messages
                ]
            
            # Call Claude API
            claude_response = await self.claude_client.generate_character_response(
                character_prompt=claude_prompt,
                context=context,
                conversation_history=claude_history,
                target_topic=target_topic
            )
            
            # Convert Claude response to our domain model
            return AIResponse(
                content=claude_response.content,
                confidence_score=claude_response.confidence_score,
                character_consistency=claude_response.character_consistency,
                metadata={
                    "estimated_tokens": claude_response.estimated_tokens,
                    "response_time_ms": claude_response.response_time_ms,
                    "provider": "claude",
                    "model": self.claude_client.model
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Claude adapter: {str(e)}")
            # Return fallback response
            return AIResponse(
                content=f"[Error generating response for {personality_config.character_name}]",
                confidence_score=0.0,
                character_consistency=False,
                metadata={"error": str(e), "provider": "claude"}
            )
    
    async def generate_news_reaction(
        self,
        personality_config: PersonalityConfig,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> AIResponse:
        """Generate news reaction using Claude API."""
        try:
            claude_prompt = self._convert_to_claude_prompt(personality_config)
            
            claude_response = await self.claude_client.generate_news_reaction(
                character_prompt=claude_prompt,
                news_headline=news_headline,
                news_content=news_content,
                emotional_context=emotional_context
            )
            
            return AIResponse(
                content=claude_response.content,
                confidence_score=claude_response.confidence_score,
                character_consistency=claude_response.character_consistency,
                metadata={
                    "estimated_tokens": claude_response.estimated_tokens,
                    "response_time_ms": claude_response.response_time_ms,
                    "provider": "claude",
                    "emotional_context": emotional_context
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Claude news reaction: {str(e)}")
            return AIResponse(
                content="",
                confidence_score=0.0,
                character_consistency=False,
                metadata={"error": str(e), "provider": "claude"}
            )
    
    async def validate_personality_consistency(
        self,
        personality_config: PersonalityConfig,
        generated_content: str
    ) -> bool:
        """Validate personality consistency using Claude."""
        try:
            claude_prompt = self._convert_to_claude_prompt(personality_config)
            return await self.claude_client._validate_personality_consistency(
                claude_prompt, generated_content
            )
        except Exception as e:
            logger.error(f"Error validating consistency: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Claude API is available."""
        try:
            # Simple test call to verify API connectivity
            test_prompt = PersonalityPrompt(
                character_name="Test",
                personality_traits="Test personality",
                background="Test background",
                language_style="English",
                topics_of_interest=["test"],
                interaction_style="casual",
                cultural_context="test context"
            )
            
            response = await self.claude_client.generate_character_response(
                character_prompt=test_prompt,
                context="Health check test",
                target_topic="test"
            )
            
            return response.character_consistency is not None
            
        except Exception as e:
            logger.error(f"Claude health check failed: {str(e)}")
            return False
    
    def _convert_to_claude_prompt(self, config: PersonalityConfig) -> PersonalityPrompt:
        """Convert our domain model to Claude's format."""
        return PersonalityPrompt(
            character_name=config.character_name,
            personality_traits=config.personality_traits,
            background=config.background,
            language_style=config.language_style,
            topics_of_interest=config.topics_of_interest,
            interaction_style=config.interaction_style,
            cultural_context=config.cultural_context
        ) 