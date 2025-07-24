"""
Comprehensive tests for FrontendEventBus.

This test suite follows the testing framework revamp plan principles:
- Uses pytest fixtures and dependency injection
- Tests both success and error cases
- Validates Redis pub/sub interactions
- Includes integration tests for complete event flow
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from app.services.frontend_event_bus import FrontendEventBus
from app.ports.frontend_port import FrontendEvent, EventBus
from app.services.redis_client import RedisClient


class TestFrontendEventBus:
    """Test suite for FrontendEventBus."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing."""
        redis = AsyncMock(spec=RedisClient)
        redis.publish = AsyncMock()
        
        # Create a proper mock pubsub object
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        # Make pubsub() return the mock object, not a coroutine
        redis.pubsub = MagicMock(return_value=mock_pubsub)
        
        return redis
    
    @pytest.fixture
    def frontend_event_bus(self, mock_redis_client):
        """Frontend event bus with mocked Redis client."""
        return FrontendEventBus(redis_client=mock_redis_client)
    
    @pytest.fixture
    def sample_frontend_event(self):
        """Sample frontend event for testing."""
        return FrontendEvent(
            event_type="test_event",
            timestamp=datetime.now(timezone.utc),
            data={"test_key": "test_value"},
            source="test_source",
            session_id="test_session_001"
        )
    
    @pytest.fixture
    def sample_system_event(self):
        """Sample system event for testing."""
        return FrontendEvent(
            event_type="system_event",
            timestamp=datetime.now(timezone.utc),
            data={"system_key": "system_value"},
            source="system"
        )

    @pytest.mark.asyncio
    async def test_publish_event_success(self, frontend_event_bus, sample_frontend_event, mock_redis_client):
        """Test successful event publishing."""
        # Act
        await frontend_event_bus.publish_event(sample_frontend_event)
        
        # Assert
        assert mock_redis_client.publish.call_count == 2  # General and session-specific channels
        
        # Verify general channel publish
        general_call = mock_redis_client.publish.call_args_list[0]
        assert general_call[0][0] == "frontend:events"
        published_data = json.loads(general_call[0][1])
        assert published_data["event_type"] == "test_event"
        assert published_data["data"]["test_key"] == "test_value"
        
        # Verify session-specific channel publish
        session_call = mock_redis_client.publish.call_args_list[1]
        assert session_call[0][0] == "frontend:session:test_session_001"
        session_data = json.loads(session_call[0][1])
        assert session_data["event_type"] == "test_event"
    
    @pytest.mark.asyncio
    async def test_publish_event_no_session(self, frontend_event_bus, sample_system_event, mock_redis_client):
        """Test event publishing without session ID."""
        # Act
        await frontend_event_bus.publish_event(sample_system_event)
        
        # Assert
        assert mock_redis_client.publish.call_count == 1  # Only general channel
        
        # Verify general channel publish
        call_args = mock_redis_client.publish.call_args
        assert call_args[0][0] == "frontend:events"
        published_data = json.loads(call_args[0][1])
        assert published_data["event_type"] == "system_event"
    
    @pytest.mark.asyncio
    async def test_publish_event_redis_error(self, mock_redis_client, sample_frontend_event):
        """Test event publishing with Redis error."""
        # Arrange
        mock_redis_client.publish.side_effect = Exception("Redis connection error")
        event_bus = FrontendEventBus(redis_client=mock_redis_client)
        
        # Act & Assert
        with pytest.raises(Exception, match="Redis connection error"):
            await event_bus.publish_event(sample_frontend_event)
    
    @pytest.mark.asyncio
    async def test_subscribe_to_events_success(self, frontend_event_bus, mock_redis_client):
        """Test successful event subscription."""
        # Arrange
        session_id = "test_session_001"
        mock_pubsub = AsyncMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        
        # Mock message stream
        mock_message = {
            "type": "message",
            "data": json.dumps({
                "event_type": "test_event",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"test_key": "test_value"},
                "source": "test_source"
            })
        }
        
        async def mock_listen():
            yield mock_message
        
        # Set the return value to the async generator, not a coroutine
        mock_pubsub.listen = mock_listen
        
        # Act
        events = []
        async for event in frontend_event_bus.subscribe_to_events(session_id):
            events.append(event)
            break  # Only get first event for test
        
        # Assert
        assert len(events) == 1
        assert events[0].event_type == "test_event"
        assert events[0].data["test_key"] == "test_value"
        
        # Verify subscription setup
        mock_pubsub.subscribe.assert_called()
        assert mock_pubsub.subscribe.call_count == 2  # General and session channels
    
    @pytest.mark.asyncio
    async def test_subscribe_to_events_parse_error(self, frontend_event_bus, mock_redis_client):
        """Test event subscription with JSON parse error."""
        # Arrange
        session_id = "test_session_001"
        mock_pubsub = AsyncMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        
        # Mock invalid message
        mock_message = {
            "type": "message",
            "data": "invalid_json"
        }
        
        async def mock_listen():
            yield mock_message
        
        # Set the return value to the async generator, not a coroutine
        mock_pubsub.listen = mock_listen
        
        # Act
        events = []
        async for event in frontend_event_bus.subscribe_to_events(session_id):
            events.append(event)
            break
        
        # Assert - Should skip invalid message and not raise exception
        assert len(events) == 0
    
    @pytest.mark.asyncio
    async def test_subscribe_to_events_unsubscribe(self, frontend_event_bus, mock_redis_client):
        """Test event subscription cleanup on unsubscribe."""
        # Arrange
        session_id = "test_session_001"
        mock_pubsub = AsyncMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        
        # Mock empty message stream
        async def mock_listen():
            if False:  # This will never yield anything
                yield {}
        
        # Set the return value to the async generator, not a coroutine
        mock_pubsub.listen = mock_listen
        
        # Act
        events = []
        async for event in frontend_event_bus.subscribe_to_events(session_id):
            events.append(event)
        
        # Assert
        assert len(events) == 0
        # Verify cleanup was called - the subscription should be removed from active subscriptions
        assert session_id not in frontend_event_bus._active_subscriptions
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_events_success(self, frontend_event_bus, mock_redis_client):
        """Test successful event unsubscription."""
        # Arrange
        session_id = "test_session_001"
        mock_pubsub = AsyncMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        frontend_event_bus.pubsub = mock_pubsub
        
        # Act
        result = await frontend_event_bus.unsubscribe_from_events(session_id)
        
        # Assert
        assert result is True
        assert frontend_event_bus._active_subscriptions[session_id] is False
        mock_pubsub.unsubscribe.assert_called()
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_events_error(self, frontend_event_bus, mock_redis_client):
        """Test event unsubscription with error."""
        # Arrange
        session_id = "test_session_001"
        mock_pubsub = AsyncMock()
        mock_pubsub.unsubscribe.side_effect = Exception("Unsubscribe error")
        mock_redis_client.pubsub.return_value = mock_pubsub
        frontend_event_bus.pubsub = mock_pubsub
        
        # Act
        result = await frontend_event_bus.unsubscribe_from_events(session_id)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_system_event(self, frontend_event_bus, mock_redis_client):
        """Test publishing system event."""
        # Act
        await frontend_event_bus.publish_system_event(
            event_type="system_test",
            data={"system_data": "test"},
            source="test_system"
        )
        
        # Assert
        mock_redis_client.publish.assert_called_once()
        call_args = mock_redis_client.publish.call_args
        assert call_args[0][0] == "frontend:events"
        
        published_data = json.loads(call_args[0][1])
        assert published_data["event_type"] == "system_test"
        assert published_data["data"]["system_data"] == "test"
        assert published_data["source"] == "test_system"
    
    @pytest.mark.asyncio
    async def test_publish_session_event(self, frontend_event_bus, mock_redis_client):
        """Test publishing session-specific event."""
        # Act
        await frontend_event_bus.publish_session_event(
            session_id="test_session_001",
            event_type="session_test",
            data={"session_data": "test"},
            source="test_session"
        )
        
        # Assert
        assert mock_redis_client.publish.call_count == 2  # General and session channels
        
        # Verify session channel publish
        session_call = mock_redis_client.publish.call_args_list[1]
        assert session_call[0][0] == "frontend:session:test_session_001"
        
        session_data = json.loads(session_call[0][1])
        assert session_data["event_type"] == "session_test"
        assert session_data["data"]["session_data"] == "test"
        assert session_data["session_id"] == "test_session_001"
    
    @pytest.mark.asyncio
    async def test_should_receive_event_same_session(self, frontend_event_bus):
        """Test event filtering for same session."""
        # Arrange
        event = FrontendEvent(
            event_type="test",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="test",
            session_id="test_session_001"
        )
        session_id = "test_session_001"
        
        # Act
        should_receive = frontend_event_bus._should_receive_event(event, session_id)
        
        # Assert
        assert should_receive is True
    
    @pytest.mark.asyncio
    async def test_should_receive_event_different_session(self, frontend_event_bus):
        """Test event filtering for different session."""
        # Arrange
        event = FrontendEvent(
            event_type="test",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="test",
            session_id="test_session_001"
        )
        session_id = "test_session_002"
        
        # Act
        should_receive = frontend_event_bus._should_receive_event(event, session_id)
        
        # Assert
        assert should_receive is False
    
    @pytest.mark.asyncio
    async def test_should_receive_event_no_session(self, frontend_event_bus):
        """Test event filtering for event without session."""
        # Arrange
        event = FrontendEvent(
            event_type="test",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="test"
        )
        session_id = "test_session_001"
        
        # Act
        should_receive = frontend_event_bus._should_receive_event(event, session_id)
        
        # Assert
        assert should_receive is True
    
    @pytest.mark.asyncio
    async def test_get_active_subscriptions(self, frontend_event_bus):
        """Test getting active subscriptions."""
        # Arrange
        frontend_event_bus._active_subscriptions["session_001"] = True
        frontend_event_bus._active_subscriptions["session_002"] = False
        
        # Act
        active_subscriptions = await frontend_event_bus.get_active_subscriptions()
        
        # Assert
        assert active_subscriptions["session_001"] is True
        assert active_subscriptions["session_002"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, frontend_event_bus, mock_redis_client):
        """Test health check success."""
        # Act
        is_healthy = await frontend_event_bus.health_check()
        
        # Assert
        assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_redis_client):
        """Test health check failure."""
        # Arrange
        mock_redis_client.ping.side_effect = Exception("Redis error")
        event_bus = FrontendEventBus(redis_client=mock_redis_client)
        
        # Act
        is_healthy = await event_bus.health_check()
        
        # Assert
        assert is_healthy is False


