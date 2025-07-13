"""
Orchestration Service Port - Clean interface for accessing the LangGraph layer.
This is the key abstraction that hides LangGraph complexity from external consumers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.conversation import NewsItem, ConversationThread, CharacterReaction


class OrchestrationRequest(BaseModel):
    """Request to process content through the orchestration system."""
    news_items: Optional[List[NewsItem]] = None
    conversation_context: Optional[str] = None
    target_characters: Optional[List[str]] = None
    priority: str = "normal"  # normal, high, urgent
    max_execution_time_ms: int = 30000  # 30 seconds default


class OrchestrationResult(BaseModel):
    """Result of orchestration processing."""
    success: bool
    execution_time_ms: int
    characters_processed: List[str]
    reactions_generated: List[CharacterReaction]
    conversations_created: List[ConversationThread]
    error_details: Optional[str] = None
    performance_metrics: Dict[str, Any]


class SystemStatus(BaseModel):
    """Current status of the orchestration system."""
    active: bool
    active_characters: List[str]
    pending_news_count: int
    active_conversations_count: int
    api_calls_this_hour: int
    last_activity: datetime
    health_score: float  # 0.0 to 1.0


class CharacterStatus(BaseModel):
    """Status of an individual character."""
    character_id: str
    character_name: str
    available: bool
    last_interaction: Optional[datetime]
    interaction_count_today: int
    current_cooldown_seconds: int
    engagement_rate: float


class OrchestrationServicePort(ABC):
    """
    Port (Interface) for the LangGraph orchestration system.
    
    This provides a clean, high-level interface to access the complex 
    LangGraph workflows without exposing implementation details.
    
    Benefits:
    - Hides LangGraph complexity from external consumers
    - Makes testing easier with mock implementations
    - Allows swapping orchestration engines
    - Provides consistent error handling
    """
    
    @abstractmethod
    async def process_content(self, request: OrchestrationRequest) -> OrchestrationResult:
        """
        Process content (news, conversations) through the character orchestration system.
        
        This is the main entry point for triggering character interactions.
        """
        pass
    
    @abstractmethod
    async def get_system_status(self) -> SystemStatus:
        """Get current status of the orchestration system."""
        pass
    
    @abstractmethod
    async def get_character_status(self, character_id: str) -> Optional[CharacterStatus]:
        """Get status of a specific character."""
        pass
    
    @abstractmethod
    async def get_all_characters_status(self) -> List[CharacterStatus]:
        """Get status of all characters in the system."""
        pass
    
    @abstractmethod
    async def add_news_item(self, news_item: NewsItem) -> bool:
        """Add a news item to the processing queue."""
        pass
    
    @abstractmethod
    async def force_character_interaction(
        self, 
        character_id: str, 
        context: str,
        bypass_cooldown: bool = False
    ) -> OrchestrationResult:
        """Force a specific character to interact with given context."""
        pass
    
    @abstractmethod
    async def pause_character(self, character_id: str) -> bool:
        """Temporarily pause a character from participating."""
        pass
    
    @abstractmethod
    async def resume_character(self, character_id: str) -> bool:
        """Resume a paused character."""
        pass
    
    @abstractmethod
    async def get_active_conversations(self) -> List[ConversationThread]:
        """Get all currently active conversation threads."""
        pass
    
    @abstractmethod
    async def get_recent_reactions(
        self, 
        character_id: Optional[str] = None,
        limit: int = 10
    ) -> List[CharacterReaction]:
        """Get recent character reactions."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the orchestration system is healthy."""
        pass
    
    @abstractmethod
    async def shutdown_gracefully(self) -> bool:
        """Gracefully shutdown the orchestration system."""
        pass 