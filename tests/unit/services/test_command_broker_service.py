"""
Comprehensive tests for CommandBrokerService.

This test suite follows the testing framework revamp plan principles:
- Uses pytest fixtures and dependency injection
- Tests both success and error cases
- Validates event emissions and Redis interactions
- Includes integration tests for complete command flow
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.services.command_broker_service import CommandBrokerService
from app.ports.command_broker_port import CommandRequest, CommandResponse, CommandStatus, CommandType
from app.ports.frontend_port import FrontendEvent, EventBus
from app.services.redis_client import RedisClient
from app.services.command_handler import CommandHandler


class TestCommandBrokerService:
    """Test suite for CommandBrokerService."""
    
    @pytest.fixture
    def mock_command_handler(self):
        """Mock command handler for testing."""
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
        """Mock Redis client for testing."""
        redis = AsyncMock(spec=RedisClient)
        redis.set = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        return redis
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus for testing."""
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
            command_id="test_cmd_001",
            command_type=CommandType.SCENARIO_TRIGGER,
            parameters={"scenario_name": "test_scenario", "character_id": "jovani_vazquez"},
            source="test",
            session_id="test_session_001",
            timestamp=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_command_response(self):
        """Sample command response for testing."""
        return CommandResponse(
            command_id="test_cmd_001",
            status=CommandStatus.COMPLETED,
            result={"message": "Test command executed successfully"},
            timestamp=datetime.now(timezone.utc),
            execution_time=0.5
        )

    @pytest.mark.asyncio
    async def test_submit_command_success(self, command_broker, sample_command_request, mock_redis_client, mock_event_bus):
        """Test successful command submission."""
        # Act
        response = await command_broker.submit_command(sample_command_request)
        
        # Assert
        assert response.command_id == sample_command_request.command_id
        assert response.status == CommandStatus.COMPLETED
        
        # Verify Redis interactions
        mock_redis_client.set.assert_called()
        assert mock_redis_client.set.call_count == 2  # Command and response storage
        
        # Verify event emissions
        assert mock_event_bus.publish_event.call_count == 2  # Submitted and completed events
        
        # Verify command handler was called
        command_broker.command_handler.execute_command.assert_called_once_with(sample_command_request)
    
    @pytest.mark.asyncio
    async def test_submit_command_redis_error(self, mock_command_handler, mock_redis_client, mock_event_bus, sample_command_request):
        """Test command submission with Redis error."""
        # Arrange
        mock_redis_client.set.side_effect = Exception("Redis connection error")
        command_broker = CommandBrokerService(
            command_handler=mock_command_handler,
            redis_client=mock_redis_client,
            event_bus=mock_event_bus
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="Redis connection error"):
            await command_broker.submit_command(sample_command_request)
    
    @pytest.mark.asyncio
    async def test_submit_command_handler_error(self, mock_command_handler, mock_redis_client, mock_event_bus, sample_command_request):
        """Test command submission with handler error."""
        # Arrange
        mock_command_handler.execute_command.side_effect = Exception("Handler execution error")
        command_broker = CommandBrokerService(
            command_handler=mock_command_handler,
            redis_client=mock_redis_client,
            event_bus=mock_event_bus
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="Handler execution error"):
            await command_broker.submit_command(sample_command_request)
    
    @pytest.mark.asyncio
    async def test_get_command_status_active(self, command_broker, sample_command_request):
        """Test getting status of active command."""
        # Arrange
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act
        response = await command_broker.get_command_status(sample_command_request.command_id)
        
        # Assert
        assert response.command_id == sample_command_request.command_id
        assert response.status == CommandStatus.EXECUTING
        assert response.metadata["active"] is True
    
    @pytest.mark.asyncio
    async def test_get_command_status_completed(self, command_broker, sample_command_response, mock_redis_client):
        """Test getting status of completed command."""
        # Arrange
        mock_redis_client.get.return_value = sample_command_response.json()
        
        # Act
        response = await command_broker.get_command_status("test_cmd_001")
        
        # Assert
        assert response.command_id == "test_cmd_001"
        assert response.status == CommandStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_get_command_status_pending(self, command_broker, sample_command_request, mock_redis_client):
        """Test getting status of pending command."""
        # Arrange
        mock_redis_client.get.side_effect = [None, sample_command_request.json()]  # No response, but command exists
        
        # Act
        response = await command_broker.get_command_status("test_cmd_001")
        
        # Assert
        assert response.command_id == "test_cmd_001"
        assert response.status == CommandStatus.PENDING
        assert response.metadata["command_found"] is True
    
    @pytest.mark.asyncio
    async def test_get_command_status_not_found(self, command_broker, mock_redis_client):
        """Test getting status of non-existent command."""
        # Arrange
        mock_redis_client.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Command test_cmd_001 not found"):
            await command_broker.get_command_status("test_cmd_001")
    
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
    
    @pytest.mark.asyncio
    async def test_cancel_command_not_found(self, command_broker, mock_event_bus):
        """Test cancelling non-existent command."""
        # Act
        result = await command_broker.cancel_command("non_existent_cmd")
        
        # Assert
        assert result is False
        mock_event_bus.publish_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_command_history(self, command_broker):
        """Test getting command history."""
        # Act
        history = await command_broker.get_command_history("test_session_001", limit=10)
        
        # Assert
        assert isinstance(history, list)
        # Note: Current implementation returns empty list as placeholder
    
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
        assert True
    
    @pytest.mark.asyncio
    async def test_event_emission_on_command_submission(self, command_broker, sample_command_request, mock_event_bus):
        """Test that events are properly emitted during command submission."""
        # Act
        await command_broker.submit_command(sample_command_request)
        
        # Assert
        assert mock_event_bus.publish_event.call_count == 2
        
        # Check submitted event
        submitted_event = mock_event_bus.publish_event.call_args_list[0][0][0]
        assert submitted_event.event_type == "command_submitted"
        assert submitted_event.data["command_id"] == sample_command_request.command_id
        assert submitted_event.data["command_type"] == sample_command_request.command_type.value
        
        # Check completed event
        completed_event = mock_event_bus.publish_event.call_args_list[1][0][0]
        assert completed_event.event_type == "command_completed"
        assert completed_event.data["command_id"] == sample_command_request.command_id


