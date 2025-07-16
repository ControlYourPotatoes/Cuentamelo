"""
Tests for Frontend Event Bus Service.

This module tests the frontend event bus service which handles real-time event
communication between different parts of the system.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.services.frontend_event_bus import FrontendEventBus
from app.ports.frontend_port import FrontendEvent, EventBus


class TestFrontendEventBus:
    """Test suite for FrontendEventBus."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        redis = AsyncMock()
        redis.publish = AsyncMock()
        redis.subscribe = AsyncMock()
        return redis
    
    @pytest.fixture
    def event_bus(self, mock_redis_client):
        """Frontend event bus with mocked dependencies."""
        return FrontendEventBus(redis_client=mock_redis_client)
    
    @pytest.fixture
    def sample_event(self):
        """Sample frontend event for testing."""
        return FrontendEvent(
            event_type="test_event",
            timestamp=datetime.now(timezone.utc),
            data={"test": "data", "value": 42},
            source="test_service",
            session_id="test_session_001"
        )
    
    @pytest.fixture
    def sample_character_event(self):
        """Sample character-related event."""
        return FrontendEvent(
            event_type="character_response_generated",
            timestamp=datetime.now(timezone.utc),
            data={
                "character_id": "jovani_vazquez",
                "character_name": "Jovani Vázquez",
                "response": "¡Wepa! This is a test response!",
                "confidence": 0.85
            },
            source="character_workflow",
            session_id="test_session_001"
        )
    
    @pytest.fixture
    def sample_news_event(self):
        """Sample news-related event."""
        return FrontendEvent(
            event_type="news_discovered",
            timestamp=datetime.now(timezone.utc),
            data={
                "news_id": "news_001",
                "title": "Test News Title",
                "source": "Test Source",
                "relevance_score": 0.8
            },
            source="news_provider",
            session_id="test_session_001"
        )
    
    @pytest.mark.asyncio
    async def test_publish_event_success(self, event_bus, sample_event, mock_redis_client):
        """Test successful event publishing."""
        # Act
        result = await event_bus.publish_event(sample_event)
        
        # Assert
        assert result is True
        
        # Verify Redis publish was called
        mock_redis_client.publish.assert_called_once()
        
        # Verify the channel and message
        call_args = mock_redis_client.publish.call_args
        assert call_args[0][0] == "frontend_events"
        assert "test_event" in call_args[0][1]
        assert "test_session_001" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_publish_event_without_session(self, event_bus, mock_redis_client):
        """Test publishing event without session ID."""
        # Arrange
        event = FrontendEvent(
            event_type="system_event",
            timestamp=datetime.now(timezone.utc),
            data={"system": "status"},
            source="system_service"
        )
        
        # Act
        result = await event_bus.publish_event(event)
        
        # Assert
        assert result is True
        mock_redis_client.publish.assert_called_once()
        
        # Verify the message doesn't contain session info
        call_args = mock_redis_client.publish.call_args
        assert "system_event" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_publish_event_redis_error(self, event_bus, sample_event, mock_redis_client):
        """Test event publishing with Redis error."""
        # Arrange
        mock_redis_client.publish.side_effect = Exception("Redis connection error")
        
        # Act
        result = await event_bus.publish_event(sample_event)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_character_event(self, event_bus, sample_character_event, mock_redis_client):
        """Test publishing character-related event."""
        # Act
        result = await event_bus.publish_event(sample_character_event)
        
        # Assert
        assert result is True
        
        # Verify the event data is properly serialized
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        assert "jovani_vazquez" in message
        assert "Jovani Vázquez" in message
        assert "¡Wepa!" in message
        assert "0.85" in message
    
    @pytest.mark.asyncio
    async def test_publish_news_event(self, event_bus, sample_news_event, mock_redis_client):
        """Test publishing news-related event."""
        # Act
        result = await event_bus.publish_event(sample_news_event)
        
        # Assert
        assert result is True
        
        # Verify the event data is properly serialized
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        assert "news_001" in message
        assert "Test News Title" in message
        assert "0.8" in message
    
    @pytest.mark.asyncio
    async def test_publish_multiple_events(self, event_bus, sample_event, sample_character_event, mock_redis_client):
        """Test publishing multiple events."""
        # Act
        results = await asyncio.gather(
            event_bus.publish_event(sample_event),
            event_bus.publish_event(sample_character_event)
        )
        
        # Assert
        assert all(results)
        assert mock_redis_client.publish.call_count == 2
    
    @pytest.mark.asyncio
    async def test_event_serialization(self, event_bus, sample_event, mock_redis_client):
        """Test that events are properly serialized."""
        # Act
        await event_bus.publish_event(sample_event)
        
        # Assert
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        # Verify JSON structure
        import json
        event_data = json.loads(message)
        
        assert event_data["event_type"] == "test_event"
        assert event_data["data"]["test"] == "data"
        assert event_data["data"]["value"] == 42
        assert event_data["source"] == "test_service"
        assert event_data["session_id"] == "test_session_001"
        assert "timestamp" in event_data
    
    @pytest.mark.asyncio
    async def test_event_with_complex_data(self, event_bus, mock_redis_client):
        """Test event with complex nested data."""
        # Arrange
        complex_event = FrontendEvent(
            event_type="complex_event",
            timestamp=datetime.now(timezone.utc),
            data={
                "nested": {
                    "level1": {
                        "level2": ["item1", "item2", {"nested_dict": "value"}]
                    }
                },
                "numbers": [1, 2, 3, 4, 5],
                "boolean": True,
                "null_value": None
            },
            source="complex_service",
            session_id="complex_session"
        )
        
        # Act
        result = await event_bus.publish_event(complex_event)
        
        # Assert
        assert result is True
        
        # Verify complex data is properly serialized
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        import json
        event_data = json.loads(message)
        
        assert event_data["data"]["nested"]["level1"]["level2"][0] == "item1"
        assert event_data["data"]["nested"]["level1"]["level2"][2]["nested_dict"] == "value"
        assert event_data["data"]["numbers"] == [1, 2, 3, 4, 5]
        assert event_data["data"]["boolean"] is True
        assert event_data["data"]["null_value"] is None
    
    @pytest.mark.asyncio
    async def test_event_with_special_characters(self, event_bus, mock_redis_client):
        """Test event with special characters and Unicode."""
        # Arrange
        special_event = FrontendEvent(
            event_type="special_chars_event",
            timestamp=datetime.now(timezone.utc),
            data={
                "message": "¡Hola! ¿Cómo estás? 🇵🇷",
                "special_chars": "áéíóú ñ ü",
                "emojis": "🎉🔥💯",
                "quotes": 'He said "Hello" and she replied \'Hi\''
            },
            source="special_service",
            session_id="special_session"
        )
        
        # Act
        result = await event_bus.publish_event(special_event)
        
        # Assert
        assert result is True
        
        # Verify special characters are preserved
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        import json
        event_data = json.loads(message)
        
        assert "¡Hola!" in event_data["data"]["message"]
        assert "áéíóú" in event_data["data"]["special_chars"]
        assert "🎉" in event_data["data"]["emojis"]
        assert '"Hello"' in event_data["data"]["quotes"]
    
    @pytest.mark.asyncio
    async def test_event_timestamp_format(self, event_bus, sample_event, mock_redis_client):
        """Test that event timestamps are properly formatted."""
        # Act
        await event_bus.publish_event(sample_event)
        
        # Assert
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        import json
        event_data = json.loads(message)
        
        # Verify timestamp is ISO format
        timestamp_str = event_data["timestamp"]
        assert "T" in timestamp_str
        assert "Z" in timestamp_str or "+" in timestamp_str
        
        # Verify it can be parsed back to datetime
        from datetime import datetime
        parsed_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        assert isinstance(parsed_timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_event_bus_initialization(self, mock_redis_client):
        """Test event bus initialization."""
        # Act
        event_bus = FrontendEventBus(redis_client=mock_redis_client)
        
        # Assert
        assert event_bus.redis_client == mock_redis_client
        assert hasattr(event_bus, 'publish_event')
    
    @pytest.mark.asyncio
    async def test_event_bus_interface_compliance(self, event_bus):
        """Test that event bus implements the EventBus interface."""
        # Assert
        assert isinstance(event_bus, EventBus)
        assert hasattr(event_bus, 'publish_event')
        assert asyncio.iscoroutinefunction(event_bus.publish_event)
    
    @pytest.mark.asyncio
    async def test_concurrent_event_publishing(self, event_bus, mock_redis_client):
        """Test concurrent event publishing."""
        # Arrange
        events = [
            FrontendEvent(
                event_type=f"concurrent_event_{i}",
                timestamp=datetime.now(timezone.utc),
                data={"index": i},
                source="concurrent_test",
                session_id="concurrent_session"
            )
            for i in range(10)
        ]
        
        # Act
        results = await asyncio.gather(*[
            event_bus.publish_event(event) for event in events
        ])
        
        # Assert
        assert all(results)
        assert mock_redis_client.publish.call_count == 10
    
    @pytest.mark.asyncio
    async def test_event_with_empty_data(self, event_bus, mock_redis_client):
        """Test event with empty data."""
        # Arrange
        empty_event = FrontendEvent(
            event_type="empty_data_event",
            timestamp=datetime.now(timezone.utc),
            data={},
            source="empty_service",
            session_id="empty_session"
        )
        
        # Act
        result = await event_bus.publish_event(empty_event)
        
        # Assert
        assert result is True
        
        # Verify empty data is handled properly
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        import json
        event_data = json.loads(message)
        assert event_data["data"] == {}
    
    @pytest.mark.asyncio
    async def test_event_with_large_data(self, event_bus, mock_redis_client):
        """Test event with large data payload."""
        # Arrange
        large_data = {
            "large_list": list(range(1000)),
            "large_string": "x" * 10000,
            "nested_data": {
                f"key_{i}": f"value_{i}" for i in range(100)
            }
        }
        
        large_event = FrontendEvent(
            event_type="large_data_event",
            timestamp=datetime.now(timezone.utc),
            data=large_data,
            source="large_service",
            session_id="large_session"
        )
        
        # Act
        result = await event_bus.publish_event(large_event)
        
        # Assert
        assert result is True
        
        # Verify large data is handled properly
        call_args = mock_redis_client.publish.call_args
        message = call_args[0][1]
        
        import json
        event_data = json.loads(message)
        
        assert len(event_data["data"]["large_list"]) == 1000
        assert len(event_data["data"]["large_string"]) == 10000
        assert len(event_data["data"]["nested_data"]) == 100 