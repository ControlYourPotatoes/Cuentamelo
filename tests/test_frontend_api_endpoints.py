"""
Tests for Frontend API endpoints.

This module tests all frontend API endpoints including dashboard operations,
character interactions, scenario management, and real-time events.
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.ports.frontend_port import (
    DashboardOverview, CharacterStatus, ScenarioCreate, ScenarioResult,
    CustomNews, NewsInjectionResult, UserInteraction, CharacterResponse,
    FrontendEvent
)
from app.services.dependency_container import DependencyContainer

client = TestClient(app)


class TestFrontendAPIEndpoints:
    """Test Frontend API endpoint functionality"""
    
    @pytest.fixture
    def mock_frontend_service(self):
        """Mock frontend service for testing."""
        service = AsyncMock()
        service.get_dashboard_overview = AsyncMock()
        service.get_character_status = AsyncMock()
        service.create_custom_scenario = AsyncMock()
        service.inject_custom_news = AsyncMock()
        service.user_interact_with_character = AsyncMock()
        service.get_active_agents = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus for testing."""
        event_bus = AsyncMock()
        event_bus.subscribe_to_events = AsyncMock()
        return event_bus
    
    @pytest.fixture
    def mock_container(self, mock_frontend_service, mock_event_bus):
        """Mock dependency container with frontend service."""
        container = MagicMock()
        container.get_frontend_service.return_value = mock_frontend_service
        container.get_frontend_event_bus.return_value = mock_event_bus
        return container
    
    @pytest.fixture
    def sample_dashboard_overview(self):
        """Sample dashboard overview for testing."""
        return DashboardOverview(
            total_characters=3,
            active_characters=2,
            total_scenarios=5,
            active_scenarios=1,
            total_news_items=10,
            recent_activity=[
                {"type": "tweet", "character": "jovani", "content": "Test tweet"}
            ],
            system_status="healthy"
        )
    
    @pytest.fixture
    def sample_character_status(self):
        """Sample character status for testing."""
        return [
            CharacterStatus(
                id="jovani_vazquez",
                name="Jovani Vázquez",
                status="active",
                last_activity=datetime.now(timezone.utc),
                tweet_count=15,
                engagement_rate=0.85
            ),
            CharacterStatus(
                id="politico_boricua",
                name="Político Boricua",
                status="inactive",
                last_activity=datetime.now(timezone.utc),
                tweet_count=8,
                engagement_rate=0.72
            )
        ]
    
    @pytest.fixture
    def sample_scenario_create(self):
        """Sample scenario creation request for testing."""
        return {
            "name": "Test Scenario",
            "description": "A test scenario for API testing",
            "characters": ["jovani_vazquez"],
            "news_injection": {
                "title": "Test News",
                "content": "Test news content",
                "source": "Test Source"
            },
            "duration_minutes": 30,
            "speed_multiplier": 1.0
        }
    
    @pytest.fixture
    def sample_scenario_result(self):
        """Sample scenario result for testing."""
        return ScenarioResult(
            scenario_id="test_scenario_001",
            status="completed",
            execution_time=1800.5,
            character_reactions=3,
            news_items_processed=2,
            success=True,
            error_message=None
        )
    
    @pytest.fixture
    def sample_custom_news(self):
        """Sample custom news for testing."""
        return {
            "title": "Test News Title",
            "content": "Test news content for API testing",
            "source": "Test Source",
            "category": "test",
            "priority": 1
        }
    
    @pytest.fixture
    def sample_news_injection_result(self):
        """Sample news injection result for testing."""
        return NewsInjectionResult(
            success=True,
            news_id="test_news_001",
            message="News injected successfully",
            error=None
        )
    
    @pytest.fixture
    def sample_user_interaction(self):
        """Sample user interaction for testing."""
        return {
            "character_id": "jovani_vazquez",
            "message": "Hello, how are you today?",
            "session_id": "test_session"
        }
    
    @pytest.fixture
    def sample_character_response(self):
        """Sample character response for testing."""
        return CharacterResponse(
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez",
            response="¡Hola! I'm doing great today. How about you?",
            timestamp=datetime.now(timezone.utc),
            confidence=0.95
        )
    
    @patch('app.api.frontend.get_container')
    def test_get_dashboard_overview_success(self, mock_get_container, mock_container,
                                           mock_frontend_service, sample_dashboard_overview):
        """Should successfully get dashboard overview."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.get_dashboard_overview.return_value = sample_dashboard_overview
        
        # Execute
        response = client.get("/api/frontend/dashboard/overview?session_id=test_session")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_characters"] == 3
        assert data["active_characters"] == 2
        assert data["system_status"] == "healthy"
        mock_frontend_service.get_dashboard_overview.assert_called_once()
    
    @patch('app.api.frontend.get_container')
    def test_get_dashboard_overview_error(self, mock_get_container, mock_container,
                                         mock_frontend_service):
        """Should handle dashboard overview errors."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.get_dashboard_overview.side_effect = Exception("Service error")
        
        # Execute
        response = client.get("/api/frontend/dashboard/overview?session_id=test_session")
        
        # Assert
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    @patch('app.api.frontend.get_container')
    def test_get_character_status_success(self, mock_get_container, mock_container,
                                         mock_frontend_service, sample_character_status):
        """Should successfully get character status."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.get_character_status.return_value = sample_character_status
        
        # Execute
        response = client.get("/api/frontend/characters/status")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "jovani_vazquez"
        assert data[0]["status"] == "active"
        assert data[1]["id"] == "politico_boricua"
        assert data[1]["status"] == "inactive"
        mock_frontend_service.get_character_status.assert_called_once()
    
    @patch('app.api.frontend.get_container')
    def test_create_custom_scenario_success(self, mock_get_container, mock_container,
                                           mock_frontend_service, sample_scenario_create,
                                           sample_scenario_result):
        """Should successfully create a custom scenario."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.create_custom_scenario.return_value = sample_scenario_result
        
        # Execute
        response = client.post("/api/frontend/scenarios/create", json=sample_scenario_create)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "test_scenario_001"
        assert data["status"] == "completed"
        assert data["success"] is True
        mock_frontend_service.create_custom_scenario.assert_called_once()
    
    @patch('app.api.frontend.get_container')
    def test_inject_custom_news_success(self, mock_get_container, mock_container,
                                       mock_frontend_service, sample_custom_news,
                                       sample_news_injection_result):
        """Should successfully inject custom news."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.inject_custom_news.return_value = sample_news_injection_result
        
        # Execute
        response = client.post("/api/frontend/news/inject", json=sample_custom_news)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["news_id"] == "test_news_001"
        assert data["message"] == "News injected successfully"
        mock_frontend_service.inject_custom_news.assert_called_once()
    
    @patch('app.api.frontend.get_container')
    def test_interact_with_character_success(self, mock_get_container, mock_container,
                                            mock_frontend_service, sample_user_interaction,
                                            sample_character_response):
        """Should successfully interact with a character."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.user_interact_with_character.return_value = sample_character_response
        
        # Execute
        response = client.post("/api/frontend/characters/interact", json=sample_user_interaction)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "jovani_vazquez"
        assert data["character_name"] == "Jovani Vázquez"
        assert "¡Hola!" in data["response"]
        assert data["confidence"] == 0.95
        mock_frontend_service.user_interact_with_character.assert_called_once()
    
    @patch('app.api.frontend.get_container')
    def test_interact_with_character_invalid_input(self, mock_get_container, mock_container,
                                                  mock_frontend_service):
        """Should handle invalid character interaction input."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.user_interact_with_character.side_effect = ValueError("Invalid character")
        
        # Execute
        response = client.post("/api/frontend/characters/interact", 
                              json={"character_id": "invalid", "message": "Hello"})
        
        # Assert
        assert response.status_code == 400
        assert "Invalid character" in response.json()["detail"]
    
    @patch('app.api.frontend.get_container')
    def test_interact_with_character_service_error(self, mock_get_container, mock_container,
                                                  mock_frontend_service, sample_user_interaction):
        """Should handle character interaction service errors."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.user_interact_with_character.side_effect = Exception("Service error")
        
        # Execute
        response = client.post("/api/frontend/characters/interact", json=sample_user_interaction)
        
        # Assert
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    @patch('app.api.frontend.get_container')
    def test_frontend_health_check_success(self, mock_get_container, mock_container,
                                          mock_frontend_service):
        """Should successfully perform frontend health check."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_frontend_service.get_dashboard_overview.return_value = MagicMock()
        mock_frontend_service.get_character_status.return_value = []
        
        # Execute
        response = client.get("/api/frontend/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "frontend_service" in data["services"]
        assert "event_bus" in data["services"]
    
    @patch('app.api.frontend.get_container')
    def test_create_session_success(self, mock_get_container, mock_container):
        """Should successfully create a session."""
        # Setup
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/frontend/session/create?user_id=test_user")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["user_id"] == "test_user"
        assert data["status"] == "created"
    
    @patch('app.api.frontend.get_container')
    def test_get_session_success(self, mock_get_container, mock_container):
        """Should successfully get session information."""
        # Setup
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/frontend/session/test_session")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert "created_at" in data
        assert "last_activity" in data
    
    @patch('app.api.frontend.get_container')
    def test_invalidate_session_success(self, mock_get_container, mock_container):
        """Should successfully invalidate a session."""
        # Setup
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.delete("/api/frontend/session/test_session")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert data["status"] == "invalidated"


class TestFrontendAPIValidation:
    """Test Frontend API validation and error handling"""
    
    def test_get_dashboard_overview_missing_session(self):
        """Should handle missing session ID for dashboard overview."""
        response = client.get("/api/frontend/dashboard/overview")
        assert response.status_code == 422
    
    def test_create_scenario_invalid_json(self):
        """Should handle invalid JSON in scenario creation."""
        response = client.post("/api/frontend/scenarios/create", data="invalid json")
        assert response.status_code == 422
    
    def test_create_scenario_missing_fields(self):
        """Should handle missing required fields in scenario creation."""
        response = client.post("/api/frontend/scenarios/create", json={"name": "Test"})
        assert response.status_code == 422
    
    def test_inject_news_invalid_json(self):
        """Should handle invalid JSON in news injection."""
        response = client.post("/api/frontend/news/inject", data="invalid json")
        assert response.status_code == 422
    
    def test_inject_news_missing_fields(self):
        """Should handle missing required fields in news injection."""
        response = client.post("/api/frontend/news/inject", json={"title": "Test"})
        assert response.status_code == 422
    
    def test_interact_with_character_invalid_json(self):
        """Should handle invalid JSON in character interaction."""
        response = client.post("/api/frontend/characters/interact", data="invalid json")
        assert response.status_code == 422
    
    def test_interact_with_character_missing_fields(self):
        """Should handle missing required fields in character interaction."""
        response = client.post("/api/frontend/characters/interact", json={"character_id": "jovani"})
        assert response.status_code == 422
    
    def test_get_session_invalid_id(self):
        """Should handle invalid session ID."""
        response = client.get("/api/frontend/session/")
        assert response.status_code == 404
    
    def test_invalidate_session_invalid_id(self):
        """Should handle invalid session ID for invalidation."""
        response = client.delete("/api/frontend/session/")
        assert response.status_code == 404


class TestFrontendAPIWebSocket:
    """Test Frontend API WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection_acceptance(self):
        """Should accept WebSocket connections."""
        # This would require a more complex WebSocket test setup
        # For now, we'll test the endpoint exists
        response = client.get("/api/frontend/ws/events/test_session")
        # WebSocket endpoints return 426 for HTTP requests
        assert response.status_code == 426
    
    @pytest.mark.asyncio
    async def test_websocket_events_subscription(self):
        """Should handle WebSocket event subscription."""
        # This would require testing with a WebSocket client
        # For now, we'll verify the endpoint structure
        pass 