"""
Tests for Command Broker Service.

This module tests the command broker service which handles central command processing,
routing, persistence, and event emission for all system interfaces.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.command_broker_service import CommandBrokerService
from app.services.command_handler import CommandHandler
from app.services.redis_client import RedisClient
from app.ports.command_broker_port import (
    CommandRequest, CommandResponse, CommandStatus, CommandType
)
from app.ports.frontend_port import FrontendEvent, EventBus


class TestCommandBrokerService:
    """Test suite for CommandBrokerService."""
    
    @pytest.fixture
    def mock_command_handler(self):
        """Mock command handler."""
        handler = AsyncMock(spec=CommandHandler)
        handler.execute_command.return_value = CommandResponse(
            command_id="test_cmd_001",
            status=CommandStatus.COMPLETED,
            result={"message": "Test command executed successfully"},
            timestamp=datetime.now(timezone.utc),
            execution_time=0.5
        )
        return handler
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        redis = AsyncMock(spec=RedisClient)
        redis.set = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        return redis
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus."""
        event_bus = AsyncMock(spec=EventBus)
        event_bus.publish_event = AsyncMock()
        return event_bus
    
    @pytest.fixture
    def command_broker(self, mock_command_handler, mock_redis_client, mock_event_bus):
        """Command broker service with mocked dependencies."""
        return CommandBrokerService(
            command_handler=mock_command_handler,
            redis_client=mock_redis_client,
            event_bus=mock_event_bus
        )
    
    @pytest.fixture
    def sample_command_request(self):
        """Sample command request for testing."""
        return CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id="test_cmd_001",
            session_id="test_session_001",
            parameters={},
            timestamp=datetime.now(timezone.utc),
            source="test"
        )
    
    @pytest.mark.asyncio
    async def test_submit_command_success(self, command_broker, sample_command_request, mock_redis_client, mock_event_bus):
        """Test successful command submission."""
        # Act
        response = await command_broker.submit_command(sample_command_request)
        
        # Assert
        assert response.status == CommandStatus.COMPLETED
        assert response.command_id == "test_cmd_001"
        assert response.result["message"] == "Test command executed successfully"
        
        # Verify Redis storage
        mock_redis_client.set.assert_called()
        
        # Verify event emission
        assert mock_event_bus.publish_event.call_count == 2  # submitted + completed
        
        # Verify command removed from active commands
        assert sample_command_request.command_id not in command_broker.active_commands
    
    @pytest.mark.asyncio
    async def test_submit_command_storage(self, command_broker, sample_command_request, mock_redis_client):
        """Test that commands are properly stored in Redis."""
        # Act
        await command_broker.submit_command(sample_command_request)
        
        # Assert
        # Verify command storage
        mock_redis_client.set.assert_any_call(
            f"command:{sample_command_request.command_id}",
            sample_command_request.json(),
            expire=3600
        )
        
        # Verify response storage
        mock_redis_client.set.assert_any_call(
            f"command_response:{sample_command_request.command_id}",
            pytest.approx(any(str)),  # Response JSON
            expire=3600
        )
    
    @pytest.mark.asyncio
    async def test_get_command_status_active(self, command_broker, sample_command_request):
        """Test getting status of active command."""
        # Arrange
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act
        response = await command_broker.get_command_status(sample_command_request.command_id)
        
        # Assert
        assert response.status == CommandStatus.EXECUTING
        assert response.metadata["active"] is True
    
    @pytest.mark.asyncio
    async def test_get_command_status_completed(self, command_broker, sample_command_request, mock_redis_client):
        """Test getting status of completed command."""
        # Arrange
        completed_response = CommandResponse(
            command_id=sample_command_request.command_id,
            status=CommandStatus.COMPLETED,
            result={"test": "data"},
            timestamp=datetime.now(timezone.utc),
            execution_time=1.0
        )
        mock_redis_client.get.return_value = completed_response.json()
        
        # Act
        response = await command_broker.get_command_status(sample_command_request.command_id)
        
        # Assert
        assert response.status == CommandStatus.COMPLETED
        assert response.result["test"] == "data"
    
    @pytest.mark.asyncio
    async def test_get_command_status_pending(self, command_broker, sample_command_request, mock_redis_client):
        """Test getting status of pending command."""
        # Arrange
        mock_redis_client.get.side_effect = [None, sample_command_request.json()]
        
        # Act
        response = await command_broker.get_command_status(sample_command_request.command_id)
        
        # Assert
        assert response.status == CommandStatus.PENDING
        assert response.metadata["command_found"] is True
    
    @pytest.mark.asyncio
    async def test_get_command_status_not_found(self, command_broker, mock_redis_client):
        """Test getting status of non-existent command."""
        # Arrange
        mock_redis_client.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Command nonexistent_cmd not found"):
            await command_broker.get_command_status("nonexistent_cmd")
    
    @pytest.mark.asyncio
    async def test_cancel_command_success(self, command_broker, sample_command_request, mock_event_bus):
        """Test successful command cancellation."""
        # Arrange
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act
        result = await command_broker.cancel_command(sample_command_request.command_id)
        
        # Assert
        assert result is True
        assert sample_command_request.command_id not in command_broker.active_commands
        
        # Verify event emission
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "command_cancelled"
        assert event_call.data["command_id"] == sample_command_request.command_id
    
    @pytest.mark.asyncio
    async def test_cancel_command_not_found(self, command_broker):
        """Test cancelling non-existent command."""
        # Act
        result = await command_broker.cancel_command("nonexistent_cmd")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_command_history(self, command_broker):
        """Test getting command history."""
        # Act
        history = await command_broker.get_command_history("test_session", limit=10)
        
        # Assert
        assert isinstance(history, list)
        # Note: Currently returns empty list as placeholder implementation
    
    @pytest.mark.asyncio
    async def test_get_active_commands(self, command_broker, sample_command_request):
        """Test getting active commands."""
        # Arrange
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act
        active_commands = await command_broker.get_active_commands()
        
        # Assert
        assert len(active_commands) == 1
        assert active_commands[0].command_id == sample_command_request.command_id
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_commands(self, command_broker, sample_command_request):
        """Test cleanup of expired commands."""
        # Arrange
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act
        await command_broker.cleanup_expired_commands()
        
        # Assert
        # Currently just logs, so we verify no exceptions are raised
        assert sample_command_request.command_id in command_broker.active_commands
    
    @pytest.mark.asyncio
    async def test_command_execution_error_handling(self, command_broker, sample_command_request, mock_command_handler):
        """Test error handling during command execution."""
        # Arrange
        mock_command_handler.execute_command.side_effect = Exception("Command execution failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Command execution failed"):
            await command_broker.submit_command(sample_command_request)
    
    @pytest.mark.asyncio
    async def test_different_command_types(self, command_broker, mock_redis_client, mock_event_bus):
        """Test different command types."""
        command_types = [
            CommandType.SYSTEM_STATUS,
            CommandType.NEWS_INJECTION,
            CommandType.SCENARIO_TRIGGER,
            CommandType.CHARACTER_CHAT
        ]
        
        for cmd_type in command_types:
            # Arrange
            command_request = CommandRequest(
                command_type=cmd_type,
                command_id=f"test_{cmd_type.value}",
                session_id="test_session",
                parameters={"test": "data"},
                timestamp=datetime.now(timezone.utc),
                source="test"
            )
            
            # Act
            response = await command_broker.submit_command(command_request)
            
            # Assert
            assert response.status == CommandStatus.COMPLETED
            assert response.command_id == f"test_{cmd_type.value}"
            
            # Verify events were emitted
            assert mock_event_bus.publish_event.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_command_with_parameters(self, command_broker, mock_redis_client):
        """Test command with parameters."""
        # Arrange
        command_request = CommandRequest(
            command_type=CommandType.NEWS_INJECTION,
            command_id="test_with_params",
            session_id="test_session",
            parameters={
                "title": "Test News",
                "content": "Test content",
                "source": "test"
            },
            timestamp=datetime.now(timezone.utc),
            source="test"
        )
        
        # Act
        response = await command_broker.submit_command(command_request)
        
        # Assert
        assert response.status == CommandStatus.COMPLETED
        
        # Verify command was stored with parameters
        stored_command_call = mock_redis_client.set.call_args_list[0]
        assert "test_with_params" in stored_command_call[0][0]
        assert "Test News" in stored_command_call[0][1] 