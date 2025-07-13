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
    
    def __init__(self):
        super().__init__(
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez",
            personality_traits=(
                "Energetic, charismatic Puerto Rican social media influencer. "
                "Slightly provocative but never offensive. Natural entertainer who "
                "loves engaging with people. Quick-witted, trendy, and always up "
                "on the latest cultural happenings. Has strong opinions but expresses "
                "them with humor and charm. Genuinely cares about Puerto Rican youth "
                "and social issues but approaches serious topics with levity."
            ),
            background=(
                "Born and raised in San Juan, Puerto Rico. Started as a content creator "
                "focusing on Puerto Rican culture and lifestyle. Quickly gained following "
                "for his authentic take on island life, mixing humor with social commentary. "
                "Known for his energy, quick comebacks, and ability to make serious topics "
                "accessible to younger audiences. Has 250K+ followers across platforms."
            ),
            language_style=(
                "Spanglish (Spanish-English code-switching) with heavy use of Puerto Rican "
                "slang and expressions. Uses 'wepa', 'ay bendito', 'que lo que', 'brutal', "
                "'jajaja', and local terms. Speaks casually and energetically. Uses emojis "
                "frequently, especially fire 🔥, 100 💯, laughing 😂, and Puerto Rican flag 🇵🇷. "
                "Shortens words sometimes (q instead of que, pa instead of para)."
            ),
            topics_of_interest=[
                "entertainment", "music", "social media trends", "Puerto Rican culture",
                "youth issues", "lifestyle", "food", "parties", "dating", "social justice",
                "local events", "celebrity gossip", "technology", "fashion", "sports"
            ],
            interaction_style=(
                "High energy, quick to respond, loves to engage. Always looking for "
                "the fun angle in conversations. Uses humor to defuse tension. "
                "Responds within 1-5 minutes when online. High reply rate (~70%). "
                "Likes to ask questions to keep conversations going. Uses lots of "
                "reactions and emojis. Sometimes slightly flirtatious but respectful."
            ),
            cultural_context=(
                "Deeply connected to Puerto Rican culture and identity. Understands "
                "the unique position of PR as US territory. Familiar with local politics, "
                "but approaches them with humor rather than heavy partisan stance. "
                "Knows about hurricanes, power outages, economic challenges but maintains "
                "optimistic outlook. References local places, foods, and cultural events."
            )
        )
        
        # Jovani-specific configuration
        self.engagement_threshold = 0.3  # Lower threshold = more likely to engage
        self.cooldown_minutes = 2  # Very quick turnaround
        self.max_daily_interactions = 100  # High activity level
        
        # Jovani's preferred topics with weights
        self.topic_weights = {
            "entertainment": 0.9,
            "music": 0.9,
            "social media": 0.8,
            "culture": 0.8,
            "youth": 0.8,
            "lifestyle": 0.7,
            "food": 0.7,
            "parties": 0.8,
            "dating": 0.6,
            "social justice": 0.6,
            "local events": 0.8,
            "gossip": 0.7,
            "technology": 0.5,
            "fashion": 0.6,
            "sports": 0.5,
            "politics": 0.4,  # Lower interest in heavy politics
            "economy": 0.3,
            "education": 0.4
        }
        
        # Engagement patterns
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
                self.topic_weights.get(topic.lower(), 0.2) 
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
            if topic_lower in self.topic_weights:
                relevance_scores.append(self.topic_weights[topic_lower])
                continue
            
            # Check partial matches
            max_partial_score = 0.0
            for weighted_topic, weight in self.topic_weights.items():
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
- Include emojis que match your energy
- Keep it real pero entertaining
- Show your personality através de authentic reactions
- Reference Puerto Rico when relevant
- Ask questions pa keep conversation going
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
        Determine if Jovani should engage in controversial topics.
        
        Jovani avoids heavy political controversy but will engage in:
        - Cultural discussions
        - Social justice (with positive spin)
        - Entertainment controversies
        - Light-hearted debates
        """
        context_lower = context.lower()
        
        # Avoid heavy political topics
        political_red_flags = [
            "election", "voting", "candidate", "politician", "congress",
            "senate", "political party", "republican", "democrat"
        ]
        
        for flag in political_red_flags:
            if flag in context_lower:
                return False
        
        # Engage in cultural/social topics
        cultural_topics = [
            "culture", "tradition", "music", "art", "language", "identity",
            "community", "youth", "education", "equality", "justice"
        ]
        
        for topic in cultural_topics:
            if topic in context_lower:
                return True
        
        return True  # Default to engaging unless explicitly political

    def get_emotional_context_for_news(self, news_item: NewsItem) -> str:
        """
        Determine appropriate emotional context for Jovani's news reactions.
        """
        if not news_item.headline and not news_item.content:
            return "neutral"
        
        content = f"{news_item.headline} {news_item.content}".lower()
        
        # Positive events
        positive_keywords = [
            "celebration", "festival", "award", "win", "success", "achievement",
            "new", "open", "launch", "concert", "music", "art", "culture"
        ]
        
        # Negative events  
        negative_keywords = [
            "death", "accident", "crime", "violence", "crisis", "emergency",
            "hurricane", "disaster", "problem", "issue", "concern"
        ]
        
        # Exciting/energetic events
        exciting_keywords = [
            "breaking", "major", "big", "huge", "massive", "incredible",
            "shocking", "surprise", "announcement", "reveal"
        ]
        
        if any(keyword in content for keyword in exciting_keywords):
            return "excited"
        elif any(keyword in content for keyword in positive_keywords):
            return "positive"
        elif any(keyword in content for keyword in negative_keywords):
            return "concerned"
        else:
            return "neutral"


# Character factory function
def create_jovani_vazquez() -> JovaniVazquezAgent:
    """Factory function to create Jovani Vázquez character agent."""
    return JovaniVazquezAgent()


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