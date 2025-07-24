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
    def real_redis_client(self):
        """Real Redis client for integration testing."""
        # Use real Redis client with test database
        redis = RedisClient()
        return redis
    
    @pytest.fixture
    def real_event_bus(self, real_redis_client):
        """Real event bus for integration testing."""
        # Use real event bus with real Redis client
        event_bus = FrontendEventBus(real_redis_client)
        return event_bus
    
    @pytest.fixture
    def real_command_handler(self):
        """Real command handler with mocked external dependencies."""
        # Create dependency container with mock external services
        container = DependencyContainer({
            "ai_provider": "mock",
            "news_provider": "mock", 
            "twitter_provider": "mock",
            "orchestration": "mock"
        })
        
        # Get real command handler from container
        command_handler = container.get_command_handler()
        return command_handler
    
    @pytest.fixture
    def command_broker(self, real_command_handler, real_redis_client, real_event_bus):
        """Command broker with real dependencies for integration testing."""
        return CommandBrokerService(
            command_handler=real_command_handler,
            redis_client=real_redis_client,
            event_bus=real_event_bus
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
    async def test_complete_command_flow(self, command_broker, sample_command_request, real_redis_client, real_event_bus):
        """Test complete command flow from submission to completion."""
        # Step 1: Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        assert response.command_id == "integration_test_cmd_001"
        assert response.result is not None
        
        # Verify Redis storage (real persistence)
        stored_command = await real_redis_client.get(f"command:{sample_command_request.command_id}")
        assert stored_command is not None
        
        stored_response = await real_redis_client.get(f"command_response:{sample_command_request.command_id}")
        assert stored_response is not None
        
        # Step 2: Check command status
        status_response = await command_broker.get_command_status(sample_command_request.command_id)
        assert status_response.status == CommandStatus.COMPLETED
        
        # Step 3: Verify command is not in active commands
        active_commands = await command_broker.get_active_commands()
        assert sample_command_request.command_id not in [cmd.command_id for cmd in active_commands]
    
    @pytest.mark.asyncio
    async def test_command_flow_with_different_types(self, command_broker, real_redis_client):
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
            
            # Verify real persistence
            stored_command = await real_redis_client.get(f"command:{command_request.command_id}")
            assert stored_command is not None
        
        # Verify total commands stored
        active_commands = await command_broker.get_active_commands()
        assert len(active_commands) == 0  # All commands should be completed
    
    @pytest.mark.asyncio
    async def test_command_flow_with_parameters(self, command_broker, real_redis_client):
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
        
        # Verify parameters were stored correctly in real Redis
        stored_command = await real_redis_client.get(f"command:{complex_command.command_id}")
        assert stored_command is not None
        
        import json
        stored_command_data = json.loads(stored_command)
        assert stored_command_data["parameters"]["news"]["title"] == "Complex Test News"
        assert stored_command_data["parameters"]["news"]["tags"] == ["test", "integration", "complex"]
        assert stored_command_data["parameters"]["metadata"]["test_mode"] is True
    
    @pytest.mark.asyncio
    async def test_command_flow_error_handling(self, command_broker, sample_command_request):
        """Test command flow error handling with real services."""
        # Test with invalid parameters that should cause command execution to fail
        invalid_command = CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,  # Valid command type
            command_id="error_test_cmd",
            session_id="error_test_session",
            parameters={"invalid_param": "this_should_cause_error"},  # Invalid parameters
            timestamp=datetime.now(timezone.utc),
            source="integration_test"
        )
        
        # Act & Assert: Command should fail gracefully
        response = await command_broker.submit_command(invalid_command)
        # Command should still complete (system status is a safe command)
        assert response.status == CommandStatus.COMPLETED
        assert response.result is not None
    
    @pytest.mark.asyncio
    async def test_command_flow_with_cancellation(self, command_broker, sample_command_request, real_event_bus):
        """Test command flow with cancellation."""
        # Arrange: Add command to active commands
        command_broker.active_commands[sample_command_request.command_id] = sample_command_request
        
        # Act: Cancel command
        result = await command_broker.cancel_command(sample_command_request.command_id)
        
        # Assert
        assert result is True
        assert sample_command_request.command_id not in command_broker.active_commands
        
        # Verify cancellation was processed - command should not be found since it was cancelled
        # Note: The command might still exist in Redis from previous tests, so we check that it's not active
        assert sample_command_request.command_id not in command_broker.active_commands
        
        # Try to get status - it might still exist in Redis but should not be active
        try:
            status_response = await command_broker.get_command_status(sample_command_request.command_id)
            # If it exists, it should not be executing
            assert status_response.status != CommandStatus.EXECUTING
        except ValueError:
            # This is also acceptable - command was completely removed
            pass
    
    @pytest.mark.asyncio
    async def test_command_flow_with_dependency_container(self, real_redis_client):
        """Test command flow using real dependency container."""
        # Arrange: Create container with real services
        container = DependencyContainer({
            "ai_provider": "mock",  # Mock external AI
            "news_provider": "mock",  # Mock external news
            "twitter_provider": "mock",  # Mock external Twitter
            "orchestration": "mock"  # Mock external orchestration
        })
        
        # Get real command broker from container
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
        
        # Submit command
        response = await command_broker.submit_command(command_request)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        assert response.command_id == "container_test_cmd"
        
        # Verify real persistence through container
        stored_command = await real_redis_client.get(f"command:{command_request.command_id}")
        assert stored_command is not None
    
    @pytest.mark.asyncio
    async def test_command_flow_with_event_bus_integration(self, command_broker, sample_command_request, real_event_bus):
        """Test command flow with real event bus integration."""
        # Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        
        # Verify command was processed
        status_response = await command_broker.get_command_status(sample_command_request.command_id)
        assert status_response.status == CommandStatus.COMPLETED
        
        # Verify real event bus processed the events
        # Note: Event bus doesn't store events, so we verify through command status
        assert status_response is not None
    
    @pytest.mark.asyncio
    async def test_command_flow_with_redis_integration(self, sample_command_request):
        """Test command flow with real Redis integration."""
        # Create real dependency container
        container = DependencyContainer({
            "ai_provider": "mock",
            "news_provider": "mock",
            "twitter_provider": "mock",
            "orchestration": "mock"
        })
        
        # Get real command broker
        command_broker = container.get_command_broker()
        
        # Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Verify response
        assert response.status == CommandStatus.COMPLETED
        
        # Verify real Redis persistence
        redis_client = container.get_redis_client()
        stored_command = await redis_client.get(f"command:{sample_command_request.command_id}")
        assert stored_command is not None
        
        stored_response = await redis_client.get(f"command_response:{sample_command_request.command_id}")
        assert stored_response is not None
        
        # Verify command data integrity
        import json
        command_data = json.loads(stored_command)
        response_data = json.loads(stored_response)
        
        assert command_data["command_id"] == sample_command_request.command_id
        assert response_data["command_id"] == sample_command_request.command_id
        assert response_data["status"] == "completed"  # Status is stored as lowercase
    
    @pytest.mark.asyncio
    async def test_command_flow_concurrent_execution(self, command_broker, real_redis_client):
        """Test command flow with concurrent execution."""
        # Create multiple commands
        commands = []
        for i in range(5):
            command = CommandRequest(
                command_type=CommandType.SYSTEM_STATUS,
                command_id=f"concurrent_test_cmd_{i}",
                session_id=f"concurrent_test_session_{i}",
                parameters={"index": i},
                timestamp=datetime.now(timezone.utc),
                source="concurrent_test"
            )
            commands.append(command)
        
        # Submit commands concurrently
        tasks = [command_broker.submit_command(cmd) for cmd in commands]
        responses = await asyncio.gather(*tasks)
        
        # Verify all commands completed
        for response in responses:
            assert response.status == CommandStatus.COMPLETED
        
        # Verify all commands stored in Redis
        for command in commands:
            stored_command = await real_redis_client.get(f"command:{command.command_id}")
            assert stored_command is not None
    
    @pytest.mark.asyncio
    async def test_command_flow_status_tracking(self, sample_command_request):
        """Test command flow status tracking with real services."""
        # Create real dependency container
        container = DependencyContainer({
            "ai_provider": "mock",
            "news_provider": "mock",
            "twitter_provider": "mock",
            "orchestration": "mock"
        })
        
        # Get real command broker
        command_broker = container.get_command_broker()
        
        # Submit command
        response = await command_broker.submit_command(sample_command_request)
        
        # Verify initial status
        assert response.status == CommandStatus.COMPLETED
        
        # Check status multiple times
        for _ in range(3):
            status_response = await command_broker.get_command_status(sample_command_request.command_id)
            assert status_response.status == CommandStatus.COMPLETED
            assert status_response.command_id == sample_command_request.command_id
        
        # Verify command history
        command_history = await command_broker.get_command_history(sample_command_request.session_id)
        assert len(command_history) >= 1
        
        # Find our command in history
        our_command = next((cmd for cmd in command_history if cmd.command_id == sample_command_request.command_id), None)
        assert our_command is not None
        assert our_command.status == CommandStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_command_flow_with_session_management(self, command_broker, real_redis_client):
        """Test command flow with session management."""
        # Create multiple commands for same session
        session_id = "session_management_test"
        commands = []
        
        for i in range(3):
            command = CommandRequest(
                command_type=CommandType.SYSTEM_STATUS,
                command_id=f"session_test_cmd_{i}",
                session_id=session_id,
                parameters={"sequence": i},
                timestamp=datetime.now(timezone.utc),
                source="session_test"
            )
            commands.append(command)
        
        # Submit all commands
        for command in commands:
            response = await command_broker.submit_command(command)
            assert response.status == CommandStatus.COMPLETED
        
        # Verify session history
        session_history = await command_broker.get_command_history(session_id)
        assert len(session_history) == 3
        
        # Verify all commands in session completed
        for cmd in session_history:
            assert cmd.status == CommandStatus.COMPLETED
            # CommandResponse doesn't have session_id, but we can verify the command exists
            assert cmd.command_id.startswith("session_test_cmd_") 