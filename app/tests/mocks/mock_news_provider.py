"""
Mock News Provider for testing.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.ports.news_provider import NewsProviderPort, NewsItem, TrendingTopic, NewsProviderInfo


class MockNewsProvider(NewsProviderPort):
    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        return [
            NewsItem(
                id="mock_news_1",
                headline="Mock News Headline",
                content="This is mock news content",
                source="Mock Source",
                url="https://mock.example.com",
                published_at=datetime.now(),
                relevance_score=0.8,
                category="general",
                tags=["mock", "test"]
            )
        ]
    
    async def get_trending_topics(self, max_topics: int = 10) -> List[TrendingTopic]:
        return [
            TrendingTopic(
                term="mock_topic",
                count=100,
                relevance=0.8,
                category="general",
                metadata={"mock": True}
            )
        ]
    
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
        return NewsItem(
            id="mock_ingested_news",
            headline=headline,
            content=content,
            source=source,
            url=url,
            published_at=published_at or datetime.now(),
            relevance_score=relevance_score or 0.5,
            category=category or "general",
            tags=tags or []
        )
    
    async def health_check(self) -> bool:
        return True
    
    async def get_provider_info(self) -> NewsProviderInfo:
        return NewsProviderInfo(
            name="Mock News Provider",
            type="mock",
            description="Mock news provider for testing",
            capabilities=["discover", "ingest", "trending"],
            rate_limits={},
            metadata={"mock": True}
        ) 