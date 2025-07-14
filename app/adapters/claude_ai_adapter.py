"""
Claude AI Adapter - Implements AIProviderPort using Anthropic Claude API.
This is the "adapter" that connects our port to the external Claude service.
"""
from typing import List, Dict, Any, Optional
import logging

from app.ports.ai_provider import AIProviderPort, AIResponse
from app.models.conversation import ConversationMessage
from app.models.ai_personality_data import AIPersonalityData
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
        personality_data: AIPersonalityData,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        target_topic: Optional[str] = None,
        thread_context: Optional[str] = None,
        is_new_thread: bool = True
    ) -> AIResponse:
        """Generate character response using Claude API with thread awareness."""
        try:
            # Convert our domain model to Claude's format
            claude_prompt = self._convert_to_claude_prompt(personality_data)
            
            # Enhance context with thread awareness
            enhanced_context = self._enhance_context_with_thread_awareness(
                context, thread_context, is_new_thread, personality_data
            )
            
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
                context=enhanced_context,
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
                    "model": self.claude_client.model,
                    "thread_aware": not is_new_thread,
                    "personality_used": personality_data.character_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Claude adapter: {str(e)}")
            # Return fallback response
            return AIResponse(
                content=f"[Error generating response for {personality_data.character_name}]",
                confidence_score=0.0,
                character_consistency=False,
                metadata={"error": str(e), "provider": "claude"}
            )
    
    async def generate_news_reaction(
        self,
        personality_data: AIPersonalityData,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> AIResponse:
        """Generate news reaction using Claude API."""
        try:
            claude_prompt = self._convert_to_claude_prompt(personality_data)
            
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
                    "emotional_context": emotional_context,
                    "personality_used": personality_data.character_id
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
        personality_data: AIPersonalityData,
        generated_content: str
    ) -> bool:
        """Validate personality consistency using Claude."""
        try:
            claude_prompt = self._convert_to_claude_prompt(personality_data)
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
            from app.models.ai_personality_data import LanguageStyle
            test_personality = AIPersonalityData(
                character_id="test",
                character_name="Test",
                character_type="test",
                personality_traits="Test personality",
                background="Test background",
                language_style=LanguageStyle.ENGLISH,
                interaction_style="casual",
                cultural_context="test context"
            )
            
            response = await self.generate_character_response(
                personality_data=test_personality,
                context="Health check test",
                target_topic="test"
            )
            
            return response.character_consistency is not None
            
        except Exception as e:
            logger.error(f"Claude health check failed: {str(e)}")
            return False
    
    def _convert_to_claude_prompt(self, personality_data: AIPersonalityData) -> PersonalityPrompt:
        """Convert our domain model to Claude's format."""
        return PersonalityPrompt(
            character_name=personality_data.character_name,
            personality_traits=personality_data.personality_traits,
            background=personality_data.background,
            language_style=personality_data.language_style.value if hasattr(personality_data.language_style, 'value') else str(personality_data.language_style),
            topics_of_interest=personality_data.topics_of_interest,
            interaction_style=personality_data.interaction_style,
            cultural_context=personality_data.cultural_context
        )
    
    def _enhance_context_with_thread_awareness(
        self,
        context: str,
        thread_context: Optional[str],
        is_new_thread: bool,
        personality_data: AIPersonalityData
    ) -> str:
        """Enhance context with thread awareness and personality-specific instructions."""
        
        enhanced_context = context
        
        # Add thread context if this is a reply
        if thread_context and not is_new_thread:
            enhanced_context = f"Thread context: {thread_context}\n\nOriginal content: {context}"
        
        # Add personality-specific response template
        if is_new_thread:
            template = personality_data.response_templates.get("new_thread", "")
        else:
            template = personality_data.response_templates.get("thread_reply", "")
        
        if template:
            enhanced_context += f"\n\n{template}"
        
        # Add character-specific personality prompt
        personality_prompt = self._generate_character_specific_prompt(personality_data)
        enhanced_context += f"\n\n{personality_prompt}"
        
        return enhanced_context
    
    def _generate_character_specific_prompt(self, personality_data: AIPersonalityData) -> str:
        """Generate character-specific personality prompt with detailed instructions."""
        
        prompt = f"""DETAILED {personality_data.character_name.upper()} PERSONALITY:

YOU ARE {personality_data.character_name.upper()} - {personality_data.personality_traits}

PLATFORM: You are posting on Twitter/X - keep responses concise, engaging, and social media optimized.

SPEAKING STYLE - YOU MUST USE THESE EXPRESSIONS:
"""
        
        # Add signature phrases
        for phrase in personality_data.signature_phrases:
            prompt += f'- "{phrase}"\n'
        
        # Add common expressions
        if personality_data.common_expressions:
            prompt += f"\nCOMMON EXPRESSIONS: {', '.join(personality_data.common_expressions)}\n"
        
        # Add emoji preferences
        if personality_data.emoji_preferences:
            prompt += f"\nEMOJI PREFERENCES: {', '.join(personality_data.emoji_preferences)}\n"
        
        # Add example responses
        if personality_data.example_responses:
            prompt += "\nTYPICAL RESPONSES YOU WOULD GIVE:\n"
            for category, responses in personality_data.example_responses.items():
                prompt += f"\nFor {category.replace('_', ' ').title()}:\n"
                for response in responses[:2]:  # Show first 2 examples
                    prompt += f'"{response}"\n'
        
        # Add energy level guidance
        energy_desc = "HIGH ENERGY" if personality_data.base_energy_level > 0.7 else "MODERATE ENERGY" if personality_data.base_energy_level > 0.4 else "CALM ENERGY"
        prompt += f"\nENERGY LEVEL:\n- You are {energy_desc}\n"
        
        if personality_data.base_energy_level > 0.7:
            prompt += "- You use lots of exclamation marks!!!\n"
            prompt += "- You speak quickly and energetically\n"
            prompt += "- You're always looking for the fun angle\n"
        
        # Add cultural context
        if personality_data.puerto_rico_references:
            prompt += f"\nPUERTO RICAN REFERENCES: {', '.join(personality_data.puerto_rico_references)}\n"
        
        # Add validation rules
        if personality_data.personality_consistency_rules:
            prompt += "\nREMEMBER:\n"
            for rule in personality_data.personality_consistency_rules:
                prompt += f"- {rule}\n"
        
        # Add Twitter/X specific instructions
        prompt += f"""
TWITTER/X RESPONSE GUIDELINES:
- KEEP RESPONSES SHORT AND PUNCHY (max 1 sentences total! maybe 2 if you have to)
- Twitter character limit: aim for under 200 characters
- Start a signature phrase when you want to be punchy and engaging
- Use hashtags with some of your signature phrases
- End with a question or call to action
- Use 2-3 strategic emojis
- Be authentic and conversational
- Engage with your audience
- Show Puerto Rican pride and culture

RESPONSE STRUCTURE (KEEP IT SHORT!):
1. Signature opening ("¡Este es Jovani!" or similar)
2. Your quick reaction/opinion (1 sentence max)
3. Relevant hashtags if appropriate

EXAMPLE GOOD RESPONSE LENGTH:
"¡Este es Jovani! 🔥 WEPAAA! El conejo malo is coming back home y esto está BRUTAL! 🇵🇷 Q dicen mi gente, nos vemos en el Choli? #BadBunnyEnPR"

REMEMBER: You are {personality_data.character_name} - {personality_data.personality_traits}
KEEP IT SHORT AND SWEET!
"""
        
        return prompt 