"""
News Provider Port - Interface for news discovery and ingestion.
This abstracts away the specific news source (Twitter, RSS, APIs, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.models.conversation import NewsItem


class TrendingTopic(BaseModel):
    """Trending topic data model."""
    term: str
    count: int
    relevance: float
    category: str
    metadata: Dict[str, Any] = {}


class NewsProviderInfo(BaseModel):
    """Information about a news provider."""
    name: str
    type: str  # 'twitter', 'rss', 'api', 'simulated'
    description: str
    capabilities: List[str]
    rate_limits: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class NewsProviderPort(ABC):
    """
    Port interface for news discovery and ingestion.

    This defines the contract that news providers must implement,
    allowing us to swap between different news sources (Twitter, RSS, APIs, etc.)
    while maintaining clean architecture principles.
    """

    @abstractmethod
    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """
        Discover latest news items from the provider.

        Args:
            max_results: Maximum number of news items to return
            categories: Filter by news categories (e.g., ['politics', 'entertainment'])
            min_relevance_score: Minimum relevance score (0.0 to 1.0)

        Returns:
            List of NewsItem objects
        """
        pass

    @abstractmethod
    async def get_trending_topics(self, max_topics: int = 10) -> List[TrendingTopic]:
        """
        Get trending topics from the news provider.

        Args:
            max_topics: Maximum number of trending topics to return

        Returns:
            List of TrendingTopic objects
        """
        pass

    @abstractmethod
    async def ingest_news_item(
        self,
        headline: str,
        content: str,
        source: str,
        url: Optional[str] = None,
        published_at: Optional[datetime] = None,
        relevance_score: Optional[float] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> NewsItem:
        """
        Ingest a single news item into the system.

        Args:
            headline: News headline
            content: News content
            source: News source name
            url: Optional URL to the full article
            published_at: Optional publication timestamp
            relevance_score: Optional relevance score (0.0 to 1.0)
            category: Optional news category
            tags: Optional list of tags

        Returns:
            Created NewsItem object
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the news provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_provider_info(self) -> NewsProviderInfo:
        """
        Get information about the news provider.

        Returns:
            NewsProviderInfo object with provider details
        """
        pass 