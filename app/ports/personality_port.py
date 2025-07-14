"""
Personality port interface for character agents.
Defines the contract for personality data access and behavior.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from app.models.personality import PersonalityData
    from app.models.ai_personality_data import AIPersonalityData
    from app.models.agent_personality_data import AgentPersonalityData


class PersonalityTone(str, Enum):
    """Character personality tones."""
    ENTHUSIASTIC = "enthusiastic"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EDUCATIONAL = "educational"
    CONTROVERSIAL = "controversial"
    SUPPORTIVE = "supportive"
    PASSIONATE = "passionate"
    # Extended tones for more nuanced personalities
    APPRECIATIVE_THEATRICAL = "appreciative_theatrical"
    ENTHUSIASTIC_PERFORMATIVE = "enthusiastic_performative"
    WARM_CELEBRATORY = "warm_celebratory"
    PLAYFUL_ENERGETIC = "playful_energetic"
    AWKWARD_SERIOUS = "awkward_serious"


class LanguageStyle(str, Enum):
    """Character language styles."""
    SPANGLISH = "spanglish"
    FORMAL_SPANISH = "formal_spanish"
    CASUAL_SPANISH = "casual_spanish"
    ENGLISH = "english"
    PUERTO_RICAN_SLANG = "puerto_rican_slang"


class PersonalityPort(ABC):
    """
    Abstract interface for personality data and behavior.
    
    This port defines the contract that personality implementations must follow,
    separating personality concerns from agent behavior logic.
    """
    
    @property
    @abstractmethod
    def character_id(self) -> str:
        """Get the character's unique identifier."""
        pass
    
    @property
    @abstractmethod
    def character_name(self) -> str:
        """Get the character's display name."""
        pass
    
    @property
    @abstractmethod
    def character_type(self) -> str:
        """Get the character's type (influencer, politician, etc.)."""
        pass
    
    @property
    @abstractmethod
    def personality_traits(self) -> str:
        """Get the character's personality description."""
        pass
    
    @property
    @abstractmethod
    def language_style(self) -> LanguageStyle:
        """Get the character's preferred language style."""
        pass
    
    @property
    @abstractmethod
    def engagement_threshold(self) -> float:
        """Get the character's engagement threshold (0.0 to 1.0)."""
        pass
    
    @property
    @abstractmethod
    def cooldown_minutes(self) -> int:
        """Get the character's cooldown period in minutes."""
        pass
    
    @property
    @abstractmethod
    def max_daily_interactions(self) -> int:
        """Get the character's maximum daily interactions."""
        pass
    
    @property
    @abstractmethod
    def max_replies_per_thread(self) -> int:
        """Get the character's maximum replies per thread."""
        pass
    
    @property
    @abstractmethod
    def topics_of_interest(self) -> List[str]:
        """Get the character's topics of interest."""
        pass
    
    @property
    @abstractmethod
    def topic_weights(self) -> Dict[str, float]:
        """Get the character's topic weight preferences."""
        pass
    
    @property
    @abstractmethod
    def preferred_topics(self) -> List[str]:
        """Get the character's preferred topics."""
        pass
    
    @property
    @abstractmethod
    def avoided_topics(self) -> List[str]:
        """Get the character's avoided topics."""
        pass
    
    @property
    @abstractmethod
    def signature_phrases(self) -> List[str]:
        """Get the character's signature phrases."""
        pass
    
    @property
    @abstractmethod
    def emoji_preferences(self) -> List[str]:
        """Get the character's preferred emojis."""
        pass
    
    @property
    @abstractmethod
    def base_energy_level(self) -> float:
        """Get the character's base energy level (0.0 to 1.0)."""
        pass
    
    @abstractmethod
    def get_topic_relevance(self, topics: List[str]) -> float:
        """
        Calculate topic relevance for this character.
        
        Args:
            topics: List of topics to evaluate
            
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def get_emotional_context(self, content: str) -> str:
        """
        Determine emotional context for given content.
        
        Args:
            content: Content to analyze
            
        Returns:
            str: Emotional context (e.g., "excited", "concerned", "neutral")
        """
        pass
    
    @abstractmethod
    def should_engage_in_controversy(self, content: str) -> bool:
        """
        Determine if character should engage with potentially controversial content.
        
        Args:
            content: Content to evaluate
            
        Returns:
            bool: True if character should engage, False otherwise
        """
        pass
    
    @abstractmethod
    def get_response_template(self, response_type: str) -> str:
        """
        Get response template for specific type.
        
        Args:
            response_type: Type of response (e.g., "new_thread", "thread_reply")
            
        Returns:
            str: Response template
        """
        pass
    
    @abstractmethod
    def get_example_responses(self, topic: str) -> List[str]:
        """
        Get example responses for a specific topic.
        
        Args:
            topic: Topic to get examples for
            
        Returns:
            List[str]: List of example responses
        """
        pass
    
    @abstractmethod
    def get_character_context(self, base_context: str) -> str:
        """
        Add character-specific context to base context.
        
        Args:
            base_context: Base context to enhance
            
        Returns:
            str: Enhanced context with character perspective
        """
        pass
    
    @abstractmethod
    def get_fallback_responses(self) -> List[str]:
        """
        Get fallback responses for when AI generation fails.
        
        Returns:
            List[str]: List of fallback responses
        """
        pass
    
    @abstractmethod
    def calculate_engagement_boost(self, content: str) -> Dict[str, float]:
        """
        Calculate engagement boost factors for this character.
        
        Args:
            content: Content to analyze for engagement factors
            
        Returns:
            Dict[str, float]: Dictionary with boost factors (e.g., "energy", "pr_relevance", "emotion", "trending")
        """
        pass
    
    @abstractmethod
    def get_personality_data(self) -> 'PersonalityData':
        """
        Get the underlying PersonalityData object for AI providers.
        
        Returns:
            PersonalityData: The personality data object
        """
        pass
    
    @abstractmethod
    def get_ai_personality_data(self) -> 'AIPersonalityData':
        """
        Get the minimal AI personality data for AI providers.
        
        Returns:
            AIPersonalityData: The minimal AI personality data
        """
        pass
    
    @abstractmethod
    def get_agent_personality_data(self) -> 'AgentPersonalityData':
        """
        Get the minimal agent personality data for agent behavior.
        
        Returns:
            AgentPersonalityData: The minimal agent personality data
        """
        pass 