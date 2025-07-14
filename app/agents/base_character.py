"""
Base character agent class for Puerto Rican AI personalities.
Integrates with LangGraph workflows and AI providers for authentic character responses.
"""
from typing import Dict, List, Optional, Any, Callable
from abc import ABC
from datetime import datetime, timedelta, timezone
import asyncio
import logging

from app.models.conversation import (
    AgentState, ConversationMessage, MessageType, AgentDecision,
    NewsItem, CharacterReaction, is_character_available
)
from app.models.personality import PersonalityData
from app.models.personalities.personality_factory import get_personality_by_id
from app.ports.personality_port import PersonalityPort
from app.ports.ai_provider import AIProviderPort, AIResponse
from app.ports.twitter_provider import TwitterProviderPort
from app.utils.event_decorators import (
    emit_character_analyzing, emit_engagement_decision, 
    emit_response_generating, emit_post_published
)

logger = logging.getLogger(__name__)


class BaseCharacterAgent:
    """
    Enhanced base class for Puerto Rican AI character agents.

    This class now works seamlessly with configuration-driven personalities
    while still supporting custom logic when needed.
    """
    
    def __init__(
        self,
        character_id: str,
        ai_provider: Optional[AIProviderPort] = None,
        personality: Optional[PersonalityPort] = None,
        twitter_provider: Optional['TwitterProviderPort'] = None
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
        
        # Inject Twitter provider dependency
        self.twitter_provider = twitter_provider
        
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
        
    @property
    def character_name(self) -> str:
        """Get character name from personality data."""
        return self.personality_data.get_agent_personality_data().character_name
    
    @property
    def character_type(self) -> str:
        """Get character type from personality data."""
        return self.personality_data.get_agent_personality_data().character_type
    
    async def initialize_ai_provider(self, ai_provider: AIProviderPort):
        """Initialize AI provider if not provided."""
        if not self.ai_provider:
            self.ai_provider = ai_provider
    
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
    
    # Core agent functionality
    
    @emit_character_analyzing()
    async def make_engagement_decision(
        self,
        state: AgentState,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        news_item: NewsItem = None
    ) -> AgentDecision:
        """
        Decide whether and how to engage with given content.
        
        Args:
            state: Current agent state
            context: Content to potentially engage with
            conversation_history: Previous conversation context
            news_item: News item if this is a news reaction
            
        Returns:
            AgentDecision: The character's decision
        """
        try:
            # Check availability
            print(f"🔍 DEBUG: Checking availability for {self.character_name}")
            print(f"🔍 DEBUG: is_character_available result: {is_character_available(state)}")
            if not is_character_available(state):
                print(f"🔍 DEBUG: {self.character_name} is not available (cooldown)")
                logger.info(f"{self.character_name} is not available (cooldown)")
                return AgentDecision.DEFER
            
            # Calculate engagement probability
            engagement_prob = self.calculate_engagement_probability(
                context, conversation_history, news_item
            )
            
            # Update state with decision info
            state.decision_confidence = engagement_prob
            state.decision_reasoning = f"Engagement probability: {engagement_prob:.2f}"
            
            # Make decision based on probability and character rules
            if engagement_prob >= self.engagement_threshold:
                # Check rate limiting
                if self._is_rate_limited(state):
                    state.decision_reasoning += " (rate limited)"
                    return AgentDecision.DEFER
                
                return AgentDecision.ENGAGE
            else:
                return AgentDecision.IGNORE
                
        except Exception as e:
            logger.error(f"Error making engagement decision for {self.character_name}: {str(e)}")
            state.error_message = str(e)
            return AgentDecision.DEFER
    
    @emit_response_generating()
    async def generate_response(
        self,
        state: AgentState,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        target_topic: str = None,
        thread_context: Optional[str] = None,
        is_new_thread: bool = True
    ) -> AIResponse:
        """
        Generate a character response using AI provider.
        
        Args:
            state: Current agent state
            context: Context for the response
            conversation_history: Previous conversation messages
            target_topic: Specific topic to focus on
            thread_context: Context from existing thread (if replying)
            is_new_thread: Whether this is a new thread or reply
            
        Returns:
            AIResponse: Generated response with metadata
        """
        if not self.ai_provider:
            raise ValueError("AI provider not initialized")
        
        try:
            # Add character-specific context
            enhanced_context = self.get_character_specific_context(context)
            
            # Generate response using AI provider
            response = await self.ai_provider.generate_character_response(
                personality_data=self.get_ai_personality_data(),
                context=enhanced_context,
                conversation_history=conversation_history,
                target_topic=target_topic,
                thread_context=thread_context,
                is_new_thread=is_new_thread
            )
            
            # Update state with response info
            state.generated_content = response.content
            state.personality_consistency_score = response.confidence_score
            state.response_time_ms = response.metadata.get("response_time_ms", 0)
            state.content_approved = response.character_consistency
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response for {self.character_name}: {str(e)}")
            state.error_message = str(e)
            state.error_count += 1
            
            # Return fallback response
            fallback_content = self._get_fallback_response(context)
            return AIResponse(
                content=fallback_content,
                confidence_score=0.0,
                character_consistency=False,
                metadata={"error": str(e), "fallback": True}
            )
    
    @emit_engagement_decision()
    async def react_to_news(
        self,
        state: AgentState,
        news_item: NewsItem,
        emotional_context: str = "neutral"
    ) -> CharacterReaction:
        """
        Generate a character's reaction to a news item.
        
        Args:
            state: Current agent state
            news_item: News item to react to
            emotional_context: Emotional context for the reaction
            
        Returns:
            CharacterReaction: The character's reaction
        """
        if not self.ai_provider:
            raise ValueError("AI provider not initialized")
        
        try:
            # Make engagement decision first
            decision = await self.make_engagement_decision(
                state=state,
                context=f"{news_item.headline}\n{news_item.content}",
                news_item=news_item
            )
            
            if decision != AgentDecision.ENGAGE:
                return CharacterReaction(
                    character_id=self.character_id,
                    character_name=self.character_name,
                    news_item_id=news_item.id,
                    reaction_content="",
                    decision=decision,
                    confidence_score=state.decision_confidence,
                    reasoning=state.decision_reasoning
                )
            
            # Generate reaction using AI provider
            response = await self.ai_provider.generate_news_reaction(
                personality_data=self.get_ai_personality_data(),
                news_headline=news_item.headline,
                news_content=news_item.content,
                emotional_context=emotional_context
            )
            
            # Create character reaction
            reaction = CharacterReaction(
                character_id=self.character_id,
                character_name=self.character_name,
                news_item_id=news_item.id,
                reaction_content=response.content,
                decision=decision,
                confidence_score=response.confidence_score,
                reasoning=f"Generated reaction with {response.confidence_score:.2f} confidence"
            )
            
            # Update interaction tracking
            self._update_interaction_tracking(state)
            
            return reaction
            
        except Exception as e:
            logger.error(f"Error generating news reaction for {self.character_name}: {str(e)}")
            state.error_message = str(e)
            state.error_count += 1
            
            return CharacterReaction(
                character_id=self.character_id,
                character_name=self.character_name,
                news_item_id=news_item.id,
                reaction_content="",
                decision=AgentDecision.DEFER,
                confidence_score=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    async def reply_to_conversation(
        self,
        state: AgentState,
        conversation_thread: List[ConversationMessage],
        original_post: str,
        reply_to_character: str,
        thread_context: Optional[str] = None
    ) -> Optional[ConversationMessage]:
        """
        Generate a reply to an existing conversation thread.
        
        Args:
            state: Current agent state
            conversation_thread: Thread of conversation messages
            original_post: Original post content
            reply_to_character: Character being replied to
            thread_context: Context from the thread
            
        Returns:
            ConversationMessage: Generated reply message
        """
        try:
            # Check if we should engage with this thread
            engagement_prob = self.calculate_engagement_probability(
                context=original_post,
                conversation_history=conversation_thread
            )
            
            if engagement_prob < self.engagement_threshold:
                logger.info(f"{self.character_name} not engaging with thread (low relevance)")
                return None
            
            # Generate reply
            response = await self.generate_response(
                state=state,
                context=original_post,
                conversation_history=conversation_thread,
                target_topic="conversation_reply",
                thread_context=thread_context,
                is_new_thread=False
            )
            
            if not response.content or response.confidence_score < 0.3:
                logger.info(f"{self.character_name} generated low-quality reply, skipping")
                return None
            
            # Create conversation message
            message = ConversationMessage(
                character_id=self.character_id,
                character_name=self.character_name,
                content=response.content,
                message_type=MessageType.CHARACTER_REPLY,
                parent_message_id=conversation_thread[-1].id if conversation_thread else None,
                engagement_score=response.confidence_score,
                metadata={
                    "reply_to": reply_to_character,
                    "thread_context": thread_context is not None,
                    "personality_consistency": response.character_consistency
                }
            )
            
            # Update interaction tracking
            self._update_interaction_tracking(state)
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating conversation reply for {self.character_name}: {str(e)}")
            state.error_message = str(e)
            return None
    
    def _is_rate_limited(self, state: AgentState) -> bool:
        """Check if character is rate limited."""
        if self.last_interaction_time:
            time_since_last = datetime.now(timezone.utc) - self.last_interaction_time
            if time_since_last < timedelta(minutes=self.cooldown_minutes):
                return True
        
        if self.interaction_count >= self.max_daily_interactions:
            return True
        
        return False
    
    def _update_interaction_tracking(self, state: AgentState):
        """Update interaction tracking metrics."""
        self.interaction_count += 1
        self.total_engagements += 1
        self.last_interaction_time = datetime.now(timezone.utc)
        
        # Update agent state
        state.interaction_count = self.interaction_count
        state.last_interaction_time = self.last_interaction_time
        state.engagement_rate = self.total_engagements / max(self.interaction_count, 1)
    
    def _get_fallback_response(self, context: str) -> str:
        """Get fallback response when AI generation fails."""
        # Use personality data to generate appropriate fallback
        agent_data = self.personality_data.get_agent_personality_data()
        if agent_data.signature_phrases:
            signature = agent_data.signature_phrases[0]
            return f"{signature} [Response temporarily unavailable]"
        
        return f"[{self.character_name} response temporarily unavailable]"
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of the character for external use."""
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "character_type": self.character_type,
            "personality_traits": self.personality_data.personality_traits,
            "engagement_threshold": self.engagement_threshold,
            "topics_of_interest": self.personality_data.topics_of_interest,
            "signature_phrases": self.personality_data.signature_phrases[:3] if self.personality_data.signature_phrases else []
        }
    
    def get_ai_personality_data(self) -> 'AIPersonalityData':
        """Get the minimal AI personality data for AI providers."""
        # Default implementation - subclasses can override
        from app.models.ai_personality_data import AIPersonalityData
        
        return AIPersonalityData(
            character_id=self.character_id,
            character_name=self.character_name,
            character_type=self.character_type,
            personality_traits=self.personality_data.personality_traits,
            background=self.personality_data.background,
            language_style=self.personality_data.language_style,
            interaction_style=self.personality_data.interaction_style,
            cultural_context=self.personality_data.cultural_context,
            signature_phrases=self.personality_data.signature_phrases,
            common_expressions=self.personality_data.common_expressions,
            emoji_preferences=self.personality_data.emoji_preferences,
            topics_of_interest=self.personality_data.topics_of_interest,
            example_responses=self.personality_data.example_responses,
            response_templates=self.personality_data.response_templates,
            base_energy_level=self.personality_data.base_energy_level,
            puerto_rico_references=self.personality_data.puerto_rico_references,
            personality_consistency_rules=self.personality_data.personality_consistency_rules
        )
    
    def __str__(self) -> str:
        return f"{self.character_name} ({self.character_type})"
    
    def __repr__(self) -> str:
        return f"BaseCharacterAgent(character_id='{self.character_id}', character_name='{self.character_name}')" 