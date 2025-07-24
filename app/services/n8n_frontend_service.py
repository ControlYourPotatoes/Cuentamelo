"""
N8N Frontend Service - N8N-specific implementation of frontend operations.

This module implements the FrontendPort interface specifically for N8N,
integrating with the existing N8N webhook service and demo orchestrator.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from app.ports.frontend_port import (
    FrontendPort, DashboardOverview, SystemStatus, CharacterStatus,
    ScenarioCreate, ScenarioResult, CustomNews, NewsInjectionResult,
    UserInteraction, CharacterResponse, FrontendEvent
)
from app.services.n8n_integration import N8NWebhookService
from app.agents.agent_factory import AgentFactory
from app.services.demo_orchestrator import DemoOrchestrator
from app.ports.frontend_port import EventBus
from app.config import get_settings

logger = logging.getLogger(__name__)


class N8NFrontendService(FrontendPort):
    """
    N8N-specific implementation of frontend operations.
    
    This service integrates with the existing N8N webhook service and demo orchestrator
    to provide frontend functionality while maintaining backward compatibility.
    """
    
    def __init__(
        self,
        n8n_webhook_service: N8NWebhookService,
        agent_factory: AgentFactory,
        demo_orchestrator: DemoOrchestrator,
        event_bus: EventBus
    ):
        """
        Initialize N8N frontend service.
        
        Args:
            n8n_webhook_service: N8N webhook service for event communication
            agent_factory: Agent factory for character management
            demo_orchestrator: Demo orchestrator for scenario management
            event_bus: Event bus for real-time communication
        """
        self.n8n_webhook_service = n8n_webhook_service
        self.agent_factory = agent_factory
        self.demo_orchestrator = demo_orchestrator
        self.event_bus = event_bus
        self.settings = get_settings()
        
        logger.info("N8N Frontend Service initialized")
    
    async def get_dashboard_overview(self) -> DashboardOverview:
        """
        Get comprehensive dashboard overview.
        
        Returns:
            DashboardOverview: Complete dashboard data including system status,
                              character statuses, recent events, and analytics.
        """
        try:
            # Get N8N service status
            n8n_status = self.n8n_webhook_service.get_status()
            
            # Create system status
            system_status = SystemStatus(
                status="healthy" if n8n_status.get("session_active", False) else "degraded",
                uptime=0.0,  # TODO: Implement uptime tracking
                active_characters=len(self._get_active_agents()),
                total_events=n8n_status.get("total_events_sent", 0),
                last_event_time=self._parse_datetime(n8n_status.get("last_event_time")),
                demo_mode=getattr(self.settings, 'DEMO_MODE_ENABLED', False)
            )
            
            # Get character statuses
            characters = await self._get_character_statuses()
            
            # Get recent events (placeholder for now)
            recent_events = []
            
            # Get active scenarios
            active_scenarios = self._get_active_scenarios()
            
            # Create analytics summary (placeholder for now)
            from app.ports.frontend_port import AnalyticsSummary
            analytics = AnalyticsSummary()
            
            return DashboardOverview(
                system=system_status,
                characters=characters,
                recent_events=recent_events,
                active_scenarios=active_scenarios,
                analytics=analytics
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            raise
    
    async def get_character_status(self) -> List[CharacterStatus]:
        """
        Get status of all AI characters.
        
        Returns:
            List[CharacterStatus]: List of all character statuses.
        """
        return await self._get_character_statuses()
    
    async def create_custom_scenario(self, scenario: ScenarioCreate) -> ScenarioResult:
        """
        Create and execute custom scenario.
        
        Args:
            scenario: Scenario configuration to create and execute.
            
        Returns:
            ScenarioResult: Result of scenario execution.
        """
        try:
            scenario_id = str(uuid.uuid4())
            
            # Validate scenario
            if not self._validate_scenario(scenario):
                return ScenarioResult(
                    scenario_id=scenario_id,
                    status="failed",
                    error="Invalid scenario configuration"
                )
            
            # Emit scenario started event
            await self.event_bus.publish_event(FrontendEvent(
                event_type="scenario_started",
                timestamp=datetime.now(timezone.utc),
                data={
                    "scenario_id": scenario_id,
                    "scenario": scenario.dict()
                },
                source="n8n_frontend_service"
            ))
            
            # Execute scenario using demo orchestrator
            # This is a simplified implementation - in practice, you'd want
            # more sophisticated scenario execution
            try:
                # For now, we'll just emit events to simulate scenario execution
                for news_item in scenario.news_items:
                    await self.event_bus.publish_event(FrontendEvent(
                        event_type="custom_news_injected",
                        timestamp=datetime.now(timezone.utc),
                        data={
                            "scenario_id": scenario_id,
                            "news_item": news_item
                        },
                        source="n8n_frontend_service"
                    ))
                
                return ScenarioResult(
                    scenario_id=scenario_id,
                    status="success",
                    result={
                        "executed_at": datetime.now(timezone.utc).isoformat(),
                        "news_items_processed": len(scenario.news_items),
                        "characters_involved": scenario.character_ids
                    }
                )
                
            except Exception as e:
                logger.error(f"Error executing scenario {scenario_id}: {e}")
                return ScenarioResult(
                    scenario_id=scenario_id,
                    status="failed",
                    error=str(e)
                )
                
        except Exception as e:
            logger.error(f"Error creating custom scenario: {e}")
            return ScenarioResult(
                scenario_id=str(uuid.uuid4()),
                status="failed",
                error=str(e)
            )
    
    async def inject_custom_news(self, news: CustomNews) -> NewsInjectionResult:
        """
        Inject custom news for testing.
        
        Args:
            news: Custom news to inject into the system.
            
        Returns:
            NewsInjectionResult: Result of news injection.
        """
        try:
            news_id = str(uuid.uuid4())
            
            # Emit news injection event
            await self.event_bus.publish_event(FrontendEvent(
                event_type="custom_news_injected",
                timestamp=datetime.now(timezone.utc),
                data={
                    "news_id": news_id,
                    "news": news.model_dump()
                },
                source="n8n_frontend_service"
            ))
            
            # Also emit to N8N for visualization
            await self.n8n_webhook_service.emit_event(
                "custom_news_injected",
                {
                    "news_id": news_id,
                    "title": news.title,
                    "content": news.content,
                    "source": news.source,
                    "category": news.category,
                    "priority": news.priority
                }
            )
            
            return NewsInjectionResult(
                news_id=news_id,
                status="injected",
                injected_at=datetime.now(timezone.utc),
                processed_by=[]  # Will be populated as characters process the news
            )
            
        except Exception as e:
            logger.error(f"Error injecting custom news: {e}")
            return NewsInjectionResult(
                news_id=str(uuid.uuid4()),
                status="failed",
                injected_at=datetime.now(timezone.utc),
                processed_by=[],
                error=str(e)
            )
    
    async def user_interact_with_character(self, interaction: UserInteraction) -> CharacterResponse:
        """
        Allow users to interact directly with AI characters.
        
        Args:
            interaction: User interaction details.
            
        Returns:
            CharacterResponse: Character's response to the interaction.
        """
        try:
            # Get character agent
            agent = self.agent_factory.get_agent(interaction.character_id)
            if not agent:
                raise ValueError(f"Character {interaction.character_id} not found")
            
            # Create context for the character
            context = {
                "user_message": interaction.message,
                "user_context": interaction.context,
                "session_id": interaction.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "interaction_type": "direct_user_interaction"
            }
            
            # Generate character response
            # This assumes the agent has a generate_response method
            # You may need to adapt this based on your actual agent interface
            if hasattr(agent, 'generate_response'):
                response = await agent.generate_response(context)
            else:
                # Fallback response if agent doesn't have the method
                response = f"Hello! I'm {interaction.character_id}. You said: {interaction.message}"
            
            # Create character response object
            character_response = CharacterResponse(
                character_id=interaction.character_id,
                message=response,
                timestamp=datetime.now(timezone.utc),
                context=context
            )
            
            # Emit interaction event
            await self.event_bus.publish_event(FrontendEvent(
                event_type="user_character_interaction",
                timestamp=datetime.now(timezone.utc),
                data={
                    "interaction": interaction.dict(),
                    "response": character_response.dict()
                },
                source="n8n_frontend_service",
                session_id=interaction.session_id
            ))
            
            return character_response
            
        except Exception as e:
            logger.error(f"Error in user interaction: {e}")
            raise
    
    # Helper methods
    def _get_active_agents(self) -> List[str]:
        """Get list of active agent IDs."""
        try:
            # This depends on your agent factory implementation
            if hasattr(self.agent_factory, 'get_active_agents'):
                return list(self.agent_factory.get_active_agents().keys())
            elif hasattr(self.agent_factory, 'get_all_agents'):
                return list(self.agent_factory.get_all_agents().keys())
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting active agents: {e}")
            return []
    
    async def _get_character_statuses(self) -> List[CharacterStatus]:
        """Get status of all characters."""
        try:
            characters = []
            
            # Get all agents from factory
            if hasattr(self.agent_factory, 'get_all_agents'):
                agents = self.agent_factory.get_all_agents()
            else:
                agents = {}
            
            for agent_id, agent in agents.items():
                try:
                    character_status = CharacterStatus(
                        id=agent_id,
                        name=getattr(agent, 'name', agent_id),
                        status="active",  # TODO: Implement actual status tracking
                        last_activity=datetime.now(timezone.utc),
                        engagement_count=0,  # TODO: Implement engagement tracking
                        response_count=0,    # TODO: Implement response tracking
                        personality_traits=getattr(agent, 'personality_traits', [])
                    )
                    characters.append(character_status)
                except Exception as e:
                    logger.error(f"Error getting status for agent {agent_id}: {e}")
                    continue
            
            return characters
            
        except Exception as e:
            logger.error(f"Error getting character statuses: {e}")
            return []
    
    def _get_active_scenarios(self) -> List[str]:
        """Get list of active scenarios."""
        try:
            # This depends on your demo orchestrator implementation
            if hasattr(self.demo_orchestrator, 'get_running_scenarios'):
                return self.demo_orchestrator.get_running_scenarios()
            elif hasattr(self.demo_orchestrator, 'get_active_scenarios'):
                return self.demo_orchestrator.get_active_scenarios()
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting active scenarios: {e}")
            return []
    
    def _validate_scenario(self, scenario: ScenarioCreate) -> bool:
        """Validate scenario configuration."""
        try:
            # Basic validation
            if not scenario.name or not scenario.description:
                return False
            
            if not scenario.character_ids:
                return False
            
            if not scenario.news_items:
                return False
            
            if scenario.execution_speed <= 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating scenario: {e}")
            return False
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not datetime_str:
            return None
        
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Error parsing datetime {datetime_str}: {e}")
            return None 