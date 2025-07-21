"""
Comprehensive tests for N8NFrontendService.

This test suite follows the testing framework revamp plan principles:
- Uses pytest fixtures and dependency injection
- Tests both success and error cases
- Validates event emissions and service interactions
- Includes integration tests for complete frontend operations
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from app.services.n8n_frontend_service import N8NFrontendService
from app.ports.frontend_port import (
    DashboardOverview, SystemStatus, CharacterStatus, ScenarioCreate,
    ScenarioResult, CustomNews, NewsInjectionResult, UserInteraction,
    CharacterResponse, FrontendEvent, EventBus
)
from app.services.n8n_integration import N8NWebhookService
from app.agents.agent_factory import AgentFactory
from app.services.demo_orchestrator import DemoOrchestrator


class TestN8NFrontendService:
    """Test suite for N8NFrontendService."""
    
    @pytest.fixture
    def mock_n8n_webhook_service(self):
        """Mock N8N webhook service for testing."""
        service = MagicMock(spec=N8NWebhookService)
        service.get_status.return_value = {
            "session_active": True,
            "total_events_sent": 42,
            "last_event_time": "2024-01-01T12:00:00Z"
        }
        return service
    
    @pytest.fixture
    def mock_agent_factory(self):
        """Mock agent factory for testing."""
        factory = MagicMock(spec=AgentFactory)
        # Return a dictionary with agent IDs as keys
        mock_agent_1 = MagicMock()
        mock_agent_1.name = "Jovani Vazquez"
        mock_agent_1.personality_traits = ["friendly", "helpful"]
        
        mock_agent_2 = MagicMock()
        mock_agent_2.name = "Politico Boricua"
        mock_agent_2.personality_traits = ["political", "engaging"]
        
        # get_active_agents should return a dictionary, not a list
        factory.get_active_agents.return_value = {
            "jovani_vazquez": mock_agent_1,
            "politico_boricua": mock_agent_2
        }
        factory.get_all_agents.return_value = {
            "jovani_vazquez": mock_agent_1,
            "politico_boricua": mock_agent_2
        }
        return factory
    
    @pytest.fixture
    def mock_demo_orchestrator(self):
        """Mock demo orchestrator for testing."""
        orchestrator = MagicMock(spec=DemoOrchestrator)
        orchestrator.get_available_scenarios.return_value = ["scenario_001", "scenario_002"]
        # Demo orchestrator doesn't have get_active_scenarios, use get_running_scenarios instead
        orchestrator.get_running_scenarios.return_value = ["scenario_001", "scenario_002"]
        return orchestrator
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus for testing."""
        event_bus = AsyncMock(spec=EventBus)
        event_bus.publish_event = AsyncMock()
        return event_bus
    
    @pytest.fixture
    def n8n_frontend_service(self, mock_n8n_webhook_service, mock_agent_factory, mock_demo_orchestrator, mock_event_bus):
        """N8N frontend service with mocked dependencies."""
        return N8NFrontendService(
            n8n_webhook_service=mock_n8n_webhook_service,
            agent_factory=mock_agent_factory,
            demo_orchestrator=mock_demo_orchestrator,
            event_bus=mock_event_bus
        )
    
    @pytest.fixture
    def sample_scenario_create(self):
        """Sample scenario creation request for testing."""
        return ScenarioCreate(
            name="Test Scenario",
            description="A test scenario for unit testing",
            character_ids=["jovani_vazquez"],
            news_items=[
                {
                    "headline": "Test News Headline",
                    "content": "Test news content",
                    "topics": ["test", "news"],
                    "source": "Test Source"
                }
            ],
            execution_mode="immediate"
        )
    
    @pytest.fixture
    def sample_custom_news(self):
        """Sample custom news for testing."""
        return CustomNews(
            title="Custom Test News",
            content="This is custom test news content",
            source="Test Source",
            category="test",
            priority=1,
            custom_metadata={"topics": ["custom", "test"], "relevance_score": 0.8}
        )
    
    @pytest.fixture
    def sample_user_interaction(self):
        """Sample user interaction for testing."""
        return UserInteraction(
            character_id="jovani_vazquez",
            message="Hello, how are you?",
            session_id="test_session_001",
            context={"timestamp": datetime.now(timezone.utc)}
        )

    @pytest.mark.asyncio
    async def test_get_dashboard_overview_success(self, n8n_frontend_service, mock_n8n_webhook_service, mock_agent_factory):
        """Test successful dashboard overview retrieval."""
        # Act
        overview = await n8n_frontend_service.get_dashboard_overview()
        
        # Assert
        assert isinstance(overview, DashboardOverview)
        assert overview.system.status == "healthy"
        assert overview.system.active_characters == 2  # From mock agent factory
        assert overview.system.total_events == 42
        assert len(overview.characters) == 2
        
        # Verify service calls
        mock_n8n_webhook_service.get_status.assert_called_once()
        mock_agent_factory.get_active_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_n8n_error(self, mock_n8n_webhook_service, mock_agent_factory, mock_demo_orchestrator, mock_event_bus):
        """Test dashboard overview with N8N service error."""
        # Arrange
        mock_n8n_webhook_service.get_status.side_effect = Exception("N8N service unavailable")
        service = N8NFrontendService(
            n8n_webhook_service=mock_n8n_webhook_service,
            agent_factory=mock_agent_factory,
            demo_orchestrator=mock_demo_orchestrator,
            event_bus=mock_event_bus
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="N8N service unavailable"):
            await service.get_dashboard_overview()
    
    @pytest.mark.asyncio
    async def test_get_character_status(self, n8n_frontend_service, mock_agent_factory):
        """Test getting character status."""
        # Act
        character_statuses = await n8n_frontend_service.get_character_status()
        
        # Assert
        assert isinstance(character_statuses, list)
        assert len(character_statuses) == 2
        
        # Verify each character status has required fields
        for status in character_statuses:
            assert hasattr(status, 'id')  # CharacterStatus uses 'id', not 'character_id'
            assert hasattr(status, 'status')
            assert hasattr(status, 'last_activity')
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_success(self, n8n_frontend_service, sample_scenario_create, mock_event_bus):
        """Test successful custom scenario creation."""
        # Act
        result = await n8n_frontend_service.create_custom_scenario(sample_scenario_create)
        
        # Assert
        assert isinstance(result, ScenarioResult)
        assert result.status == "success"
        assert result.scenario_id is not None
        assert result.result["news_items_processed"] == 1
        assert result.result["characters_involved"] == ["jovani_vazquez"]
        
        # Verify event emissions
        assert mock_event_bus.publish_event.call_count == 2  # Started + news injection events
        started_event = mock_event_bus.publish_event.call_args_list[0][0][0]
        assert started_event.event_type == "scenario_started"
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_invalid(self, n8n_frontend_service, mock_event_bus):
        """Test custom scenario creation with invalid configuration."""
        # Arrange
        invalid_scenario = ScenarioCreate(
            name="Invalid Scenario",
            description="Invalid scenario",
            character_ids=[],  # Empty character list
            news_items=[],     # Empty news items
            execution_mode="immediate"
        )
        
        # Act
        result = await n8n_frontend_service.create_custom_scenario(invalid_scenario)
        
        # Assert
        assert result.status == "failed"
        assert "Invalid scenario configuration" in result.error
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_execution_error(self, n8n_frontend_service, sample_scenario_create, mock_event_bus):
        """Test custom scenario creation with execution error."""
        # Arrange
        mock_event_bus.publish_event.side_effect = Exception("Event bus error")
        
        # Act
        result = await n8n_frontend_service.create_custom_scenario(sample_scenario_create)
        
        # Assert
        assert result.status == "failed"
        assert "Event bus error" in result.error
        # Verify that the error was logged
        assert mock_event_bus.publish_event.called
    
    @pytest.mark.asyncio
    async def test_inject_custom_news_success(self, n8n_frontend_service, sample_custom_news, mock_event_bus):
        """Test successful custom news injection."""
        # Act
        result = await n8n_frontend_service.inject_custom_news(sample_custom_news)
        
        # Assert
        assert isinstance(result, NewsInjectionResult)
        assert result.status == "injected"
        assert result.news_id is not None
        assert result.injected_at is not None
        
        # Verify event emission
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "custom_news_injected"
        assert event_call.data["news"]["title"] == sample_custom_news.title
    
    @pytest.mark.asyncio
    async def test_inject_custom_news_error(self, n8n_frontend_service, sample_custom_news, mock_event_bus):
        """Test custom news injection with error."""
        # Arrange
        mock_event_bus.publish_event.side_effect = Exception("Event bus error")
        
        # Act
        result = await n8n_frontend_service.inject_custom_news(sample_custom_news)
        
        # Assert
        assert result.status == "failed"
        assert "Event bus error" in result.error
        # Verify that the error was logged
        assert mock_event_bus.publish_event.called
    
    @pytest.mark.asyncio
    async def test_user_interact_with_character_success(self, n8n_frontend_service, sample_user_interaction, mock_agent_factory, mock_event_bus):
        """Test successful user interaction with character."""
        # Arrange
        mock_agent = AsyncMock()
        mock_agent.generate_response.return_value = "Hello! I'm doing great, thanks for asking!"
        mock_agent_factory.get_agent.return_value = mock_agent
        
        # Act
        response = await n8n_frontend_service.user_interact_with_character(sample_user_interaction)
        
        # Assert
        assert isinstance(response, CharacterResponse)
        assert response.character_id == "jovani_vazquez"
        assert response.message == "Hello! I'm doing great, thanks for asking!"
        assert response.timestamp is not None
        
        # Verify agent factory and agent calls
        mock_agent_factory.get_agent.assert_called_once_with("jovani_vazquez")
        # The actual method call includes a context dictionary, not separate parameters
        mock_agent.generate_response.assert_called_once()
        call_args = mock_agent.generate_response.call_args[0][0]
        assert isinstance(call_args, dict)
        assert call_args["user_message"] == sample_user_interaction.message
        
        # Verify event emission
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "user_character_interaction"
    
    @pytest.mark.asyncio
    async def test_user_interact_with_character_agent_not_found(self, n8n_frontend_service, sample_user_interaction, mock_agent_factory):
        """Test user interaction with non-existent character."""
        # Arrange
        mock_agent_factory.get_agent.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Character jovani_vazquez not found"):
            await n8n_frontend_service.user_interact_with_character(sample_user_interaction)
    
    @pytest.mark.asyncio
    async def test_user_interact_with_character_agent_error(self, n8n_frontend_service, sample_user_interaction, mock_agent_factory):
        """Test user interaction with agent error."""
        # Arrange
        mock_agent = AsyncMock()
        mock_agent.generate_response.side_effect = Exception("Agent generation error")
        mock_agent_factory.get_agent.return_value = mock_agent
        
        # Act & Assert
        with pytest.raises(Exception, match="Agent generation error"):
            await n8n_frontend_service.user_interact_with_character(sample_user_interaction)
    
    @pytest.mark.asyncio
    async def test_get_active_agents(self, n8n_frontend_service, mock_agent_factory):
        """Test getting active agents."""
        # Act
        active_agents = n8n_frontend_service._get_active_agents()
        
        # Assert
        assert isinstance(active_agents, list)
        assert len(active_agents) == 2
        assert "jovani_vazquez" in active_agents
        assert "politico_boricua" in active_agents
        
        # Verify agent factory call
        mock_agent_factory.get_active_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_scenarios(self, n8n_frontend_service, mock_demo_orchestrator):
        """Test getting active scenarios."""
        # Act
        active_scenarios = n8n_frontend_service._get_active_scenarios()
        
        # Assert
        assert isinstance(active_scenarios, list)
        assert len(active_scenarios) == 2
        assert "scenario_001" in active_scenarios
        assert "scenario_002" in active_scenarios
        
        # Verify demo orchestrator call
        mock_demo_orchestrator.get_running_scenarios.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_scenario_valid(self, n8n_frontend_service, sample_scenario_create):
        """Test scenario validation with valid scenario."""
        # Act
        is_valid = n8n_frontend_service._validate_scenario(sample_scenario_create)
        
        # Assert
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_scenario_invalid(self, n8n_frontend_service):
        """Test scenario validation with invalid scenario."""
        # Arrange
        invalid_scenario = ScenarioCreate(
            name="",
            description="",
            character_ids=[],
            news_items=[],
            execution_mode="invalid_mode"
        )
        
        # Act
        is_valid = n8n_frontend_service._validate_scenario(invalid_scenario)
        
        # Assert
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_parse_datetime_valid(self, n8n_frontend_service):
        """Test datetime parsing with valid string."""
        # Arrange
        datetime_str = "2024-01-01T12:00:00Z"
        
        # Act
        parsed_datetime = n8n_frontend_service._parse_datetime(datetime_str)
        
        # Assert
        assert isinstance(parsed_datetime, datetime)
        assert parsed_datetime.year == 2024
        assert parsed_datetime.month == 1
        assert parsed_datetime.day == 1
    
    @pytest.mark.asyncio
    async def test_parse_datetime_none(self, n8n_frontend_service):
        """Test datetime parsing with None value."""
        # Act
        parsed_datetime = n8n_frontend_service._parse_datetime(None)
        
        # Assert
        assert parsed_datetime is None
    
    @pytest.mark.asyncio
    async def test_parse_datetime_invalid(self, n8n_frontend_service):
        """Test datetime parsing with invalid string."""
        # Arrange
        invalid_datetime_str = "invalid_datetime"
        
        # Act
        parsed_datetime = n8n_frontend_service._parse_datetime(invalid_datetime_str)
        
        # Assert
        assert parsed_datetime is None


