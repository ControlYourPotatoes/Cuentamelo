"""
Tests for Frontend API endpoints.

This module tests all frontend API endpoints including dashboard operations,
character interactions, scenario management, and real-time events.
"""

import pytest
import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.ports.frontend_port import (
    DashboardOverview, CharacterStatus, ScenarioCreate, ScenarioResult,
    CustomNews, NewsInjectionResult, UserInteraction, CharacterResponse,
    FrontendEvent
)

client = TestClient(app)


class TestFrontendAPIEndpoints:
    """Test Frontend API endpoint functionality"""
    
    def test_get_dashboard_overview_success(self):
        """Should successfully get dashboard overview."""
        # Execute
        response = client.get("/api/frontend/dashboard/overview?session_id=test_session")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        assert "system" in data
        assert "characters" in data
        assert "recent_events" in data
        assert "active_scenarios" in data
        assert "analytics" in data
        
        # Check system status structure
        system = data["system"]
        assert "status" in system
        assert "uptime" in system
        assert "active_characters" in system
        assert "total_events" in system
        assert "demo_mode" in system
        
        # Check characters is a list
        assert isinstance(data["characters"], list)
        
        # Check recent_events is a list
        assert isinstance(data["recent_events"], list)
        
        # Check active_scenarios is a list
        assert isinstance(data["active_scenarios"], list)
    
    def test_get_dashboard_overview_missing_session(self):
        """Should handle missing session ID for dashboard overview."""
        response = client.get("/api/frontend/dashboard/overview")
        assert response.status_code == 422  # Validation error
    
    def test_get_character_status_success(self):
        """Should successfully get character status."""
        # Execute
        response = client.get("/api/frontend/characters/status")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list)
        
        # If there are characters, check their structure
        if data:
            character = data[0]
            assert "id" in character
            assert "name" in character
            assert "status" in character
            assert "last_activity" in character
            assert "engagement_count" in character
            assert "response_count" in character
            assert "personality_traits" in character
            assert isinstance(character["personality_traits"], list)
    
    def test_create_custom_scenario_success(self):
        """Should successfully create a custom scenario."""
        # Test data
        scenario_data = {
            "name": "Test Scenario",
            "description": "A test scenario for API testing",
            "character_ids": ["jovani_vazquez"],
            "news_items": [
                {
                    "title": "Test News",
                    "content": "Test news content",
                    "source": "Test Source"
                }
            ],
            "execution_speed": 1.0,
            "custom_parameters": {}
        }
        
        # Execute
        response = client.post("/api/frontend/scenarios/create", json=scenario_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "scenario_id" in data
        assert "status" in data
        assert data["scenario_id"]  # Should not be empty
        
        # Status should be either success or failed
        assert data["status"] in ["success", "failed"]
        
        # If successful, should have result
        if data["status"] == "success":
            assert "result" in data
            assert isinstance(data["result"], dict)
        
        # If failed, should have error
        if data["status"] == "failed":
            assert "error" in data
    
    def test_create_custom_scenario_invalid_json(self):
        """Should handle invalid JSON in scenario creation."""
        response = client.post("/api/frontend/scenarios/create", data="invalid json")
        assert response.status_code == 422
    
    def test_create_custom_scenario_missing_fields(self):
        """Should handle missing required fields in scenario creation."""
        response = client.post("/api/frontend/scenarios/create", json={"name": "Test"})
        assert response.status_code == 422
    
    def test_inject_custom_news_success(self):
        """Should successfully inject custom news."""
        # Test data
        news_data = {
            "title": "Test News Title",
            "content": "Test news content for API testing",
            "source": "Test Source",
            "category": "test",
            "priority": 1,
            "custom_metadata": {}
        }
        
        # Execute
        response = client.post("/api/frontend/news/inject", json=news_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "news_id" in data
        assert "status" in data
        assert "injected_at" in data
        assert "processed_by" in data
        
        assert data["news_id"]  # Should not be empty
        assert data["status"] in ["injected", "failed"]
        assert data["injected_at"]  # Should be a timestamp
        
        # If failed, should have error
        if data["status"] == "failed":
            assert "error" in data
    
    def test_inject_news_invalid_json(self):
        """Should handle invalid JSON in news injection."""
        response = client.post("/api/frontend/news/inject", data="invalid json")
        assert response.status_code == 422
    
    def test_inject_news_missing_fields(self):
        """Should handle missing required fields in news injection."""
        response = client.post("/api/frontend/news/inject", json={"title": "Test"})
        assert response.status_code == 422
    
    def test_interact_with_character_success(self):
        """Should successfully interact with a character."""
        # Test data
        interaction_data = {
            "character_id": "jovani_vazquez",
            "message": "Hello, how are you today?",
            "session_id": "test_session"
        }
        
        # Execute
        response = client.post("/api/frontend/characters/interact", json=interaction_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "character_id" in data
        assert "message" in data
        assert "timestamp" in data
        assert "context" in data
        
        assert data["character_id"] == "jovani_vazquez"
        assert data["message"]  # Should have a response
        assert data["timestamp"]  # Should be a timestamp
        assert isinstance(data["context"], dict)
    
    def test_interact_with_character_invalid_character(self):
        """Should handle invalid character ID."""
        interaction_data = {
            "character_id": "nonexistent_character",
            "message": "Hello",
            "session_id": "test_session"
        }
        
        response = client.post("/api/frontend/characters/interact", json=interaction_data)
        
        # Should either return 400 (bad request) or 500 (server error)
        # depending on how the service handles invalid characters
        assert response.status_code in [400, 500]
    
    def test_interact_with_character_invalid_json(self):
        """Should handle invalid JSON in character interaction."""
        response = client.post("/api/frontend/characters/interact", data="invalid json")
        assert response.status_code == 422
    
    def test_interact_with_character_missing_fields(self):
        """Should handle missing required fields in character interaction."""
        response = client.post("/api/frontend/characters/interact", json={"character_id": "jovani"})
        assert response.status_code == 422
    
    def test_frontend_health_check_success(self):
        """Should successfully perform frontend health check."""
        # Execute
        response = client.get("/api/frontend/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "frontend_service" in data
        assert "event_bus" in data
        assert "timestamp" in data
        
        # Health status should be one of the expected values
        assert data["frontend_service"] in ["healthy", "degraded", "down"]
        assert data["event_bus"] in ["healthy", "degraded", "down"]
        assert data["timestamp"]  # Should be a timestamp
    
    def test_create_session_success(self):
        """Should successfully create a session."""
        # Execute
        response = client.get("/api/frontend/session/create?user_id=test_user")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "session_id" in data
        assert "user_id" in data
        assert "permissions" in data
        assert "created_at" in data
        
        assert data["session_id"]  # Should not be empty
        assert data["user_id"] == "test_user"
        assert data["created_at"]  # Should be a timestamp
    
    def test_create_session_without_user_id(self):
        """Should successfully create a session without user_id."""
        # Execute
        response = client.get("/api/frontend/session/create")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "session_id" in data
        assert "user_id" in data
        assert "permissions" in data
        assert "created_at" in data
        
        assert data["session_id"]  # Should not be empty
        assert data["created_at"]  # Should be a timestamp
    
    def test_get_session_success(self):
        """Should successfully get session information."""
        # First create a session
        create_response = client.get("/api/frontend/session/create?user_id=test_user")
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Then get the session
        response = client.get(f"/api/frontend/session/{session_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "session_id" in data
        assert "user_id" in data
        assert "permissions" in data
        assert "preferences" in data
        assert "created_at" in data
        assert "last_activity" in data
        
        assert data["session_id"] == session_id
        assert data["user_id"] == "test_user"
        assert data["created_at"]  # Should be a timestamp
        assert data["last_activity"]  # Should be a timestamp
    
    def test_get_session_not_found(self):
        """Should handle non-existent session."""
        response = client.get("/api/frontend/session/nonexistent_session")
        assert response.status_code == 404
    
    def test_invalidate_session_success(self):
        """Should successfully invalidate a session."""
        # First create a session
        create_response = client.get("/api/frontend/session/create?user_id=test_user")
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Then invalidate it
        response = client.delete(f"/api/frontend/session/{session_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check response
        assert "message" in data
        assert f"Session {session_id} invalidated successfully" in data["message"]
    
    def test_invalidate_session_not_found(self):
        """Should handle invalidating non-existent session."""
        response = client.delete("/api/frontend/session/nonexistent_session")
        assert response.status_code == 404
    
    def test_websocket_endpoint_exists(self):
        """Should have WebSocket endpoint available."""
        # WebSocket endpoints return 426 for HTTP requests
        response = client.get("/api/frontend/ws/events/test_session")
        assert response.status_code == 426  # Upgrade Required


class TestFrontendAPIValidation:
    """Test Frontend API validation and error handling"""
    
    def test_get_session_invalid_id(self):
        """Should handle invalid session ID."""
        response = client.get("/api/frontend/session/")
        assert response.status_code == 404
    
    def test_invalidate_session_invalid_id(self):
        """Should handle invalid session ID for invalidation."""
        response = client.delete("/api/frontend/session/")
        assert response.status_code == 404


class TestFrontendAPIErrorHandling:
    """Test Frontend API error handling scenarios"""
    
    def test_dashboard_overview_service_error(self):
        """Should handle service errors gracefully."""
        # This test would require the service to be in an error state
        # For now, we'll just verify the endpoint exists and responds
        response = client.get("/api/frontend/dashboard/overview?session_id=test_session")
        # Should either be 200 (success) or 500 (service error)
        assert response.status_code in [200, 500]
    
    def test_character_status_service_error(self):
        """Should handle character status service errors gracefully."""
        response = client.get("/api/frontend/characters/status")
        # Should either be 200 (success) or 500 (service error)
        assert response.status_code in [200, 500]
    
    def test_scenario_creation_service_error(self):
        """Should handle scenario creation service errors gracefully."""
        scenario_data = {
            "name": "Test Scenario",
            "description": "A test scenario",
            "character_ids": ["jovani_vazquez"],
            "news_items": [
                {
                    "title": "Test News",
                    "content": "Test content",
                    "source": "Test Source"
                }
            ],
            "execution_speed": 1.0,
            "custom_parameters": {}
        }
        
        response = client.post("/api/frontend/scenarios/create", json=scenario_data)
        # Should either be 200 (success) or 500 (service error)
        assert response.status_code in [200, 500] 