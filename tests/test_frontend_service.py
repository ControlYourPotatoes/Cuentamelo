"""
Tests for N8N Frontend Service.

This module tests the N8N frontend service which provides dashboard functionality,
scenario management, and user interactions through the N8N integration.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.services.n8n_frontend_service import N8NFrontendService
from app.services.n8n_integration import N8NWebhookService
from app.agents.agent_factory import AgentFactory
from app.services.demo_orchestrator import DemoOrchestrator
from app.ports.frontend_port import (
    FrontendEvent, EventBus, DashboardOverview, SystemStatus,
    CharacterStatus, ScenarioCreate, ScenarioResult, CustomNews,
    NewsInjectionResult, UserInteraction, CharacterResponse
)


class TestN8NFrontendService:
    """Test suite for N8NFrontendService."""
    
    @pytest.fixture
    def mock_n8n_webhook_service(self):
        """Mock N8N webhook service."""
        service = MagicMock(spec=N8NWebhookService)
        service.get_status.return_value = {
            "session_active": True,
            "total_events_sent": 42,
            "last_event_time": "2024-01-15T10:00:00Z"
        }
        return service
    
    @pytest.fixture
    def mock_agent_factory(self):
        """Mock agent factory."""
        factory = MagicMock(spec=AgentFactory)
        factory.get_available_agents.return_value = ["jovani_vazquez", "politico_boricua"]
        return factory
    
    @pytest.fixture
    def mock_demo_orchestrator(self):
        """Mock demo orchestrator."""
        orchestrator = MagicMock(spec=DemoOrchestrator)
        orchestrator.get_running_scenarios.return_value = ["scenario_001", "scenario_002"]
        return orchestrator
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus."""
        event_bus = AsyncMock(spec=EventBus)
        event_bus.publish_event = AsyncMock()
        return event_bus
    
    @pytest.fixture
    def frontend_service(self, mock_n8n_webhook_service, mock_agent_factory, mock_demo_orchestrator, mock_event_bus):
        """N8N frontend service with mocked dependencies."""
        return N8NFrontendService(
            n8n_webhook_service=mock_n8n_webhook_service,
            agent_factory=mock_agent_factory,
            demo_orchestrator=mock_demo_orchestrator,
            event_bus=mock_event_bus
        )
    
    @pytest.fixture
    def sample_scenario_create(self):
        """Sample scenario creation request."""
        return ScenarioCreate(
            name="Test Scenario",
            description="A test scenario for testing",
            character_ids=["jovani_vazquez"],
            news_items=[
                {
                    "title": "Test News",
                    "content": "Test content",
                    "source": "test",
                    "category": "test"
                }
            ],
            execution_speed=1.0,
            custom_parameters={"test": True}
        )
    
    @pytest.fixture
    def sample_custom_news(self):
        """Sample custom news request."""
        return CustomNews(
            title="Test News Title",
            content="Test news content for testing purposes.",
            source="test_source",
            category="test",
            priority=1,
            custom_metadata={"test": True}
        )
    
    @pytest.fixture
    def sample_user_interaction(self):
        """Sample user interaction request."""
        return UserInteraction(
            session_id="test_session_001",
            character_id="jovani_vazquez",
            message="Hello, how are you?",
            context={"user_name": "Test User"}
        )
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_success(self, frontend_service, mock_n8n_webhook_service):
        """Test successful dashboard overview retrieval."""
        # Act
        overview = await frontend_service.get_dashboard_overview()
        
        # Assert
        assert isinstance(overview, DashboardOverview)
        assert overview.system.status == "healthy"
        assert overview.system.active_characters == 2
        assert overview.system.total_events == 42
        assert overview.system.demo_mode is False  # Default from settings
        
        # Verify N8N service was called
        mock_n8n_webhook_service.get_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview_degraded_status(self, frontend_service, mock_n8n_webhook_service):
        """Test dashboard overview with degraded N8N status."""
        # Arrange
        mock_n8n_webhook_service.get_status.return_value = {
            "session_active": False,
            "total_events_sent": 0,
            "last_event_time": None
        }
        
        # Act
        overview = await frontend_service.get_dashboard_overview()
        
        # Assert
        assert overview.system.status == "degraded"
        assert overview.system.total_events == 0
    
    @pytest.mark.asyncio
    async def test_get_character_status(self, frontend_service, mock_agent_factory):
        """Test character status retrieval."""
        # Act
        characters = await frontend_service.get_character_status()
        
        # Assert
        assert isinstance(characters, list)
        assert len(characters) == 2
        
        # Verify all characters have required fields
        for char in characters:
            assert hasattr(char, 'id')
            assert hasattr(char, 'name')
            assert hasattr(char, 'status')
            assert hasattr(char, 'last_activity')
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_success(self, frontend_service, sample_scenario_create, mock_event_bus):
        """Test successful custom scenario creation."""
        # Act
        result = await frontend_service.create_custom_scenario(sample_scenario_create)
        
        # Assert
        assert isinstance(result, ScenarioResult)
        assert result.status == "success"
        assert result.scenario_id is not None
        assert result.result["news_items_processed"] == 1
        assert result.result["characters_involved"] == ["jovani_vazquez"]
        
        # Verify events were emitted
        assert mock_event_bus.publish_event.call_count >= 2  # scenario_started + news_injected
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_invalid(self, frontend_service, mock_event_bus):
        """Test scenario creation with invalid configuration."""
        # Arrange
        invalid_scenario = ScenarioCreate(
            name="",  # Invalid: empty name
            description="Test",
            character_ids=[],  # Invalid: no characters
            news_items=[],
            execution_speed=1.0
        )
        
        # Act
        result = await frontend_service.create_custom_scenario(invalid_scenario)
        
        # Assert
        assert result.status == "failed"
        assert "Invalid scenario configuration" in result.error
    
    @pytest.mark.asyncio
    async def test_create_custom_scenario_execution_error(self, frontend_service, sample_scenario_create, mock_event_bus):
        """Test scenario creation with execution error."""
        # Arrange
        mock_event_bus.publish_event.side_effect = Exception("Event bus error")
        
        # Act
        result = await frontend_service.create_custom_scenario(sample_scenario_create)
        
        # Assert
        assert result.status == "failed"
        assert "Event bus error" in result.error
    
    @pytest.mark.asyncio
    async def test_inject_custom_news_success(self, frontend_service, sample_custom_news, mock_event_bus):
        """Test successful custom news injection."""
        # Act
        result = await frontend_service.inject_custom_news(sample_custom_news)
        
        # Assert
        assert isinstance(result, NewsInjectionResult)
        assert result.status == "success"
        assert result.news_id is not None
        assert result.injected_at is not None
        
        # Verify event was emitted
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "custom_news_injected"
        assert event_call.data["news_id"] == result.news_id
    
    @pytest.mark.asyncio
    async def test_inject_custom_news_error(self, frontend_service, sample_custom_news, mock_event_bus):
        """Test custom news injection with error."""
        # Arrange
        mock_event_bus.publish_event.side_effect = Exception("Event bus error")
        
        # Act
        result = await frontend_service.inject_custom_news(sample_custom_news)
        
        # Assert
        assert result.status == "failed"
        assert "Event bus error" in result.error
    
    @pytest.mark.asyncio
    async def test_user_interact_with_character_success(self, frontend_service, sample_user_interaction, mock_event_bus):
        """Test successful user interaction with character."""
        # Act
        response = await frontend_service.user_interact_with_character(sample_user_interaction)
        
        # Assert
        assert isinstance(response, CharacterResponse)
        assert response.character_id == "jovani_vazquez"
        assert response.user_message == "Hello, how are you?"
        assert response.character_response is not None
        assert response.timestamp is not None
        
        # Verify event was emitted
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "user_character_interaction"
        assert event_call.data["character_id"] == "jovani_vazquez"
    
    @pytest.mark.asyncio
    async def test_user_interact_with_character_error(self, frontend_service, sample_user_interaction, mock_event_bus):
        """Test user interaction with error."""
        # Arrange
        mock_event_bus.publish_event.side_effect = Exception("Event bus error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Event bus error"):
            await frontend_service.user_interact_with_character(sample_user_interaction)
    
    @pytest.mark.asyncio
    async def test_get_active_agents(self, frontend_service, mock_agent_factory):
        """Test getting active agents."""
        # Act
        active_agents = frontend_service._get_active_agents()
        
        # Assert
        assert isinstance(active_agents, list)
        assert len(active_agents) == 2
        assert "jovani_vazquez" in active_agents
        assert "politico_boricua" in active_agents
        
        # Verify agent factory was called
        mock_agent_factory.get_available_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_scenarios(self, frontend_service, mock_demo_orchestrator):
        """Test getting active scenarios."""
        # Act
        active_scenarios = frontend_service._get_active_scenarios()
        
        # Assert
        assert isinstance(active_scenarios, list)
        assert len(active_scenarios) == 2
        assert "scenario_001" in active_scenarios
        assert "scenario_002" in active_scenarios
        
        # Verify demo orchestrator was called
        mock_demo_orchestrator.get_running_scenarios.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_scenario_valid(self, frontend_service, sample_scenario_create):
        """Test scenario validation with valid scenario."""
        # Act
        is_valid = frontend_service._validate_scenario(sample_scenario_create)
        
        # Assert
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_scenario_invalid(self, frontend_service):
        """Test scenario validation with invalid scenarios."""
        invalid_scenarios = [
            # Empty name
            ScenarioCreate(
                name="",
                description="Test",
                character_ids=["jovani_vazquez"],
                news_items=[],
                execution_speed=1.0
            ),
            # No characters
            ScenarioCreate(
                name="Test",
                description="Test",
                character_ids=[],
                news_items=[],
                execution_speed=1.0
            ),
            # Invalid speed
            ScenarioCreate(
                name="Test",
                description="Test",
                character_ids=["jovani_vazquez"],
                news_items=[],
                execution_speed=-1.0
            )
        ]
        
        for scenario in invalid_scenarios:
            is_valid = frontend_service._validate_scenario(scenario)
            assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_parse_datetime_valid(self, frontend_service):
        """Test datetime parsing with valid string."""
        # Arrange
        datetime_str = "2024-01-15T10:00:00Z"
        
        # Act
        parsed = frontend_service._parse_datetime(datetime_str)
        
        # Assert
        assert isinstance(parsed, datetime)
        assert parsed.year == 2024
        assert parsed.month == 1
        assert parsed.day == 15
    
    @pytest.mark.asyncio
    async def test_parse_datetime_invalid(self, frontend_service):
        """Test datetime parsing with invalid string."""
        # Arrange
        invalid_datetime_str = "invalid_datetime"
        
        # Act
        parsed = frontend_service._parse_datetime(invalid_datetime_str)
        
        # Assert
        assert parsed is None
    
    @pytest.mark.asyncio
    async def test_parse_datetime_none(self, frontend_service):
        """Test datetime parsing with None."""
        # Act
        parsed = frontend_service._parse_datetime(None)
        
        # Assert
        assert parsed is None
    
    @pytest.mark.asyncio
    async def test_error_handling_in_dashboard_overview(self, frontend_service, mock_n8n_webhook_service):
        """Test error handling in dashboard overview."""
        # Arrange
        mock_n8n_webhook_service.get_status.side_effect = Exception("N8N service error")
        
        # Act & Assert
        with pytest.raises(Exception, match="N8N service error"):
            await frontend_service.get_dashboard_overview()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_character_status(self, frontend_service, mock_agent_factory):
        """Test error handling in character status."""
        # Arrange
        mock_agent_factory.get_available_agents.side_effect = Exception("Agent factory error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Agent factory error"):
            await frontend_service.get_character_status()
    
    @pytest.mark.asyncio
    async def test_scenario_with_multiple_news_items(self, frontend_service, mock_event_bus):
        """Test scenario creation with multiple news items."""
        # Arrange
        scenario = ScenarioCreate(
            name="Multi News Scenario",
            description="Test scenario with multiple news items",
            character_ids=["jovani_vazquez", "politico_boricua"],
            news_items=[
                {"title": "News 1", "content": "Content 1", "source": "test", "category": "test"},
                {"title": "News 2", "content": "Content 2", "source": "test", "category": "test"},
                {"title": "News 3", "content": "Content 3", "source": "test", "category": "test"}
            ],
            execution_speed=2.0
        )
        
        # Act
        result = await frontend_service.create_custom_scenario(scenario)
        
        # Assert
        assert result.status == "success"
        assert result.result["news_items_processed"] == 3
        assert result.result["characters_involved"] == ["jovani_vazquez", "politico_boricua"]
        
        # Verify events were emitted for each news item
        assert mock_event_bus.publish_event.call_count >= 4  # scenario_started + 3 news_injected 