"""
Pytest configuration and shared fixtures for Cuentamelo test suite.
"""
import pytest
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.models.conversation import NewsItem, ThreadEngagementState
from app.models.personality import create_jovani_vazquez_personality


class NewsItemBuilder:
    """Builder pattern for creating test news items."""
    
    def __init__(self):
        self.news_data = {
            "id": "test_news_001",
            "headline": "Test News Headline",
            "content": "Test news content for demonstration purposes.",
            "topics": ["test", "demo"],
            "source": "Test Source",
            "published_at": datetime.now(timezone.utc),
            "relevance_score": 0.5
        }
    
    def with_id(self, news_id: str) -> 'NewsItemBuilder':
        self.news_data["id"] = news_id
        return self
    
    def with_headline(self, headline: str) -> 'NewsItemBuilder':
        self.news_data["headline"] = headline
        return self
    
    def with_content(self, content: str) -> 'NewsItemBuilder':
        self.news_data["content"] = content
        return self
    
    def with_topics(self, topics: List[str]) -> 'NewsItemBuilder':
        self.news_data["topics"] = topics
        return self
    
    def with_source(self, source: str) -> 'NewsItemBuilder':
        self.news_data["source"] = source
        return self
    
    def with_relevance_score(self, score: float) -> 'NewsItemBuilder':
        self.news_data["relevance_score"] = score
        return self
    
    def build(self) -> NewsItem:
        return NewsItem(**self.news_data)


class ThreadEngagementStateBuilder:
    """Builder pattern for creating test thread engagement states."""
    
    def __init__(self):
        self.thread_data = {
            "thread_id": "test_thread_001",
            "original_content": "Test thread original content"
        }
    
    def with_thread_id(self, thread_id: str) -> 'ThreadEngagementStateBuilder':
        self.thread_data["thread_id"] = thread_id
        return self
    
    def with_original_content(self, content: str) -> 'ThreadEngagementStateBuilder':
        self.thread_data["original_content"] = content
        return self
    
    def build(self) -> ThreadEngagementState:
        return ThreadEngagementState(**self.thread_data)


@pytest.fixture
def news_item_builder() -> NewsItemBuilder:
    """Fixture providing a news item builder."""
    return NewsItemBuilder()


@pytest.fixture
def thread_state_builder() -> ThreadEngagementStateBuilder:
    """Fixture providing a thread engagement state builder."""
    return ThreadEngagementStateBuilder()


@pytest.fixture
def sample_news_items() -> List[NewsItem]:
    """Fixture providing sample news items for testing."""
    return [
        NewsItemBuilder()
            .with_id("news_001")
            .with_headline("Breaking: New Puerto Rican Music Festival Announced in San Juan")
            .with_content("A major music festival featuring local and international artists will take place in San Juan next month.")
            .with_topics(["music", "entertainment", "culture", "tourism", "san juan"])
            .with_source("Puerto Rico Daily News")
            .with_relevance_score(0.8)
            .build(),
        NewsItemBuilder()
            .with_id("news_002")
            .with_headline("Traffic Chaos in Bayamón: Major Construction Project Delays Commuters")
            .with_content("Ongoing construction on Highway 22 in Bayamón is causing significant delays for morning commuters.")
            .with_topics(["traffic", "construction", "bayamón", "transportation", "daily life"])
            .with_source("El Nuevo Día")
            .with_relevance_score(0.6)
            .build(),
        NewsItemBuilder()
            .with_id("news_003")
            .with_headline("Cultural Heritage: Restoration of Historic Buildings in Old San Juan")
            .with_content("The government has announced funding for the restoration of several historic buildings in Old San Juan.")
            .with_topics(["culture", "history", "old san juan", "heritage", "restoration"])
            .with_source("Caribbean Business")
            .with_relevance_score(0.7)
            .build()
    ]


@pytest.fixture
def jovani_personality():
    """Fixture providing Jovani Vázquez personality data."""
    return create_jovani_vazquez_personality()


@pytest.fixture
def politico_personality():
    """Fixture providing Político Boricua personality data."""
    # For now, return Jovani's personality as a placeholder
    # This can be updated when other personalities are implemented
    return create_jovani_vazquez_personality()


@pytest.fixture
def ciudadano_personality():
    """Fixture providing Ciudadano Boricua personality data."""
    # For now, return Jovani's personality as a placeholder
    # This can be updated when other personalities are implemented
    return create_jovani_vazquez_personality()


