"""
Tests for Command API endpoints.

This module tests all command API endpoints including command submission,
status checking, cancellation, history, and WebSocket functionality.
"""

import pytest
import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient
import asyncio
from httpx import AsyncClient

from app.main import app
from app.ports.command_broker_port import CommandRequest, CommandResponse, CommandStatus, CommandType

client = TestClient(app)


class TestCommandAPIEndpoints:
    """Test Command API endpoint functionality"""
    
    def test_submit_command_success(self):
        """Should successfully submit a command."""
        # Prepare command request
        command_request = {
            "command_type": "news_injection",
            "command_id": "test_cmd_001",
            "session_id": "test_session",
            "parameters": {
                "news": {
                    "title": "Test News",
                    "content": "Test content",
                    "source": "Test Source",
                    "category": "test"
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api"
        }
        
        # Execute
        response = client.post("/api/commands/submit", json=command_request)
        if response.status_code != 200:
            print("RESPONSE:", response.status_code, response.text)
        assert response.status_code == 200
        data = response.json()
        assert data["command_id"] == "test_cmd_001"
        assert data["status"] in ["pending", "completed", "failed", "executing", "cancelled"]
    
    def test_submit_command_invalid_type(self):
        """Should handle invalid command type."""
        command_request = {
            "command_type": "INVALID_TYPE",
            "command_id": "test_cmd_002",
            "session_id": "test_session",
            "parameters": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api"
        }
        
        response = client.post("/api/commands/submit", json=command_request)
        assert response.status_code == 422
    
    def test_get_command_status_success(self):
        """Should successfully get command status."""
        # First submit a command
        command_request = {
            "command_type": "news_injection",
            "command_id": "test_cmd_status_001",
            "session_id": "test_session",
            "parameters": {
                "news": {
                    "title": "Status Test News",
                    "content": "Test content for status check",
                    "source": "Test Source",
                    "category": "test"
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api"
        }
        
        # Submit command
        submit_response = client.post("/api/commands/submit", json=command_request)
        assert submit_response.status_code == 200
        
        # Get status
        response = client.get("/api/commands/status/test_cmd_status_001")
        assert response.status_code == 200
        data = response.json()
        assert data["command_id"] == "test_cmd_status_001"
        assert "status" in data
    
    def test_get_command_status_not_found(self):
        """Should handle command not found."""
        response = client.get("/api/commands/status/nonexistent_command")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_cancel_command_success(self):
        """Should successfully cancel a command."""
        # First submit a command
        command_request = {
            "command_type": "news_injection",
            "command_id": "test_cmd_cancel_001",
            "session_id": "test_session",
            "parameters": {
                "news": {
                    "title": "Cancel Test News",
                    "content": "Test content for cancellation",
                    "source": "Test Source",
                    "category": "test"
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api"
        }
        
        # Submit command
        submit_response = client.post("/api/commands/submit", json=command_request)
        assert submit_response.status_code == 200
        
        # Cancel command
        response = client.delete("/api/commands/cancel/test_cmd_cancel_001")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    @pytest.mark.asyncio
    async def test_get_command_history_success(self):
        """Should successfully get command history."""
        # Use TestClient but with proper async handling
        with TestClient(app) as client:
            # Submit a few commands first
            for i in range(3):
                command_request = {
                    "command_type": "news_injection",
                    "command_id": f"test_cmd_history_{i:03d}",
                    "session_id": "test_session_history",
                    "parameters": {
                        "news": {
                            "title": f"History Test News {i}",
                            "content": f"Test content {i}",
                            "source": "Test Source",
                            "category": "test"
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "api"
                }
                resp = client.post("/api/commands/submit", json=command_request)
                assert resp.status_code == 200

            # Give a short delay to ensure all async tasks complete
            await asyncio.sleep(0.2)

            # Get history
            response = client.get("/api/commands/history/test_session_history")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 3
    
    def test_get_command_history_with_limit(self):
        """Should get command history with custom limit."""
        response = client.get("/api/commands/history/test_session_history?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2
    
    def test_trigger_scenario_success(self):
        """Should successfully trigger a scenario."""
        response = client.post("/api/commands/trigger-scenario?scenario_name=test_scenario&speed=1.0")
        assert response.status_code == 200
        data = response.json()
        assert "command_id" in data
        assert data["status"] in ["pending", "completed", "failed", "executing", "cancelled"]
    
    def test_inject_news_success(self):
        """Should successfully inject news."""
        response = client.post("/api/commands/inject-news?title=Test&content=Content&source=Test&category=test")
        assert response.status_code == 200
        data = response.json()
        assert "command_id" in data
        assert data["status"] in ["pending", "completed", "failed", "executing", "cancelled"]
    
    def test_chat_with_character_success(self):
        """Should successfully chat with a character."""
        response = client.post("/api/commands/chat-with-character?character_id=jovani&message=Hello")
        assert response.status_code == 200
        data = response.json()
        assert "command_id" in data
        assert data["status"] in ["pending", "completed", "failed", "executing", "cancelled"]
    
    def test_get_system_status_success(self):
        """Should successfully get system status."""
        response = client.get("/api/commands/system-status")
        assert response.status_code == 200
        data = response.json()
        assert "command_id" in data
        assert data["status"] in ["pending", "completed", "failed", "executing", "cancelled"]


class TestCommandAPIValidation:
    """Test Command API validation and error handling"""
    
    def test_submit_command_invalid_json(self):
        """Should handle invalid JSON in command submission."""
        response = client.post("/api/commands/submit", data="invalid json")
        assert response.status_code == 422
    
    def test_submit_command_missing_fields(self):
        """Should handle missing required fields in command submission."""
        response = client.post("/api/commands/submit", json={"command_type": "TEST"})
        assert response.status_code == 422
    
    def test_get_command_status_invalid_id(self):
        """Should handle invalid command ID format."""
        response = client.get("/api/commands/status/")
        assert response.status_code == 404
    
    def test_cancel_command_invalid_id(self):
        """Should handle invalid command ID for cancellation."""
        response = client.delete("/api/commands/cancel/")
        assert response.status_code == 404
    
    def test_get_command_history_invalid_session(self):
        """Should handle invalid session ID for history."""
        response = client.get("/api/commands/history/")
        assert response.status_code == 404
    
    def test_trigger_scenario_missing_name(self):
        """Should handle missing scenario name."""
        response = client.post("/api/commands/trigger-scenario")
        assert response.status_code == 422
    
    def test_inject_news_missing_required_fields(self):
        """Should handle missing required news fields."""
        response = client.post("/api/commands/inject-news?title=Test")
        assert response.status_code == 422
    
    def test_chat_with_character_missing_fields(self):
        """Should handle missing character chat fields."""
        response = client.post("/api/commands/chat-with-character?character_id=jovani")
        assert response.status_code == 422 