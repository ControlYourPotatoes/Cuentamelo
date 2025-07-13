"""
Base character agent class for Puerto Rican AI personalities.
Integrates with LangGraph workflows and Claude API for authentic character responses.
"""
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import asyncio
import logging

from app.models.conversation import (
    AgentState, ConversationMessage, MessageType, AgentDecision,
    NewsItem, CharacterReaction, is_character_available
)
from app.tools.claude_client import (
    ClaudeClient, PersonalityPrompt, ClaudeResponse, get_claude_client
)

logger = logging.getLogger(__name__)


class BaseCharacterAgent(ABC):
    """
    Abstract base class for Puerto Rican AI character agents.
    
    This class provides the foundation for character-specific personalities
    while integrating with LangGraph workflows and Claude API for response generation.
    """
    
    def __init__(
        self,
        character_id: str,
        character_name: str,
        personality_traits: str,
        background: str,
        language_style: str,
        topics_of_interest: List[str],
        interaction_style: str,
        cultural_context: str,
        claude_client: Optional[ClaudeClient] = None
    ):
        self.character_id = character_id
        self.character_name = character_name
        self.personality_prompt = PersonalityPrompt(
            character_name=character_name,
            personality_traits=personality_traits,
            background=background,
            language_style=language_style,
            topics_of_interest=topics_of_interest,
            interaction_style=interaction_style,
            cultural_context=cultural_context
        )
        self.claude_client = claude_client
        
        # Character-specific configuration
        self.engagement_threshold = 0.5  # Minimum relevance to engage
        self.cooldown_minutes = 15  # Minutes between interactions
        self.max_daily_interactions = 50
        self.preferred_topics = set(topics_of_interest)
        
        # Performance tracking
        self.interaction_count = 0
        self.total_engagements = 0
        self.last_interaction_time: Optional[datetime] = None
        
    async def initialize_claude_client(self):
        """Initialize Claude client if not provided."""
        if not self.claude_client:
            self.claude_client = await get_claude_client()
    
    # Abstract methods for character-specific behavior
    
    @abstractmethod
    def calculate_engagement_probability(
        self,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        news_item: NewsItem = None
    ) -> float:
        """
        Calculate the probability that this character would engage with given content.
        
        Returns:
            float: Probability between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def get_topic_relevance(self, topics: List[str]) -> float:
        """
        Calculate how relevant given topics are to this character.
        
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def get_character_specific_context(self, base_context: str) -> str:
        """
        Add character-specific context to the base prompt context.
        
        Returns:
            str: Enhanced context with character-specific perspective
        """
        pass
    
    # Core agent functionality
    
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
            if not is_character_available(state):
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
    
    async def generate_response(
        self,
        state: AgentState,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        target_topic: str = None
    ) -> ClaudeResponse:
        """
        Generate a character response using Claude API.
        
        Args:
            state: Current agent state
            context: Context for the response
            conversation_history: Previous conversation messages
            target_topic: Specific topic to focus on
            
        Returns:
            ClaudeResponse: Generated response with metadata
        """
        await self.initialize_claude_client()
        
        try:
            # Add character-specific context
            enhanced_context = self.get_character_specific_context(context)
            
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
            
            # Generate response
            response = await self.claude_client.generate_character_response(
                character_prompt=self.personality_prompt,
                context=enhanced_context,
                conversation_history=claude_history,
                target_topic=target_topic
            )
            
            # Update state with response info
            state.generated_content = response.content
            state.personality_consistency_score = response.confidence_score
            state.response_time_ms = response.response_time_ms
            state.content_approved = response.character_consistency
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response for {self.character_name}: {str(e)}")
            state.error_message = str(e)
            state.error_count += 1
            
            # Return fallback response
            fallback_content = self._get_fallback_response(context)
            return ClaudeResponse(
                content=fallback_content,
                confidence_score=0.0,
                character_consistency=False,
                estimated_tokens=0,
                response_time_ms=0
            )
    
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
        await self.initialize_claude_client()
        
        try:
            # Make engagement decision first
            decision = await self.make_engagement_decision(
                state=state,
                context=f"{news_item.headline}\n{news_item.content}",
                news_item=news_item
            )
            
            reaction_content = ""
            confidence_score = 0.0
            
            if decision == AgentDecision.ENGAGE:
                # Generate news reaction
                response = await self.claude_client.generate_news_reaction(
                    character_prompt=self.personality_prompt,
                    news_headline=news_item.headline,
                    news_content=news_item.content,
                    emotional_context=emotional_context
                )
                
                reaction_content = response.content
                confidence_score = response.confidence_score
                
                # Update interaction tracking
                self._update_interaction_tracking(state)
            
            return CharacterReaction(
                character_id=self.character_id,
                character_name=self.character_name,
                news_item_id=news_item.id,
                reaction_content=reaction_content,
                decision=decision,
                confidence_score=confidence_score,
                reasoning=state.decision_reasoning,
                engagement_prediction=state.decision_confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating news reaction for {self.character_name}: {str(e)}")
            return CharacterReaction(
                character_id=self.character_id,
                character_name=self.character_name,
                news_item_id=news_item.id,
                reaction_content="",
                decision=AgentDecision.DEFER,
                confidence_score=0.0,
                reasoning=f"Error: {str(e)}",
                engagement_prediction=0.0
            )
    
    async def reply_to_conversation(
        self,
        state: AgentState,
        conversation_thread: List[ConversationMessage],
        original_post: str,
        reply_to_character: str
    ) -> Optional[ConversationMessage]:
        """
        Generate a reply in an ongoing conversation.
        
        Args:
            state: Current agent state
            conversation_thread: Full conversation history
            original_post: The original post that started the conversation
            reply_to_character: Character being replied to
            
        Returns:
            ConversationMessage or None if not engaging
        """
        await self.initialize_claude_client()
        
        try:
            # Make engagement decision
            decision = await self.make_engagement_decision(
                state=state,
                context=original_post,
                conversation_history=conversation_thread
            )
            
            if decision != AgentDecision.ENGAGE:
                return None
            
            # Generate conversation reply
            response = await self.claude_client.generate_conversation_reply(
                character_prompt=self.personality_prompt,
                original_post=original_post,
                conversation_thread=[
                    {
                        "speaker": msg.character_name,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in conversation_thread
                ],
                reply_to_character=reply_to_character
            )
            
            if not response.character_consistency:
                logger.warning(f"Personality inconsistency detected for {self.character_name}")
                return None
            
            # Update interaction tracking
            self._update_interaction_tracking(state)
            
            # Find the message being replied to
            parent_message_id = None
            if conversation_thread:
                # Reply to the last message from the target character
                for msg in reversed(conversation_thread):
                    if msg.character_name == reply_to_character:
                        parent_message_id = msg.id
                        break
            
            return ConversationMessage(
                character_id=self.character_id,
                character_name=self.character_name,
                content=response.content,
                message_type=MessageType.CHARACTER_REPLY,
                parent_message_id=parent_message_id,
                engagement_score=response.confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error generating conversation reply for {self.character_name}: {str(e)}")
            return None
    
    # Helper methods
    
    def _is_rate_limited(self, state: AgentState) -> bool:
        """Check if character is rate limited."""
        # Check daily interaction limit
        if state.interaction_count >= self.max_daily_interactions:
            return True
        
        # Check cooldown period
        if (state.last_interaction_time and 
            datetime.utcnow() - state.last_interaction_time < timedelta(minutes=self.cooldown_minutes)):
            return True
        
        return False
    
    def _update_interaction_tracking(self, state: AgentState):
        """Update interaction tracking metrics."""
        state.interaction_count += 1
        state.last_interaction_time = datetime.utcnow()
        state.cooldown_until = datetime.utcnow() + timedelta(minutes=self.cooldown_minutes)
        
        # Update performance metrics
        self.interaction_count += 1
        self.last_interaction_time = datetime.utcnow()
    
    def _get_fallback_response(self, context: str) -> str:
        """Get a fallback response when Claude API fails."""
        fallback_responses = [
            f"Ay, perdón - {self.character_name} está teniendo problemas técnicos 🤖",
            f"Dame un momentito, {self.character_name} needs a quick reset ⚡",
            f"¡Wepa! Sistema temporalmente down - {self.character_name} volverá pronto 💪"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    # Character information methods
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of this character's configuration and stats."""
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "personality_traits": self.personality_prompt.personality_traits,
            "background": self.personality_prompt.background,
            "topics_of_interest": self.personality_prompt.topics_of_interest,
            "interaction_style": self.personality_prompt.interaction_style,
            "engagement_threshold": self.engagement_threshold,
            "cooldown_minutes": self.cooldown_minutes,
            "max_daily_interactions": self.max_daily_interactions,
            "total_interactions": self.interaction_count,
            "last_interaction": self.last_interaction_time.isoformat() if self.last_interaction_time else None
        }
    
    def __str__(self) -> str:
        return f"CharacterAgent({self.character_name}, ID: {self.character_id})"
    
    def __repr__(self) -> str:
        return self.__str__() 