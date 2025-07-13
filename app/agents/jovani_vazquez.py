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
    """
    
    def __init__(self, ai_provider=None, personality: Optional[PersonalityPort] = None):
        # Use provided personality or create default
        self.personality = personality or create_jovani_personality()
        
        super().__init__(
            character_id=self.personality.character_id,
            ai_provider=ai_provider
        )

    def calculate_engagement_probability(
        self,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        news_item: Optional[NewsItem] = None
    ) -> float:
        """
        Calculate Jovani's engagement probability based on content relevance.
        
        Jovani is more likely to engage with:
        - Entertainment and culture content
        - Puerto Rico-related topics
        - High-energy/exciting content
        - Social media trends
        - Content with emotional appeal
        """
        base_probability = 0.4  # Jovani's baseline engagement
        
        # Get engagement boosts from personality
        boosts = self.personality.calculate_engagement_boost(context)
        
        # Topic relevance based on news item
        topic_boost = 0.0
        if news_item and news_item.topics:
            topic_boost = self.personality.get_topic_relevance(news_item.topics) * 0.3
        
        # Check for conversation momentum
        conversation_boost = 0.0
        if conversation_history and len(conversation_history) > 0:
            # Jovani loves active conversations
            recent_messages = [msg for msg in conversation_history[-5:]]
            if len(recent_messages) >= 3:
                conversation_boost = 0.2
            elif len(recent_messages) >= 2:
                conversation_boost = 0.1
        
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
    "controversy_tolerance": "moderate"
} 