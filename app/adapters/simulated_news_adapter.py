"""
Simulated News Adapter - Implements NewsProviderPort for demos and testing.
This adapter provides pre-configured news scenarios for demonstrations.
"""
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime, timezone
import random

from app.ports.news_provider import NewsProviderPort, TrendingTopic, NewsProviderInfo
from app.models.conversation import NewsItem


class SimulatedNewsAdapter(NewsProviderPort):
    """
    Adapter that implements NewsProviderPort for demos and testing.

    Features:
    - Pre-configured news scenarios
    - Easy news injection for demos
    - No external dependencies
    - Realistic news data for testing
    """

    def __init__(self, demo_scenarios_config: Dict[str, Any]):
        self.demo_scenarios = demo_scenarios_config.get("scenarios", [])
        self.current_scenario_index = 0
        self.ingested_news = []
        self.logger = logging.getLogger(__name__)

    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """
        Discover latest news from demo scenarios.
        
        Args:
            max_results: Maximum number of news items to return
            categories: Filter by news categories
            min_relevance_score: Minimum relevance score
            
        Returns:
            List of NewsItem objects
        """
        try:
            self.logger.info(f"Discovering latest news from {len(self.demo_scenarios)} demo scenarios")
            
            # Combine demo scenarios with ingested news
            all_news = []
            
            # Add demo scenarios
            for scenario in self.demo_scenarios:
                news_item = self._scenario_to_news_item(scenario)
                if news_item:
                    all_news.append(news_item)
            
            # Add ingested news
            all_news.extend(self.ingested_news)
            
            # Filter by categories and relevance
            filtered_news = self._filter_news(all_news, categories, min_relevance_score)
            
            # Sort by relevance and recency
            filtered_news.sort(key=lambda x: (x.relevance_score, x.published_at), reverse=True)
            
            self.logger.info(f"Discovered {len(filtered_news)} filtered news items")
            return filtered_news[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error discovering news: {str(e)}")
            return []

    async def get_trending_topics(self, max_topics: int = 10) -> List[TrendingTopic]:
        """
        Get trending topics from demo scenarios.
        
        Args:
            max_topics: Maximum number of trending topics to return
            
        Returns:
            List of TrendingTopic objects
        """
        try:
            # Get all news items
            news_items = await self.discover_latest_news(max_results=50)
            
            # Extract trending topics
            trending_topics = self._extract_trending_topics(news_items)
            
            return trending_topics[:max_topics]
            
        except Exception as e:
            self.logger.error(f"Error getting trending topics: {str(e)}")
            return []

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
            relevance_score: Optional relevance score
            category: Optional news category
            tags: Optional list of tags
            
        Returns:
            Created NewsItem object
        """
        try:
            # Calculate relevance score if not provided
            if relevance_score is None:
                relevance_score = self._calculate_relevance_score(content, category)
            
            # Create news item
            news_item = NewsItem(
                id=f"ingested_{datetime.now(timezone.utc).timestamp()}",
                headline=headline,
                content=content,
                source=source,
                url=url,
                published_at=published_at.isoformat() if published_at else datetime.now(timezone.utc).isoformat(),
                relevance_score=relevance_score
            )
            
            # Add to ingested news
            self.ingested_news.append(news_item)
            
            self.logger.info(f"Ingested news item: {headline}")
            return news_item
            
        except Exception as e:
            self.logger.error(f"Error ingesting news item: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the simulated news provider is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Simulated provider is always healthy
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    async def get_provider_info(self) -> NewsProviderInfo:
        """
        Get information about the simulated news provider.
        
        Returns:
            NewsProviderInfo object with provider details
        """
        return NewsProviderInfo(
            name="Simulated News Provider",
            type="simulated",
            description="Provides pre-configured news scenarios for demos and testing",
            capabilities=[
                "demo_scenarios",
                "news_ingestion",
                "trending_topics",
                "category_filtering",
                "no_external_dependencies"
            ],
            rate_limits={},
            metadata={
                "scenarios_count": len(self.demo_scenarios),
                "ingested_news_count": len(self.ingested_news)
            }
        )

    def _scenario_to_news_item(self, scenario: Dict[str, Any]) -> Optional[NewsItem]:
        """Convert a demo scenario to a NewsItem."""
        try:
            return NewsItem(
                id=scenario.get("id", f"scenario_{random.randint(1000, 9999)}"),
                headline=scenario["headline"],
                content=scenario["content"],
                source=scenario["source"],
                url=scenario.get("url"),
                published_at=scenario.get("published_at", datetime.now(timezone.utc).isoformat()),
                relevance_score=scenario.get("relevance_score", 0.8)
            )
        except Exception as e:
            self.logger.error(f"Error converting scenario to news item: {str(e)}")
            return None

    def _calculate_relevance_score(self, content: str, category: Optional[str]) -> float:
        """Calculate relevance score for content."""
        # Simple relevance scoring for simulated provider
        score = 0.5  # Base score
        
        content_lower = content.lower()
        
        # Add score for Puerto Rican keywords
        pr_keywords = ["puerto rico", "boricua", "borinquen", "san juan", "ponce", "mayaguez"]
        for keyword in pr_keywords:
            if keyword in content_lower:
                score += 0.2
        
        # Add score for news keywords
        news_keywords = ["breaking", "noticia", "anuncio", "gobierno", "política", "economía"]
        for keyword in news_keywords:
            if keyword in content_lower:
                score += 0.1
        
        # Add score for category
        if category:
            if category == "politics":
                score += 0.2
            elif category == "entertainment":
                score += 0.15
            elif category == "culture":
                score += 0.15
        
        # Cap at 1.0
        return min(score, 1.0)

    def _filter_news(
        self,
        news_items: List[NewsItem],
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """Filter news items by categories and relevance score."""
        filtered = []
        
        for item in news_items:
            # Check relevance score
            if item.relevance_score < min_relevance_score:
                continue
            
            # Check categories if specified
            if categories:
                # Simple category detection based on content
                content_lower = item.content.lower()
                item_category = "general"
                
                if any(keyword in content_lower for keyword in ["política", "gobierno", "senado", "cámara"]):
                    item_category = "politics"
                elif any(keyword in content_lower for keyword in ["música", "concierto", "artista", "entretenimiento"]):
                    item_category = "entertainment"
                elif any(keyword in content_lower for keyword in ["cultura", "turismo", "museo"]):
                    item_category = "culture"
                
                if item_category not in categories:
                    continue
            
            filtered.append(item)
        
        return filtered

    def _extract_trending_topics(self, news_items: List[NewsItem]) -> List[TrendingTopic]:
        """Extract trending topics from news items."""
        topic_counts = {}
        
        for item in news_items:
            # Extract key terms from content
            terms = self._extract_key_terms(item.content)
            
            for term in terms:
                if term not in topic_counts:
                    topic_counts[term] = {
                        "count": 0,
                        "relevance": 0.0,
                        "category": "general"
                    }
                
                topic_counts[term]["count"] += 1
                topic_counts[term]["relevance"] += item.relevance_score
        
        # Convert to TrendingTopic objects
        trending_topics = []
        for term, data in topic_counts.items():
            if data["count"] >= 1:  # Include all terms for demo
                topic = TrendingTopic(
                    term=term,
                    count=data["count"],
                    relevance=data["relevance"] / data["count"],  # Average relevance
                    category=data["category"]
                )
                trending_topics.append(topic)
        
        # Sort by count and relevance
        trending_topics.sort(key=lambda x: (x.count, x.relevance), reverse=True)
        
        return trending_topics

    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from content."""
        # Simple term extraction - split by spaces and filter
        words = content.lower().split()
        terms = []
        
        for word in words:
            # Remove common words and short words
            if len(word) > 3 and word not in ["the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say", "she", "too", "use"]:
                # Remove punctuation
                word = word.strip(".,!?;:()[]{}'\"")
                if word:
                    terms.append(word)
        
        return terms[:10]  # Limit to top 10 terms

    def add_demo_scenario(self, scenario: Dict[str, Any]):
        """Add a new demo scenario."""
        self.demo_scenarios.append(scenario)
        self.logger.info(f"Added demo scenario: {scenario.get('headline', 'Unknown')}")

    def clear_ingested_news(self):
        """Clear all ingested news items."""
        self.ingested_news.clear()
        self.logger.info("Cleared all ingested news items")

    def get_next_scenario(self) -> Optional[Dict[str, Any]]:
        """Get the next demo scenario in rotation."""
        if not self.demo_scenarios:
            return None
        
        scenario = self.demo_scenarios[self.current_scenario_index]
        self.current_scenario_index = (self.current_scenario_index + 1) % len(self.demo_scenarios)
        return scenario 