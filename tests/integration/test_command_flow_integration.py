"""
Integration Tests for Command Flow.

This module tests the complete command flow from submission through execution
to status tracking, ensuring all components work together properly.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.dependency_container import DependencyContainer
from app.services.command_broker_service import CommandBrokerService
from app.services.command_handler import CommandHandler
from app.services.redis_client import RedisClient
from app.services.frontend_event_bus import FrontendEventBus
from app.ports.command_broker_port import (
    CommandRequest, CommandResponse, CommandStatus, CommandType
)
from app.ports.frontend_port import FrontendEvent, EventBus


class TestCommandFlowIntegration:
    """Integration test suite for command flow."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for integration testing."""
        redis = AsyncMock(spec=RedisClient)
        redis.set = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        redis.publish = AsyncMock()
        return redis
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus for integration testing."""
        event_bus = AsyncMock(spec=EventBus)
        event_bus.publish_event = AsyncMock()
        return event_bus
    
    @pytest.fixture
    def mock_command_handler(self):
        """Mock command handler for integration testing."""
        handler = AsyncMock(spec=CommandHandler)
        handler.execute_command.return_value = CommandResponse(
            command_id="test_cmd_001",
            status=CommandStatus.COMPLETED,
            result={"message": "Command executed successfully"},
            timestamp=datetime.now(timezone.utc),
            execution_time=0.5
        )
        return handler
    
    @pytest.fixture
    def command_broker(self, mock_command_handler, mock_redis_client, mock_event_bus):
        """Command broker with mocked dependencies for integration testing."""
        return CommandBrokerService(
            command_handler=mock_command_handler,
            redis_client=mock_redis_client,
            event_bus=mock_event_bus
        )
    
    @pytest.fixture
    def sample_command_request(self):
        """Sample command request for integration testing."""
        return CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id="integration_test_cmd_001",
            session_id="integration_test_session_001",
            parameters={"test": "integration"},
            timestamp=datetime.now(timezone.utc),
            source="integration_test"
        )
    
    @pytest.mark.asyncio
    async def test_complete_command_flow(self, command_broker, sample_command_request, mock_redis_client, mock_event_bus, mock_command_handler):
        """Test complete command flow from submission to completion."""
        # Step 1: Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        assert response.command_id == "integration_test_cmd_001"
        assert response.result["message"] == "Command executed successfully"
        
        # Verify Redis storage
        assert mock_redis_client.set.call_count == 2  # command + response
        
        # Verify event emission
        assert mock_event_bus.publish_event.call_count == 2  # submitted + completed
        
        # Verify command handler was called
        mock_command_handler.execute_command.assert_called_once_with(sample_command_request)
        
        # Step 2: Check command status
        status_response = await command_broker.get_command_status(sample_command_request.command_id)
        assert status_response.status == CommandStatus.COMPLETED
        
        # Step 3: Verify command is not in active commands
        active_commands = await command_broker.get_active_commands()
        assert sample_command_request.command_id not in [cmd.command_id for cmd in active_commands]
    
    @pytest.mark.asyncio
    async def test_command_flow_with_different_types(self, command_broker, mock_redis_client, mock_event_bus):
        """Test command flow with different command types."""
        command_types = [
            CommandType.SYSTEM_STATUS,
            CommandType.NEWS_INJECTION,
            CommandType.SCENARIO_TRIGGER,
            CommandType.CHARACTER_CHAT
        ]
        
        for cmd_type in command_types:
            # Create command request
            command_request = CommandRequest(
                command_type=cmd_type,
                command_id=f"integration_test_{cmd_type.value}",
                session_id="integration_test_session",
                parameters={"test_type": cmd_type.value},
                timestamp=datetime.now(timezone.utc),
                source="integration_test"
            )
            
            # Submit command
            response = await command_broker.submit_command(command_request)
            
            # Verify response
            assert response.status == CommandStatus.COMPLETED
            assert response.command_id == f"integration_test_{cmd_type.value}"
            
            # Verify events were emitted
            assert mock_event_bus.publish_event.call_count >= 2
        
        # Verify total events emitted
        assert mock_event_bus.publish_event.call_count >= len(command_types) * 2
    
    @pytest.mark.asyncio
    async def test_command_flow_with_parameters(self, command_broker, mock_redis_client, mock_event_bus):
        """Test command flow with complex parameters."""
        # Create command with complex parameters
        complex_command = CommandRequest(
            command_type=CommandType.NEWS_INJECTION,
            command_id="complex_params_cmd",
            session_id="complex_session",
            parameters={
                "news": {
                    "title": "Complex Test News",
                    "content": "This is a test news item with complex parameters",
                    "source": "integration_test",
                    "category": "test",
                    "priority": 1,
                    "tags": ["test", "integration", "complex"]
                },
                "metadata": {
                    "test_mode": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            },
            timestamp=datetime.now(timezone.utc),
            source="integration_test"
        )
        
        # Submit command
        response = await command_broker.submit_command(complex_command)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        
        # Verify parameters were stored correctly
        stored_command_call = mock_redis_client.set.call_args_list[0]
        stored_command_json = stored_command_call[0][1]
        
        import json
        stored_command_data = json.loads(stored_command_json)
        assert stored_command_data["parameters"]["news"]["title"] == "Complex Test News"
        assert stored_command_data["parameters"]["news"]["tags"] == ["test", "integration", "complex"]
        assert stored_command_data["parameters"]["metadata"]["test_mode"] is True
    
    @pytest.mark.asyncio
    async def test_command_flow_error_handling(self, command_broker, sample_command_request, mock_command_handler):
        """Test command flow error handling."""
        # Arrange: Make command handler throw an exception
        mock_command_handler.execute_command.side_effect = Exception("Command execution failed")
        
        # Act & Assert: Command should fail
        with pytest.raises(Exception, match="Command execution failed"):
            await command_broker.submit_command(sample_command_request)
    
    @pytest.mark.asyncio
    async def test_command_flow_with_cancellation(self, command_broker, sample_command_request, mock_event_bus):
        """Test command flow with cancellation."""
        # Arrange: Add command to active commands
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act: Cancel command
        result = await command_broker.cancel_command(sample_command_request.command_id)
        
        # Assert
        assert result is True
        assert sample_command_request.command_id not in command_broker.active_commands
        
        # Verify cancellation event was emitted
        mock_event_bus.publish_event.assert_called_once()
        event_call = mock_event_bus.publish_event.call_args[0][0]
        assert event_call.event_type == "command_cancelled"
        assert event_call.data["command_id"] == sample_command_request.command_id
    
    @pytest.mark.asyncio
    async def test_command_flow_with_dependency_container(self, mock_redis_client, mock_event_bus):
        """Test command flow using dependency container."""
        # Arrange: Create container with mock configuration
        container = DependencyContainer({
            "ai_provider": "mock",
            "news_provider": "mock",
            "twitter_provider": "mock",
            "orchestration": "mock"
        })
        
        # Get command broker from container
        command_broker = container.get_command_broker()
        
        # Create command request
        command_request = CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id="container_test_cmd",
            session_id="container_test_session",
            parameters={},
            timestamp=datetime.now(timezone.utc),
            source="container_test"
        )
        
        # Act: Submit command
        response = await command_broker.submit_command(command_request)
        
        # Assert
        assert response.status == CommandStatus.COMPLETED
        assert response.command_id == "container_test_cmd"
    
    @pytest.mark.asyncio
    async def test_command_flow_with_event_bus_integration(self, command_broker, sample_command_request, mock_event_bus):
        """Test command flow with event bus integration."""
        # Act: Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Assert: Verify events were emitted
        assert mock_event_bus.publish_event.call_count == 2
        
        # Verify submitted event
        submitted_event = mock_event_bus.publish_event.call_args_list[0][0][0]
        assert submitted_event.event_type == "command_submitted"
        assert submitted_event.data["command_id"] == sample_command_request.command_id
        assert submitted_event.data["command_type"] == CommandType.SYSTEM_STATUS.value
        assert submitted_event.data["source"] == "integration_test"
        assert submitted_event.session_id == "integration_test_session_001"
        
        # Verify completed event
        completed_event = mock_event_bus.publish_event.call_args_list[1][0][0]
        assert completed_event.event_type == "command_completed"
        assert completed_event.data["command_id"] == sample_command_request.command_id
        assert completed_event.data["status"] == CommandStatus.COMPLETED.value
        assert "execution_time" in completed_event.data
    
    @pytest.mark.asyncio
    async def test_command_flow_with_redis_integration(self, command_broker, sample_command_request, mock_redis_client):
        """Test command flow with Redis integration."""
        # Act: Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Assert: Verify Redis operations
        assert mock_redis_client.set.call_count == 2
        
        # Verify command storage
        command_storage_call = mock_redis_client.set.call_args_list[0]
        assert command_storage_call[0][0] == f"command:{sample_command_request.command_id}"
        assert command_storage_call[0][2] == 3600  # 1 hour expiration
        
        # Verify response storage
        response_storage_call = mock_redis_client.set.call_args_list[1]
        assert response_storage_call[0][0] == f"command_response:{sample_command_request.command_id}"
        assert response_storage_call[0][2] == 3600  # 1 hour expiration
    
    @pytest.mark.asyncio
    async def test_command_flow_concurrent_execution(self, command_broker, mock_redis_client, mock_event_bus):
        """Test command flow with concurrent command execution."""
        # Create multiple commands
        commands = [
            CommandRequest(
                command_type=CommandType.SYSTEM_STATUS,
                command_id=f"concurrent_cmd_{i}",
                session_id="concurrent_session",
                parameters={"index": i},
                timestamp=datetime.now(timezone.utc),
                source="concurrent_test"
            )
            for i in range(5)
        ]
        
        # Act: Submit all commands concurrently
        responses = await asyncio.gather(*[
            command_broker.submit_command(cmd) for cmd in commands
        ])
        
        # Assert: All commands should complete successfully
        for i, response in enumerate(responses):
            assert response.status == CommandStatus.COMPLETED
            assert response.command_id == f"concurrent_cmd_{i}"
        
        # Verify total events and Redis operations
        assert mock_event_bus.publish_event.call_count == 10  # 5 commands * 2 events each
        assert mock_redis_client.set.call_count == 10  # 5 commands * 2 storage operations each
    
    @pytest.mark.asyncio
    async def test_command_flow_status_tracking(self, command_broker, sample_command_request, mock_redis_client):
        """Test command flow status tracking."""
        # Arrange: Store a completed response in Redis
        completed_response = CommandResponse(
            command_id=sample_command_request.command_id,
            status=CommandStatus.COMPLETED,
            result={"test": "completed"},
            timestamp=datetime.now(timezone.utc),
            execution_time=1.0
        )
        mock_redis_client.get.return_value = completed_response.json()
        
        # Act: Get command status
        status_response = await command_broker.get_command_status(sample_command_request.command_id)
        
        # Assert
        assert status_response.status == CommandStatus.COMPLETED
        assert status_response.result["test"] == "completed"
        assert status_response.execution_time == 1.0
        
        # Verify Redis was queried
        mock_redis_client.get.assert_called_with(f"command_response:{sample_command_request.command_id}")
    
    @pytest.mark.asyncio
    async def test_command_flow_with_session_management(self, command_broker, mock_redis_client):
        """Test command flow with session management."""
        # Create commands for different sessions
        session1_commands = [
            CommandRequest(
                command_type=CommandType.SYSTEM_STATUS,
                command_id=f"session1_cmd_{i}",
                session_id="session_001",
                parameters={"session": "session1", "index": i},
                timestamp=datetime.now(timezone.utc),
                source="session_test"
            )
            for i in range(3)
        ]
        
        session2_commands = [
            CommandRequest(
                command_type=CommandType.NEWS_INJECTION,
                command_id=f"session2_cmd_{i}",
                session_id="session_002",
                parameters={"session": "session2", "index": i},
                timestamp=datetime.now(timezone.utc),
                source="session_test"
            )
            for i in range(2)
        ]
        
        # Submit all commands
        all_commands = session1_commands + session2_commands
        responses = await asyncio.gather(*[
            command_broker.submit_command(cmd) for cmd in all_commands
        ])
        
        # Assert: All commands should complete successfully
        for response in responses:
            assert response.status == CommandStatus.COMPLETED
        
        # Verify session-specific data in stored commands
        for cmd in all_commands:
            # Find the storage call for this command
            for call in mock_redis_client.set.call_args_list:
                if cmd.command_id in call[0][1]:
                    stored_data = call[0][1]
                    assert cmd.session_id in stored_data
                    assert cmd.parameters["session"] in stored_data
                    break 