@pytest.fixture
def historiador_personality():
    """Fixture providing Historiador Cultural personality data."""
    # For now, return Jovani's personality as a placeholder
    # This can be updated when other personalities are implemented
    return create_jovani_vazquez_personality()


@pytest.fixture
def sample_thread_state() -> ThreadEngagementState:
    """Fixture providing a sample thread engagement state."""
    return ThreadEngagementStateBuilder()\
        .with_thread_id("test_thread_001")\
        .with_original_content("Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷")\
        .build()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock service fixtures for new infrastructure
from unittest.mock import AsyncMock, MagicMock, patch
from app.ports.command_broker_port import CommandResponse, CommandStatus
from app.ports.twitter_provider import TwitterPostResult, TwitterPost, TwitterPostStatus

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    redis = AsyncMock()
    redis.set = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.publish = AsyncMock()
    redis.subscribe = AsyncMock()
    return redis


@pytest.fixture
def mock_event_bus():
    """Mock event bus for testing."""
    event_bus = AsyncMock()
    event_bus.publish_event = AsyncMock()
    return event_bus


@pytest.fixture
def mock_command_handler():
    """Mock command handler for testing."""
    handler = AsyncMock()
    handler.execute_command.return_value = CommandResponse(
        command_id="test_cmd_001",
        status=CommandStatus.COMPLETED,
        result={"message": "Test command executed successfully"},
        timestamp=datetime.now(timezone.utc),
        execution_time=0.5
    )
    return handler


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing."""
    provider = AsyncMock()
    provider.generate_response = AsyncMock(return_value="Mock AI response")
    provider.health_check = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def mock_news_provider():
    """Mock news provider for testing."""
    provider = AsyncMock()
    provider.discover_latest_news = AsyncMock(return_value=[])
    provider.get_trending_topics = AsyncMock(return_value=[])
    provider.health_check = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def mock_twitter_provider():
    """Mock Twitter provider for testing."""
    provider = AsyncMock()
    provider.post_tweet = AsyncMock(return_value=TwitterPostResult(
        success=True,
        twitter_tweet_id="123456789",
        post=TwitterPost(
            content="Test tweet",
            character_id="test_character",
            character_name="Test Character",
            status=TwitterPostStatus.POSTED
        )
    ))
    return provider


@pytest.fixture
def mock_orchestration_service():
    """Mock orchestration service for testing."""
    service = AsyncMock()
    service.execute_orchestration_cycle = AsyncMock(return_value={
        "success": True,
        "execution_time_ms": 1000,
        "character_reactions": []
    })
    return service


@pytest.fixture
def dependency_container_with_mocks(mock_ai_provider, mock_news_provider, mock_twitter_provider, mock_orchestration_service):
    """Dependency container configured with mock services."""
    with patch('app.services.dependency_container.get_settings') as mock_settings:
        mock_settings.return_value = MagicMock(
            ANTHROPIC_API_KEY="test_key",
            TWITTER_BEARER_TOKEN="test_token",
            DEMO_MODE_ENABLED=True
        )
        
        container = DependencyContainer({
            "ai_provider": "mock",
            "news_provider": "mock", 
            "twitter_provider": "mock",
            "orchestration": "mock"
        })
        
        # Inject mock services directly
        container._services["ai_provider"] = mock_ai_provider
        container._services["news_provider"] = mock_news_provider
        container._services["twitter_provider"] = mock_twitter_provider
        container._services["orchestration_service"] = mock_orchestration_service
        
        return container


# Test data constants
MUSIC_FESTIVAL_NEWS = {
    "id": "music_festival",
    "headline": "New Puerto Rican Music Festival Announced",
    "content": "A major music festival featuring local and international artists will take place in San Juan next month.",
    "topics": ["music", "entertainment", "culture"],
    "source": "Test",
    "relevance_score": 0.9
}

TRAFFIC_NEWS = {
    "id": "traffic_news",
    "headline": "Traffic Chaos in Bayamón",
    "content": "Ongoing construction on Highway 22 in Bayamón is causing significant delays.",
    "topics": ["traffic", "construction", "bayamón"],
    "source": "Test",
    "relevance_score": 0.6
}

CULTURAL_NEWS = {
    "id": "cultural_news",
    "headline": "Cultural Heritage Restoration",
    "content": "The government has announced funding for the restoration of historic buildings in Old San Juan.",
    "topics": ["culture", "history", "old san juan"],
    "source": "Test",
    "relevance_score": 0.7
} 