"""
Claude API client for character personality generation and conversation management.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from anthropic import AsyncAnthropic
from pydantic import BaseModel
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PersonalityPrompt(BaseModel):
    """Structured prompt for character personality generation."""
    character_name: str
    personality_traits: str
    background: str
    language_style: str
    topics_of_interest: List[str]
    interaction_style: str
    cultural_context: str


class ClaudeResponse(BaseModel):
    """Structured response from Claude API."""
    content: str
    confidence_score: float
    character_consistency: bool
    estimated_tokens: int
    response_time_ms: int


class ClaudeClient:
    """
    Anthropic Claude API client for Puerto Rican AI character personality generation.
    
    Provides methods for:
    - Character response generation
    - Personality consistency validation
    - Conversation context management
    - Cultural authenticity verification
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncAnthropic(
            api_key=api_key or settings.ANTHROPIC_API_KEY
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1000
        self.temperature = 0.7
        
    async def generate_character_response(
        self,
        character_prompt: PersonalityPrompt,
        context: str,
        conversation_history: List[Dict[str, Any]] = None,
        target_topic: str = None
    ) -> ClaudeResponse:
        """
        Generate a character response using Claude API with personality consistency.
        
        Args:
            character_prompt: Character personality definition
            context: Current context or news item to respond to
            conversation_history: Previous conversation context
            target_topic: Specific topic to focus the response on
            
        Returns:
            ClaudeResponse with generated content and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build the system prompt for character consistency
            system_prompt = self._build_character_system_prompt(character_prompt)
            
            # Build the user prompt with context
            user_prompt = self._build_context_prompt(
                context, conversation_history, target_topic
            )
            
            # Generate response from Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Calculate response time
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Extract content
            content = response.content[0].text if response.content else ""
            
            # Validate personality consistency
            consistency_check = await self._validate_personality_consistency(
                character_prompt, content
            )
            
            return ClaudeResponse(
                content=content,
                confidence_score=0.85,  # TODO: Implement proper confidence scoring
                character_consistency=consistency_check,
                estimated_tokens=response.usage.output_tokens,
                response_time_ms=response_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error generating character response: {str(e)}")
            # Return a fallback response
            return ClaudeResponse(
                content=f"[Error generating response for {character_prompt.character_name}]",
                confidence_score=0.0,
                character_consistency=False,
                estimated_tokens=0,
                response_time_ms=int((asyncio.get_event_loop().time() - start_time) * 1000)
            )
    
    def _build_character_system_prompt(self, character_prompt: PersonalityPrompt) -> str:
        """Build system prompt for character personality consistency."""
        return f"""You are {character_prompt.character_name}, a Puerto Rican AI character with the following characteristics:

PERSONALITY TRAITS: {character_prompt.personality_traits}

BACKGROUND: {character_prompt.background}

LANGUAGE STYLE: {character_prompt.language_style}
- Use authentic Puerto Rican Spanish expressions and Spanglish naturally
- Maintain your unique voice and speaking patterns
- Express emotions and reactions genuinely

TOPICS OF INTEREST: {', '.join(character_prompt.topics_of_interest)}

INTERACTION STYLE: {character_prompt.interaction_style}

CULTURAL CONTEXT: {character_prompt.cultural_context}
- You understand Puerto Rican culture, politics, and daily life deeply
- Reference local places, events, and cultural nuances authentically
- Respond with the perspective of someone who lives this culture

RESPONSE GUIDELINES:
1. Stay true to your character's personality at all times
2. Use natural Puerto Rican expressions and language patterns
3. Respond with appropriate emotion and energy level for your character
4. Keep responses concise but engaging (1-3 sentences typically)
5. Use relevant emojis that match your personality
6. Reference Puerto Rican culture when relevant

Remember: You are not just playing a role - you ARE this character. Respond naturally as they would."""

    def _build_context_prompt(
        self,
        context: str,
        conversation_history: List[Dict[str, Any]] = None,
        target_topic: str = None
    ) -> str:
        """Build user prompt with context and conversation history."""
        prompt_parts = []
        
        if conversation_history:
            prompt_parts.append("CONVERSATION HISTORY:")
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                speaker = msg.get('speaker', 'Unknown')
                content = msg.get('content', '')
                prompt_parts.append(f"{speaker}: {content}")
            prompt_parts.append("")
        
        prompt_parts.append("CURRENT CONTEXT:")
        prompt_parts.append(context)
        
        if target_topic:
            prompt_parts.append(f"\nFOCUS ON: {target_topic}")
        
        prompt_parts.append("\nRespond as your character would naturally react to this context.")
        
        return "\n".join(prompt_parts)
    
    async def _validate_personality_consistency(
        self,
        character_prompt: PersonalityPrompt,
        generated_content: str
    ) -> bool:
        """
        Validate that the generated content maintains character consistency.
        
        This is a simplified implementation - could be enhanced with
        more sophisticated consistency checking.
        """
        try:
            # Basic consistency checks
            character_name = character_prompt.character_name.lower()
            content_lower = generated_content.lower()
            
            # Check if response is not empty and has reasonable length
            if not generated_content.strip() or len(generated_content.strip()) < 10:
                return False
            
            # Check for obvious inconsistencies (very basic)
            if "[error" in content_lower or "i am claude" in content_lower:
                return False
            
            # For now, return True for basic validation
            # TODO: Implement more sophisticated consistency checking
            return True
            
        except Exception as e:
            logger.error(f"Error validating personality consistency: {str(e)}")
            return False
    
    async def generate_news_reaction(
        self,
        character_prompt: PersonalityPrompt,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> ClaudeResponse:
        """
        Generate a character's reaction to breaking news.
        
        Args:
            character_prompt: Character personality definition
            news_headline: News headline
            news_content: Full news content
            emotional_context: Expected emotional tone (urgent, celebratory, etc.)
            
        Returns:
            ClaudeResponse with character's news reaction
        """
        context = f"""
BREAKING NEWS:
Headline: {news_headline}

Content: {news_content}

Emotional Context: {emotional_context}

React to this news as your character would. Consider:
- How does this affect Puerto Rico and your community?
- What is your character's perspective on this type of news?
- How would you naturally express your reaction on social media?
"""
        
        return await self.generate_character_response(
            character_prompt=character_prompt,
            context=context,
            target_topic="news_reaction"
        )
    
    async def generate_conversation_reply(
        self,
        character_prompt: PersonalityPrompt,
        original_post: str,
        conversation_thread: List[Dict[str, Any]],
        reply_to_character: str
    ) -> ClaudeResponse:
        """
        Generate a reply in an ongoing conversation between characters.
        
        Args:
            character_prompt: Character personality definition
            original_post: The original post that started the conversation
            conversation_thread: Full conversation history
            reply_to_character: Name of character being replied to
            
        Returns:
            ClaudeResponse with conversational reply
        """
        context = f"""
CONVERSATION CONTEXT:
Original post: {original_post}

You are replying to {reply_to_character} in this conversation thread.

Respond naturally as your character would in this social media conversation.
Keep it engaging and authentic to your personality.
"""
        
        return await self.generate_character_response(
            character_prompt=character_prompt,
            context=context,
            conversation_history=conversation_thread,
            target_topic="conversation_reply"
        )


# Global client instance
claude_client = ClaudeClient()


async def get_claude_client() -> ClaudeClient:
    """Get the global Claude client instance."""
    return claude_client 