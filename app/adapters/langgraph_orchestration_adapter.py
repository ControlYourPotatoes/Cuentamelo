"""
LangGraph Orchestration Adapter - Clean interface to access the LangGraph layer.
This is the key adapter that hides LangGraph complexity from external consumers.
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta, timezone

from app.ports.orchestration_service import (
    OrchestrationServicePort, OrchestrationRequest, OrchestrationResult,
    SystemStatus, CharacterStatus
)
from app.models.conversation import (
    NewsItem, ConversationThread, CharacterReaction, OrchestrationState,
    create_orchestration_state, is_character_available
)
from app.graphs.orchestrator import (
    execute_orchestration_cycle, get_orchestration_status,
    add_news_item, get_available_characters
)
from app.ports.ai_provider import AIProviderPort

logger = logging.getLogger(__name__)


class LangGraphOrchestrationAdapter(OrchestrationServicePort):
    """
    Adapter that provides clean access to the LangGraph orchestration system.
    
    This is THE KEY ABSTRACTION that solves your "accessing this layer" concern.
    
    Benefits:
    - Hides all LangGraph implementation details
    - Provides simple, testable interface
    - Handles error recovery and state management
    - Enables dependency injection for testing
    - Makes the system much more maintainable
    """
    
    def __init__(
        self,
        ai_provider: AIProviderPort,
        initial_characters: Optional[List[str]] = None
    ):
        """
        Initialize with dependency injection.
        
        Args:
            ai_provider: Injected AI provider (for flexibility/testing)
            initial_characters: Characters to start with
        """
        self.ai_provider = ai_provider
        self.orchestration_state: Optional[OrchestrationState] = None
        self.characters = get_available_characters()
        self._initialize_state(initial_characters or ["jovani_vazquez"])
    
    def _initialize_state(self, character_ids: List[str]):
        """Initialize the orchestration state."""
        self.orchestration_state = create_orchestration_state(character_ids)
        logger.info(f"Initialized orchestration with characters: {character_ids}")
    
    async def process_content(self, request: OrchestrationRequest) -> OrchestrationResult:
        """
        Process content through the character orchestration system.
        
        This is the main entry point - hides all LangGraph complexity!
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Handle different types of requests
            news_items = request.news_items or []
            
            # Filter to target characters if specified
            if request.target_characters:
                # TODO: Filter characters based on request
                pass
            
            # Execute the LangGraph orchestration cycle
            workflow_result = await execute_orchestration_cycle(
                news_items=news_items,
                existing_state=self.orchestration_state
            )
            
            # Update our state
            if workflow_result.get("orchestration_state"):
                self.orchestration_state = workflow_result["orchestration_state"]
            
            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Convert LangGraph results to our clean interface
            return OrchestrationResult(
                success=workflow_result.get("success", False),
                execution_time_ms=execution_time_ms,
                characters_processed=workflow_result.get("processing_characters", []),
                reactions_generated=workflow_result.get("character_reactions", []),
                conversations_created=workflow_result.get("new_conversations", []),
                error_details=workflow_result.get("error_details"),
                performance_metrics={
                    "workflow_step": workflow_result.get("workflow_step", "unknown"),
                    "langgraph_execution_time": workflow_result.get("execution_time_ms", 0),
                    "system_messages": workflow_result.get("system_messages", [])
                }
            )
            
        except Exception as e:
            logger.error(f"Error in orchestration processing: {str(e)}")
            return OrchestrationResult(
                success=False,
                execution_time_ms=0,
                characters_processed=[],
                reactions_generated=[],
                conversations_created=[],
                error_details=str(e),
                performance_metrics={}
            )
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status - clean, simple interface."""
        try:
            if not self.orchestration_state:
                return SystemStatus(
                    active=False,
                    active_characters=[],
                    pending_news_count=0,
                    active_conversations_count=0,
                    api_calls_this_hour=0,
                    last_activity=datetime.now(timezone.utc),
                    health_score=0.0
                )
            
            # Get status from the orchestration state
            status_data = await get_orchestration_status(self.orchestration_state)
            
            # Calculate health score based on system metrics
            health_score = self._calculate_health_score(status_data)
            
            return SystemStatus(
                active=status_data.get("active", False),
                active_characters=status_data.get("active_characters", []),
                pending_news_count=status_data.get("pending_news", 0),
                active_conversations_count=status_data.get("active_conversations", 0),
                api_calls_this_hour=status_data.get("api_calls_this_hour", 0),
                last_activity=datetime.fromisoformat(status_data.get("last_activity", datetime.now(timezone.utc).isoformat())),
                health_score=health_score
            )
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return SystemStatus(
                active=False,
                active_characters=[],
                pending_news_count=0,
                active_conversations_count=0,
                api_calls_this_hour=0,
                last_activity=datetime.now(timezone.utc),
                health_score=0.0
            )
    
    async def get_character_status(self, character_id: str) -> Optional[CharacterStatus]:
        """Get status of a specific character."""
        try:
            if not self.orchestration_state:
                return None
            
            agent_state = self.orchestration_state.character_states.get(character_id)
            if not agent_state:
                return None
            
            # Calculate cooldown seconds
            cooldown_seconds = 0
            if agent_state.cooldown_until:
                remaining = agent_state.cooldown_until - datetime.now(timezone.utc)
                cooldown_seconds = max(0, int(remaining.total_seconds()))
            
            return CharacterStatus(
                character_id=character_id,
                character_name=agent_state.character_name,
                available=is_character_available(agent_state),
                last_interaction=agent_state.last_interaction_time,
                interaction_count_today=agent_state.interaction_count,
                current_cooldown_seconds=cooldown_seconds,
                engagement_rate=agent_state.engagement_rate
            )
            
        except Exception as e:
            logger.error(f"Error getting character status: {str(e)}")
            return None
    
    async def get_all_characters_status(self) -> List[CharacterStatus]:
        """Get status of all characters."""
        try:
            if not self.orchestration_state:
                return []
            
            statuses = []
            for character_id in self.orchestration_state.active_characters:
                status = await self.get_character_status(character_id)
                if status:
                    statuses.append(status)
            
            return statuses
            
        except Exception as e:
            logger.error(f"Error getting all character statuses: {str(e)}")
            return []
    
    async def add_news_item(self, news_item: NewsItem) -> bool:
        """Add news item to processing queue."""
        try:
            if not self.orchestration_state:
                return False
            
            await add_news_item(news_item, self.orchestration_state)
            return True
            
        except Exception as e:
            logger.error(f"Error adding news item: {str(e)}")
            return False
    
    async def force_character_interaction(
        self, 
        character_id: str, 
        context: str,
        bypass_cooldown: bool = False
    ) -> OrchestrationResult:
        """Force a specific character to interact."""
        try:
            # Create a special orchestration request for this character
            if bypass_cooldown and self.orchestration_state:
                agent_state = self.orchestration_state.character_states.get(character_id)
                if agent_state:
                    agent_state.cooldown_until = None
            
            # Create a synthetic news item for the interaction
            synthetic_news = NewsItem(
                headline="Direct Interaction Request",
                content=context,
                source="system",
                published_at=datetime.now(timezone.utc),
                topics=["forced_interaction"]
            )
            
            request = OrchestrationRequest(
                news_items=[synthetic_news],
                target_characters=[character_id],
                priority="high"
            )
            
            return await self.process_content(request)
            
        except Exception as e:
            logger.error(f"Error forcing character interaction: {str(e)}")
            return OrchestrationResult(
                success=False,
                execution_time_ms=0,
                characters_processed=[],
                reactions_generated=[],
                conversations_created=[],
                error_details=str(e),
                performance_metrics={}
            )
    
    async def pause_character(self, character_id: str) -> bool:
        """Pause a character from participating."""
        try:
            if not self.orchestration_state:
                return False
            
            agent_state = self.orchestration_state.character_states.get(character_id)
            if agent_state:
                # Set a very long cooldown to effectively pause the character
                agent_state.cooldown_until = datetime.now(timezone.utc) + timedelta(days=365)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error pausing character: {str(e)}")
            return False
    
    async def resume_character(self, character_id: str) -> bool:
        """Resume a paused character."""
        try:
            if not self.orchestration_state:
                return False
            
            agent_state = self.orchestration_state.character_states.get(character_id)
            if agent_state:
                agent_state.cooldown_until = None
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resuming character: {str(e)}")
            return False
    
    async def get_active_conversations(self) -> List[ConversationThread]:
        """Get all active conversation threads."""
        try:
            if not self.orchestration_state:
                return []
            
            return self.orchestration_state.active_conversations
            
        except Exception as e:
            logger.error(f"Error getting active conversations: {str(e)}")
            return []
    
    async def get_recent_reactions(
        self, 
        character_id: Optional[str] = None,
        limit: int = 10
    ) -> List[CharacterReaction]:
        """Get recent character reactions."""
        try:
            if not self.orchestration_state:
                return []
            
            reactions = self.orchestration_state.character_reactions
            
            # Filter by character if specified
            if character_id:
                reactions = [r for r in reactions if r.character_id == character_id]
            
            # Sort by timestamp and limit
            reactions.sort(key=lambda r: r.generated_at, reverse=True)
            return reactions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent reactions: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check system health."""
        try:
            # Check AI provider health
            ai_healthy = await self.ai_provider.health_check()
            
            # Check orchestration state
            state_healthy = self.orchestration_state is not None
            
            return ai_healthy and state_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def shutdown_gracefully(self) -> bool:
        """Gracefully shutdown the system."""
        try:
            if self.orchestration_state:
                self.orchestration_state.orchestration_active = False
            
            logger.info("Orchestration system shutdown gracefully")
            return True
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            return False
    
    def _calculate_health_score(self, status_data: Dict[str, Any]) -> float:
        """Calculate system health score from 0.0 to 1.0."""
        try:
            score = 1.0
            
            # Penalize if not active
            if not status_data.get("active", False):
                score -= 0.5
            
            # Penalize high API usage
            api_calls = status_data.get("api_calls_this_hour", 0)
            if api_calls > 80:
                score -= 0.2
            elif api_calls > 60:
                score -= 0.1
            
            # Penalize if no recent activity
            last_activity_str = status_data.get("last_activity")
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                time_since_activity = datetime.now(timezone.utc) - last_activity
                if time_since_activity > timedelta(hours=1):
                    score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default to neutral health score 