class TestCommandBrokerIntegration:
    """Integration tests for CommandBrokerService."""
    
    @pytest.fixture
    def integration_command_broker(self):
        """Command broker with real dependencies for integration testing."""
        # This would use real Redis and event bus in integration tests
        # For now, we'll use mocks but test the complete flow
        mock_command_handler = AsyncMock()
        mock_redis_client = AsyncMock()
        mock_event_bus = AsyncMock()
        
        return CommandBrokerService(
            command_handler=mock_command_handler,
            redis_client=mock_redis_client,
            event_bus=mock_event_bus
        )
    
    @pytest.mark.asyncio
    async def test_complete_command_flow(self, integration_command_broker):
        """Test complete command flow from submission to completion."""
        # Arrange
        command_request = CommandRequest(
            command_id="integration_test_001",
            command_type=CommandType.SCENARIO_TRIGGER,
            parameters={"scenario_name": "integration_test_scenario", "character_id": "jovani_vazquez"},
            source="integration_test",
            session_id="integration_session_001",
            timestamp=datetime.now(timezone.utc)
        )
        
        expected_response = CommandResponse(
            command_id="integration_test_001",
            status=CommandStatus.COMPLETED,
            result={"orchestration_result": "success"},
            timestamp=datetime.now(timezone.utc),
            execution_time=1.2
        )
        
        integration_command_broker.command_handler.execute_command.return_value = expected_response
        
        # Act
        response = await integration_command_broker.submit_command(command_request)
        
        # Assert
        assert response.command_id == "integration_test_001"
        assert response.status == CommandStatus.COMPLETED
        
        # Verify Redis storage
        integration_command_broker.redis_client.set.assert_called()
        
        # Verify event emissions
        assert integration_command_broker.event_bus.publish_event.call_count == 2
        
        # Verify command is not in active commands after completion
        assert command_request.command_id not in integration_command_broker.active_commands
    
    @pytest.mark.asyncio
    async def test_command_status_tracking(self, integration_command_broker):
        """Test command status tracking throughout execution."""
        # Arrange
        command_id = "status_tracking_test_001"
        command_request = CommandRequest(
            command_id=command_id,
            command_type=CommandType.SCENARIO_TRIGGER,
            parameters={"scenario_name": "status_tracking_scenario"},
            source="test",
            session_id="test_session",
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add to active commands to simulate execution
        integration_command_broker.active_commands[command_id] = command_request
        
        # Act - Check status during execution
        status_during_execution = await integration_command_broker.get_command_status(command_id)
        
        # Assert
        assert status_during_execution.status == CommandStatus.EXECUTING
        assert status_during_execution.metadata["active"] is True
        
        # Simulate completion
        del integration_command_broker.active_commands[command_id]
        integration_command_broker.redis_client.get.return_value = CommandResponse(
            command_id=command_id,
            status=CommandStatus.COMPLETED,
            execution_time=1.5,
            timestamp=datetime.now(timezone.utc)
        ).json()
        
        # Act - Check status after completion
        status_after_completion = await integration_command_broker.get_command_status(command_id)
        
        # Assert
        assert status_after_completion.status == CommandStatus.COMPLETED 