class TestFrontendEventBusIntegration:
    """Integration tests for FrontendEventBus."""
    
    @pytest.fixture
    def integration_event_bus(self):
        """Event bus with real Redis client for integration testing."""
        # This would use real Redis in integration tests
        # For now, we'll use mocks but test the complete flow
        mock_redis_client = AsyncMock()
        
        # Create a proper mock pubsub object
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        
        # Make pubsub() return the mock object, not a coroutine
        mock_redis_client.pubsub = MagicMock(return_value=mock_pubsub)
        
        return FrontendEventBus(redis_client=mock_redis_client)
    
    @pytest.mark.asyncio
    async def test_complete_event_flow(self, integration_event_bus):
        """Test complete event flow from publishing to subscription."""
        # Arrange
        session_id = "integration_session_001"
        test_event = FrontendEvent(
            event_type="integration_test",
            timestamp=datetime.now(timezone.utc),
            data={"integration_key": "integration_value"},
            source="integration_test",
            session_id=session_id
        )
        
        # Mock Redis pubsub for subscription
        mock_pubsub = AsyncMock()
        integration_event_bus.redis_client.pubsub.return_value = mock_pubsub
        
        # Mock message stream
        mock_message = {
            "type": "message",
            "data": test_event.json()
        }
        
        async def mock_listen():
            yield mock_message
        
        # Set the return value to the async generator, not a coroutine
        mock_pubsub.listen = mock_listen
        
        # Act - Publish event
        await integration_event_bus.publish_event(test_event)
        
        # Act - Subscribe and receive event
        received_events = []
        async for event in integration_event_bus.subscribe_to_events(session_id):
            received_events.append(event)
            break
        
        # Assert
        assert len(received_events) == 1
        assert received_events[0].event_type == "integration_test"
        assert received_events[0].data["integration_key"] == "integration_value"
        
        # Verify Redis interactions
        integration_event_bus.redis_client.publish.assert_called()
        mock_pubsub.subscribe.assert_called()
    
    @pytest.mark.asyncio
    async def test_multiple_session_events(self, integration_event_bus):
        """Test handling multiple events for different sessions."""
        # Arrange
        session_1 = "session_001"
        session_2 = "session_002"
        
        event_1 = FrontendEvent(
            event_type="session_1_event",
            timestamp=datetime.now(timezone.utc),
            data={"session": "1"},
            source="test",
            session_id=session_1
        )
        
        event_2 = FrontendEvent(
            event_type="session_2_event",
            timestamp=datetime.now(timezone.utc),
            data={"session": "2"},
            source="test",
            session_id=session_2
        )
        
        # Act
        await integration_event_bus.publish_event(event_1)
        await integration_event_bus.publish_event(event_2)
        
        # Assert
        assert integration_event_bus.redis_client.publish.call_count == 4  # 2 events × 2 channels each
        
        # Verify session-specific channels were used
        call_args = integration_event_bus.redis_client.publish.call_args_list
        session_channels = [call[0][0] for call in call_args]
        assert f"frontend:session:{session_1}" in session_channels
        assert f"frontend:session:{session_2}" in session_channels
    
    @pytest.mark.asyncio
    async def test_event_filtering_by_session(self, integration_event_bus):
        """Test that events are properly filtered by session."""
        # Arrange
        session_id = "filter_test_session"
        
        # Event for different session
        other_session_event = FrontendEvent(
            event_type="other_session_event",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="test",
            session_id="other_session"
        )
        
        # Event for target session
        target_session_event = FrontendEvent(
            event_type="target_session_event",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="test",
            session_id=session_id
        )
        
        # Act
        should_receive_other = integration_event_bus._should_receive_event(other_session_event, session_id)
        should_receive_target = integration_event_bus._should_receive_event(target_session_event, session_id)
        
        # Assert
        assert should_receive_other is False
        assert should_receive_target is True
    
    @pytest.mark.asyncio
    async def test_system_event_broadcast(self, integration_event_bus):
        """Test that system events are broadcast to all sessions."""
        # Arrange
        system_event = FrontendEvent(
            event_type="system_broadcast",
            timestamp=datetime.now(timezone.utc),
            data={"broadcast": "data"},
            source="system"
        )
        
        # Act
        should_receive_session_1 = integration_event_bus._should_receive_event(system_event, "session_1")
        should_receive_session_2 = integration_event_bus._should_receive_event(system_event, "session_2")
        
        # Assert
        assert should_receive_session_1 is True
        assert should_receive_session_2 is True 