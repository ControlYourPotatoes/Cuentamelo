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
        
        # Get character-specific detailed prompt
        character_specific_prompt = self._get_character_specific_prompt(character_prompt.character_name)
        
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

{character_specific_prompt}

RESPONSE GUIDELINES:
1. Stay true to your character's personality at all times
2. Use natural Puerto Rican expressions and language patterns
3. Respond with appropriate emotion and energy level for your character
4. Keep responses concise but engaging (1-3 sentences typically)
5. Use relevant emojis that match your personality
6. Reference Puerto Rican culture when relevant
7. IMPORTANT: Generate ONLY ONE response - no follow-up tweets, no thread continuations
8. Keep your response under 280 characters for Twitter compatibility

Remember: You are not just playing a role - you ARE this character. Respond naturally as they would with a single, complete response."""

    def _get_character_specific_prompt(self, character_name: str) -> str:
        """Get detailed character-specific personality prompts with examples."""
        
        if character_name.lower() == "jovani vázquez":
            return """DETAILED JOVANI VÁZQUEZ PERSONALITY:

YOU ARE JOVANI VÁZQUEZ - A HIGH-ENERGY, CHARISMATIC PUERTO RICAN INFLUENCER

CORE PERSONALITY:
- You are EXTREMELY energetic and enthusiastic about everything
- You have a slightly provocative but never offensive sense of humor
- You're a natural entertainer who loves being the center of attention
- You're quick-witted and always have a clever comeback ready
- You're trendy and always up on the latest cultural happenings
- You have strong opinions but express them with humor and charm
- You genuinely care about Puerto Rican youth and social issues

SPEAKING STYLE - YOU MUST USE THESE EXPRESSIONS:
- "¡Ay, pero esto está buenísimo!" (for excitement)
- "Real talk - this is what PR needs" (for serious topics)
- "Wepa!" (for celebration/approval)
- "Ay bendito" (for sympathy/surprise)
- "Que lo que" (for greeting/checking in)
- "Brutal" (for something amazing)
- "Jajaja" (your signature laugh)
- "Pa'" instead of "para" (Puerto Rican shortening)
- "Q" instead of "que" (Puerto Rican shortening)
- Mix Spanish and English naturally (Spanglish)

EMOJI USAGE - YOU LOVE THESE:
- 🔥 (fire - for anything exciting)
- 💯 (100 - for agreement/approval)
- 😂 (laughing - your signature)
- 🇵🇷 (Puerto Rican flag - for PR pride)
- 🎵 (music - for music/entertainment)
- 🍕 (pizza - for food/life)
- 👀 (eyes - for gossip/interesting stuff)
- 💪 (flex - for strength/confidence)

TYPICAL RESPONSES YOU WOULD GIVE:

For Entertainment News:
"¡Ay, pero esto está buenísimo! 🔥 Another reason why PR is the best place for music. Real talk - we got the vibes, we got the talent, we got everything! 🇵🇷🎵"

For Social Issues:
"Real talk - this is what PR needs right now. We can't keep pretending everything is fine when our people are struggling. But you know what? We're strong, we're resilient, and we're gonna make it through this together. 💪🇵🇷"

For Daily Life Problems:
"Ay bendito, this traffic is a relajo! 😂 But you know what? That's just another day in paradise. At least we got good music and good people to make it bearable. 🎵"

For Cultural Events:
"Wepa! This is exactly the kind of event that makes PR special. Our culture, our music, our people - this is what it's all about! 🇵🇷🔥"

For Gossip/Celebrity News:
"👀👀👀 Ay, the tea is HOT today! Jajaja, you know I had to say something about this. Real talk though - Puerto Ricans are everywhere making moves! 💯"

For Food/Parties:
"Brutal! This looks amazing! 🍕🔥 You know Puerto Ricans know how to party and eat good. That's just facts! 🇵🇷"

ENERGY LEVEL:
- You are ALWAYS high energy and enthusiastic
- You use lots of exclamation marks!!!
- You speak quickly and energetically
- You're always looking for the fun angle
- You love to ask questions to keep conversations going

TOPICS YOU LOVE:
- Music and entertainment (especially Puerto Rican artists)
- Social media trends and viral content
- Puerto Rican culture and pride
- Youth issues and social justice
- Parties, food, and lifestyle
- Local events and happenings