class TestN8NFrontendServiceIntegration:
    """Integration tests for N8NFrontendService."""
    
    @pytest.fixture
    def integration_n8n_frontend_service(self):
        """N8N frontend service with real dependencies for integration testing."""
        # This would use real services in integration tests
        # For now, we'll use mocks but test the complete flow
        mock_n8n_webhook_service = MagicMock()
        mock_agent_factory = MagicMock()
        mock_demo_orchestrator = MagicMock()
        mock_event_bus = AsyncMock()
        
        return N8NFrontendService(
            n8n_webhook_service=mock_n8n_webhook_service,
            agent_factory=mock_agent_factory,
            demo_orchestrator=mock_demo_orchestrator,
            event_bus=mock_event_bus
        )
    
    @pytest.mark.asyncio
    async def test_complete_dashboard_flow(self, integration_n8n_frontend_service):
        """Test complete dashboard flow from overview to character interaction."""
        # Arrange
        integration_n8n_frontend_service.n8n_webhook_service.get_status.return_value = {
            "session_active": True,
            "total_events_sent": 100,
            "last_event_time": "2024-01-01T12:00:00Z"
        }
        
        # Mock agent for integration test
        mock_agent = MagicMock()
        mock_agent.name = "Jovani Vazquez"
        mock_agent.personality_traits = ["friendly", "helpful"]
        
        integration_n8n_frontend_service.agent_factory.get_active_agents.return_value = {
            "jovani_vazquez": mock_agent
        }
        integration_n8n_frontend_service.agent_factory.get_all_agents.return_value = {
            "jovani_vazquez": mock_agent
        }
        
        # Mock agent for interaction testing
        mock_interaction_agent = AsyncMock()
        mock_interaction_agent.generate_response.return_value = "Integration test response"
        integration_n8n_frontend_service.agent_factory.get_agent.return_value = mock_interaction_agent
        
        # Act - Get dashboard overview
        overview = await integration_n8n_frontend_service.get_dashboard_overview()
        
        # Assert overview
        assert overview.system.status == "healthy"
        assert overview.system.active_characters == 1
        
        # Act - Get character status
        character_statuses = await integration_n8n_frontend_service.get_character_status()
        
        # Assert character statuses
        assert len(character_statuses) == 1
        assert character_statuses[0].id == "jovani_vazquez"  # CharacterStatus uses 'id', not 'character_id'
        
        # Act - User interaction
        interaction = UserInteraction(
            character_id="jovani_vazquez",
            message="Integration test message",
            session_id="integration_session",
            timestamp=datetime.now(timezone.utc)
        )
        
        response = await integration_n8n_frontend_service.user_interact_with_character(interaction)
        
        # Assert interaction response
        assert response.character_id == "jovani_vazquez"
        assert response.message == "Integration test response"  # CharacterResponse uses 'message', not 'response'
        
        # Verify all service interactions
        integration_n8n_frontend_service.n8n_webhook_service.get_status.assert_called()
        integration_n8n_frontend_service.agent_factory.get_active_agents.assert_called()
        integration_n8n_frontend_service.agent_factory.get_agent.assert_called()
        mock_interaction_agent.generate_response.assert_called()
        assert integration_n8n_frontend_service.event_bus.publish_event.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_complete_scenario_flow(self, integration_n8n_frontend_service):
        """Test complete scenario flow from creation to execution."""
        # Arrange
        scenario = ScenarioCreate(
            name="Integration Test Scenario",
            description="Complete scenario flow test",
            character_ids=["jovani_vazquez"],
            news_items=[
                {
                    "headline": "Integration Test News",
                    "content": "This is integration test news",
                    "topics": ["integration", "test"],
                    "source": "Integration Test"
                }
            ],
            execution_mode="immediate"
        )
        
        # Act
        result = await integration_n8n_frontend_service.create_custom_scenario(scenario)
        
        # Assert
        assert result.status == "success"
        assert result.scenario_id is not None
        assert result.result["news_items_processed"] == 1
        assert result.result["characters_involved"] == ["jovani_vazquez"]
        
        # Verify event emissions
        assert integration_n8n_frontend_service.event_bus.publish_event.call_count == 2
        
        # Check scenario started event
        started_event = integration_n8n_frontend_service.event_bus.publish_event.call_args_list[0][0][0]
        assert started_event.event_type == "scenario_started"
        assert started_event.data["scenario_id"] == result.scenario_id
        
        # Check news injection event
        news_event = integration_n8n_frontend_service.event_bus.publish_event.call_args_list[1][0][0]
        assert news_event.event_type == "custom_news_injected"
        assert news_event.data["scenario_id"] == result.scenario_id 