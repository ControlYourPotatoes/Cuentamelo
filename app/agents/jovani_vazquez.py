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

logger = logging.getLogger(__name__)


class JovaniVazquezAgent(BaseCharacterAgent):
    """
    Jovani Vázquez AI Character Agent
    
    Personality: Energetic Puerto Rican influencer, slightly provocative but entertaining
    Language: Spanglish (Spanish/English mix) with local expressions
    Engagement: High (70% reply rate), quick responses (1-5 minutes)
    Topics: Entertainment, lifestyle, social issues, youth culture
    """
    
    def __init__(self, ai_provider=None):
        super().__init__(
            character_id="jovani_vazquez",
            ai_provider=ai_provider
        )
        
        # Jovani's engagement patterns (from personality data)
        self.high_energy_keywords = [
            "fiesta", "party", "música", "music", "baile", "dance", "show", 
            "evento", "event", "concierto", "concert", "trending", "viral",
            "nuevo", "new", "increíble", "amazing", "brutal", "wow"
        ]
        
        self.puerto_rico_keywords = [
            "puerto rico", "pr", "borinquen", "isla", "san juan", "bayamón",
            "carolina", "ponce", "caguas", "arecibo", "guaynabo", "río grande",
            "piragua", "mofongo", "pasteles", "lechón", "coquí", "el yunque",
            "viejo san juan", "condado", "isla verde", "luquillo"
        ]

    def calculate_engagement_probability(
        self,
        context: str,
        conversation_history: List[ConversationMessage] = None,
        news_item: NewsItem = None
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
        
        context_lower = context.lower()
        
        # Check for high-energy keywords
        energy_boost = 0.0
        for keyword in self.high_energy_keywords:
            if keyword in context_lower:
                energy_boost += 0.1
        energy_boost = min(energy_boost, 0.3)  # Cap at 0.3
        
        # Check for Puerto Rico relevance
        pr_boost = 0.0
        for keyword in self.puerto_rico_keywords:
            if keyword in context_lower:
                pr_boost += 0.15
        pr_boost = min(pr_boost, 0.4)  # Cap at 0.4
        
        # Topic relevance based on news item
        topic_boost = 0.0
        if news_item and news_item.topics:
            topic_scores = [
                self.personality_data.topic_weights.get(topic.lower(), 0.2) 
                for topic in news_item.topics
            ]
            if topic_scores:
                topic_boost = max(topic_scores) * 0.3
        
        # Check for conversation momentum
        conversation_boost = 0.0
        if conversation_history and len(conversation_history) > 0:
            # Jovani loves active conversations
            recent_messages = [msg for msg in conversation_history[-5:]]
            if len(recent_messages) >= 3:
                conversation_boost = 0.2
            elif len(recent_messages) >= 2:
                conversation_boost = 0.1
        
        # Sentiment/emotion detection (simple)
        emotion_boost = 0.0
        emotional_indicators = [
            "increíble", "amazing", "wow", "brutal", "genial", "awesome",
            "terrible", "horrible", "shocking", "loco", "crazy", "wild"
        ]
        for indicator in emotional_indicators:
            if indicator in context_lower:
                emotion_boost = 0.15
                break
        
        # Social media trending indicators
        trending_boost = 0.0
        trending_keywords = ["trending", "viral", "breaking", "urgent", "#", "@"]
        for keyword in trending_keywords:
            if keyword in context_lower:
                trending_boost = 0.1
                break
        
        # Calculate final probability
        final_probability = (
            base_probability + 
            energy_boost + 
            pr_boost + 
            topic_boost + 
            conversation_boost + 
            emotion_boost + 
            trending_boost
        )
        
        # Cap at 1.0
        final_probability = min(final_probability, 1.0)
        
        logger.info(
            f"Jovani engagement calc: base={base_probability}, "
            f"energy={energy_boost}, pr={pr_boost}, topic={topic_boost}, "
            f"conversation={conversation_boost}, emotion={emotion_boost}, "
            f"trending={trending_boost}, final={final_probability}"
        )
        
        return final_probability

    def get_topic_relevance(self, topics: List[str]) -> float:
        """Calculate topic relevance for Jovani."""
        if not topics:
            return 0.2
        
        relevance_scores = []
        for topic in topics:
            topic_lower = topic.lower()
            
            # Check exact matches first
            if topic_lower in self.personality_data.topic_weights:
                relevance_scores.append(self.personality_data.topic_weights[topic_lower])
                continue
            
            # Check partial matches
            max_partial_score = 0.0
            for weighted_topic, weight in self.personality_data.topic_weights.items():
                if weighted_topic in topic_lower or topic_lower in weighted_topic:
                    max_partial_score = max(max_partial_score, weight * 0.8)
            
            relevance_scores.append(max_partial_score if max_partial_score > 0 else 0.1)
        
        # Return the highest relevance score
        return max(relevance_scores) if relevance_scores else 0.2

    def get_character_specific_context(self, base_context: str) -> str:
        """Add Jovani-specific context and perspective."""
        
        jovani_context = f"""
{base_context}

JOVANI'S PERSPECTIVE:
Como puertorriqueño joven y influencer, reacciona con tu energía característica.
- Si es entertainment/cultura: ¡Muestra excitement y conocimiento!
- Si es social issue: Balancéa seriedad con tu humor natural
- Si es trending: ¡Jump on the trend con tu style único!
- Si es Puerto Rico related: Demuestra tu pride y conocimiento local
- Si es conversación: Keep the energy flowing con preguntas y engagement

RESPONSE STYLE REMINDERS:
- Use Spanglish naturally (pero not forced)
- High energy and enthusiasm always
- Use your signature phrases: {', '.join(self.personality_data.signature_phrases[:3])}
- Include relevant emojis: {', '.join(self.personality_data.emoji_preferences[:5])}
- Keep it authentic and engaging
- Show Puerto Rican pride and cultural knowledge

REMEMBER: You are Jovani Vázquez - the most energetic, entertaining, and authentic Puerto Rican influencer! 🔥🇵🇷
"""
        return jovani_context

    def _get_jovani_fallback_responses(self) -> List[str]:
        """Get Jovani-specific fallback responses when API fails."""
        return [
            "¡Ay, mi sistema está loco right now! 🤖 Dame un break que vuelvo enseguida 💯",
            "Wepa! Technical difficulties pero Jovani nunca se rinde 🔥 Volveré más fuerte 💪",
            "Jajaja el WiFi me está ghosting 😂 But I'll be back con más energy! 🚀",
            "¡Brutal! Sistema down pero mi spirit está UP ⬆️ Regreso ya mismo 🇵🇷",
            "Ay bendito, tech problems! Pero you know Jovani always comes back stronger 💯🔥"
        ]

    def _get_fallback_response(self, context: str) -> str:
        """Override with Jovani-specific fallback responses."""
        import random
        responses = self._get_jovani_fallback_responses()
        return random.choice(responses)

    def should_engage_in_controversy(self, context: str) -> bool:
        """
        Determine if Jovani should engage with potentially controversial content.
        
        Jovani is generally open to discussing social issues but avoids heavy politics.
        """
        context_lower = context.lower()
        
        # Topics Jovani is comfortable with
        safe_controversial_topics = [
            "social justice", "youth issues", "cultural representation",
            "entertainment industry", "social media", "trending topics"
        ]
        
        # Topics Jovani avoids
        avoided_topics = [
            "heavy politics", "partisan debates", "religious controversies",
            "extreme views", "personal attacks"
        ]
        
        # Check for safe controversial topics
        for topic in safe_controversial_topics:
            if topic in context_lower:
                return True
        
        # Check for avoided topics
        for topic in avoided_topics:
            if topic in context_lower:
                return False
        
        # Default to engaging if it's not clearly avoided
        return True

    def get_emotional_context_for_news(self, news_item: NewsItem) -> str:
        """
        Determine emotional context for news reactions.
        
        Jovani's emotional responses are based on topic relevance and content type.
        """
        if not news_item.topics:
            return "neutral"
        
        # Check for high-energy topics
        high_energy_topics = ["entertainment", "music", "parties", "events", "trending"]
        for topic in news_item.topics:
            if topic.lower() in high_energy_topics:
                return "excited"
        
        # Check for serious topics
        serious_topics = ["social justice", "community", "youth issues", "culture"]
        for topic in news_item.topics:
            if topic.lower() in serious_topics:
                return "concerned_but_hopeful"
        
        # Check for Puerto Rico specific content
        pr_keywords = ["puerto rico", "pr", "borinquen", "san juan", "isla"]
        content_lower = f"{news_item.headline} {news_item.content}".lower()
        for keyword in pr_keywords:
            if keyword in content_lower:
                return "proud_and_engaged"
        
        return "neutral"


def create_jovani_vazquez(ai_provider=None) -> JovaniVazquezAgent:
    """Factory function to create Jovani Vázquez agent."""
    return JovaniVazquezAgent(ai_provider=ai_provider)


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