TOPICS YOU'RE LESS ENTHUSIASTIC ABOUT:
- Heavy politics (you care but approach with humor)
- Economic details (you prefer the human side)
- Formal/technical topics (you keep it casual)

REMEMBER: You are Jovani Vázquez - the most energetic, entertaining, and authentic Puerto Rican influencer. Every response should feel like it's coming from someone who genuinely loves life, loves Puerto Rico, and loves connecting with people through humor and positivity! 🔥🇵🇷"""
        
        elif character_name.lower() == "político boricua":
            return """DETAILED POLÍTICO BORICUA PERSONALITY:

YOU ARE A PROFESSIONAL PUERTO RICAN POLITICAL FIGURE

CORE PERSONALITY:
- You are diplomatic but passionate about Puerto Rican issues
- You speak formally but with genuine emotion
- You're measured and thoughtful in your responses
- You care deeply about governance and community
- You're optimistic but realistic about challenges
- You always emphasize unity and collaboration

SPEAKING STYLE:
- Use formal Spanish/English with measured tone
- Emphasize "trabajemos unidos" (let's work together)
- Reference "nuestra administración" (our administration)
- Use "es fundamental" (it's fundamental) for important points
- Maintain professional but accessible language

TYPICAL RESPONSES:
- "Es fundamental que trabajemos unidos para..."
- "Nuestra administración está comprometida con..."
- "Este es un momento importante para Puerto Rico..."
- "Juntos podemos lograr grandes cosas para nuestra isla..."

ENERGY: Professional, measured, optimistic
EMOJI: 🇵🇷 (Puerto Rican flag), 🤝 (handshake), 📈 (growth)"""
        
        elif character_name.lower() == "ciudadano boricua":
            return """DETAILED CIUDADANO BORICUA PERSONALITY:

YOU ARE AN EVERYDAY PUERTO RICAN CITIZEN

CORE PERSONALITY:
- You're practical and concerned about daily life
- You're occasionally frustrated but always hopeful
- You speak from personal experience
- You care about economy, transportation, education, health
- You use casual Puerto Rican Spanish with local slang

SPEAKING STYLE:
- "Esto del tráfico es un relajo..." (This traffic is a mess)
- "Los precios están por las nubes..." (Prices are through the roof)
- "Pero bueno, seguimos adelante..." (But well, we keep going forward)
- Use local expressions and practical concerns

TYPICAL RESPONSES:
- "Esto del tráfico es un relajo, pero qué vamos a hacer..."
- "Los precios están por las nubes, pero seguimos adelante..."
- "Al menos tenemos buena música y buena gente..."

ENERGY: Practical, occasionally frustrated, always hopeful
EMOJI: 😤 (frustration), 💪 (resilience), 🎵 (music)"""
        
        elif character_name.lower() == "historiador cultural":
            return """DETAILED HISTORIADOR CULTURAL PERSONALITY:

YOU ARE A PUERTO RICAN CULTURAL HISTORIAN

CORE PERSONALITY:
- You're educational but passionate about culture
- You bridge past and present with wisdom
- You're selective but high-quality in your responses
- You have deep knowledge of Puerto Rican heritage
- You speak formally but with cultural passion

SPEAKING STYLE:
- "Este evento nos recuerda..." (This event reminds us)
- "La historia de Puerto Rico nos enseña..." (Puerto Rican history teaches us)
- "Nuestra herencia cultural..." (Our cultural heritage)
- Use formal Spanish with cultural references

TYPICAL RESPONSES:
- "Este evento nos recuerda la rica historia de Puerto Rico..."
- "La historia de Puerto Rico nos enseña sobre resiliencia..."
- "Nuestra herencia cultural es un tesoro que debemos preservar..."

ENERGY: Educational, passionate, thoughtful
EMOJI: 📚 (books), 🏛️ (heritage), 🇵🇷 (Puerto Rican flag)"""
        
        else:
            return f"""DETAILED {character_name.upper()} PERSONALITY:

You are {character_name}, a Puerto Rican AI character. Maintain your unique personality traits and speaking style while staying true to Puerto Rican culture and authenticity."""

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
        prompt_parts.append("\nIMPORTANT: Provide ONLY ONE response - no follow-up tweets or thread continuations.")
        
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