"""
Frontend Port - Abstract interfaces for frontend operations.

This module defines the abstract interfaces that frontend implementations must follow,
following the Ports & Adapters pattern used throughout the project.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


# Domain Models
class SystemStatus(BaseModel):
    """System status information"""
    status: str  # "healthy", "degraded", "down"
    uptime: float
    active_characters: int
    total_events: int
    last_event_time: Optional[datetime]
    demo_mode: bool


class CharacterStatus(BaseModel):
    """Character status information"""
    id: str
    name: str
    status: str  # "active", "thinking", "responding", "idle"
    last_activity: Optional[datetime]
    engagement_count: int
    response_count: int
    personality_traits: List[str]


class DashboardOverview(BaseModel):
    """Complete dashboard overview"""
    system: SystemStatus
    characters: List[CharacterStatus]
    recent_events: List[Dict[str, Any]]
    active_scenarios: List[str]
    analytics: "AnalyticsSummary"


class AnalyticsSummary(BaseModel):
    """Analytics summary for dashboard"""
    total_interactions: int = 0
    favorite_characters: List[str] = []
    engagement_rate: float = 0.0
    session_duration: float = 0.0


class UserSession(BaseModel):
    """User session information"""
    session_id: str
    user_id: Optional[str]
    permissions: List[str]
    preferences: Dict[str, Any]
    created_at: datetime
    last_activity: datetime


class FrontendEvent(BaseModel):
    """Frontend event for real-time communication"""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    session_id: Optional[str] = None


class ScenarioCreate(BaseModel):
    """Request to create a custom scenario"""
    name: str
    description: str
    character_ids: List[str]
    news_items: List[Dict[str, Any]]
    execution_speed: float = 1.0
    custom_parameters: Dict[str, Any] = {}


class ScenarioResult(BaseModel):
    """Result of scenario execution"""
    scenario_id: str
    status: str  # "success", "failed", "running"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CustomNews(BaseModel):
    """Custom news for injection"""
    title: str
    content: str
    source: str
    category: str
    priority: int = 1
    custom_metadata: Dict[str, Any] = {}


class NewsInjectionResult(BaseModel):
    """Result of news injection"""
    news_id: str
    status: str
    injected_at: datetime
    processed_by: List[str] = []
    error: Optional[str] = None


class UserInteraction(BaseModel):
    """User interaction with a character"""
    session_id: str
    character_id: str
    message: str
    context: Dict[str, Any] = {}


class CharacterResponse(BaseModel):
    """Character response to user interaction"""
    character_id: str
    message: str
    timestamp: datetime
    context: Dict[str, Any] = {}


# Abstract Interfaces
class FrontendPort(ABC):
    """
    Abstract interface for frontend operations.
    
    This defines the contract that all frontend implementations must follow,
    ensuring consistency and testability across different frontend providers.
    """
    
    @abstractmethod
    async def get_dashboard_overview(self) -> DashboardOverview:
        """
        Get comprehensive dashboard overview.
        
        Returns:
            DashboardOverview: Complete dashboard data including system status,
                              character statuses, recent events, and analytics.
        """
        pass
    
    @abstractmethod
    async def get_character_status(self) -> List[CharacterStatus]:
        """
        Get status of all AI characters.
        
        Returns:
            List[CharacterStatus]: List of all character statuses.
        """
        pass
    
    @abstractmethod
    async def create_custom_scenario(self, scenario: ScenarioCreate) -> ScenarioResult:
        """
        Create and execute custom scenario.
        
        Args:
            scenario: Scenario configuration to create and execute.
            
        Returns:
            ScenarioResult: Result of scenario execution.
        """
        pass
    
    @abstractmethod
    async def inject_custom_news(self, news: CustomNews) -> NewsInjectionResult:
        """
        Inject custom news for testing.
        
        Args:
            news: Custom news to inject into the system.
            
        Returns:
            NewsInjectionResult: Result of news injection.
        """
        pass
    
    @abstractmethod
    async def user_interact_with_character(self, interaction: UserInteraction) -> CharacterResponse:
        """
        Allow users to interact directly with AI characters.
        
        Args:
            interaction: User interaction details.
            
        Returns:
            CharacterResponse: Character's response to the interaction.
        """
        pass


class EventBus(ABC):
    """
    Abstract interface for event communication.
    
    This defines the contract for real-time event communication between
    frontend components and the backend system.
    """
    
    @abstractmethod
    async def publish_event(self, event: FrontendEvent) -> None:
        """
        Publish frontend event to all subscribers.
        
        Args:
            event: Event to publish.
        """
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, session_id: str):
        """
        Subscribe to frontend events for a session.
        
        Args:
            session_id: Session ID to subscribe for.
            
        Yields:
            FrontendEvent: Events for the session.
        """
        pass


class UserSessionManager(ABC):
    """
    Abstract interface for user session management.
    
    This defines the contract for managing user sessions, permissions,
    and preferences.
    """
    
    @abstractmethod
    async def create_session(self, user_id: Optional[str] = None) -> UserSession:
        """
        Create new user session.
        
        Args:
            user_id: Optional user ID for authenticated sessions.
            
        Returns:
            UserSession: Created session information.
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID to retrieve.
            
        Returns:
            Optional[UserSession]: Session information if found.
        """
        pass
    
    @abstractmethod
    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp.
        
        Args:
            session_id: Session ID to update.
            
        Returns:
            bool: True if session was updated successfully.
        """
        pass
    
    @abstractmethod
    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_id: Session ID to invalidate.
            
        Returns:
            bool: True if session was invalidated successfully.
        """
        pass


class AnalyticsEngine(ABC):
    """
    Abstract interface for analytics processing.
    
    This defines the contract for analytics data processing and retrieval.
    """
    
    @abstractmethod
    async def get_user_analytics(self, user_id: Optional[str]) -> AnalyticsSummary:
        """
        Get analytics summary for a specific user.
        
        Args:
            user_id: User ID to get analytics for.
            
        Returns:
            AnalyticsSummary: Analytics summary for the user.
        """
        pass
    
    @abstractmethod
    async def track_event(self, event: FrontendEvent) -> None:
        """
        Track frontend event for analytics.
        
        Args:
            event: Event to track.
        """
        pass 