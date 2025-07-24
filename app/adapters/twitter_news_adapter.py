"""
Twitter News Adapter - Implements NewsProviderPort using Twitter API.
This adapter discovers news from configured Twitter accounts with smart caching.
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass

from app.ports.news_provider import NewsProviderPort, TrendingTopic, NewsProviderInfo
from app.models.conversation import NewsItem
from app.tools.twitter_connector import TwitterConnector
from app.services.redis_client import RedisClient


@dataclass
class NewsSource:
    """Configuration for a news source account."""
    username: str
    display_name: str
    category: str  # 'news', 'politics', 'culture', 'entertainment'
    relevance_score: float  # 0.0 to 1.0
    is_active: bool = True


class TwitterNewsAdapter(NewsProviderPort):
    """
    Adapter that implements NewsProviderPort using Twitter API.

    Features:
    - Configurable Twitter accounts (no hardcoded accounts)
    - Smart caching to avoid rate limits
    - Relevance scoring for Puerto Rican content
    - Category-based filtering
    """

    def __init__(
        self,
        twitter_connector: TwitterConnector,
        redis_client: RedisClient,
        news_sources_config: Dict[str, Any]
    ):
        self.twitter = twitter_connector
        self.redis = redis_client
        self.cache_ttl = news_sources_config.get("cache_ttl", 3600)
        
        # Load news sources from configuration
        self.news_sources = self._load_news_sources(news_sources_config.get("sources", []))
        
        # Load keywords and hashtags for relevance scoring
        self.news_keywords = news_sources_config.get("keywords", {})
        self.pr_hashtags = news_sources_config.get("hashtags", {})
        
        self.logger = logging.getLogger(__name__)

    def _load_news_sources(self, sources_config: List[Dict[str, Any]]) -> List[NewsSource]:
        """Load news sources from configuration."""
        sources = []
        for source_config in sources_config:
            if source_config.get("is_active", True):
                source = NewsSource(
                    username=source_config["username"],
                    display_name=source_config["display_name"],
                    category=source_config["category"],
                    relevance_score=source_config["relevance_score"]
                )
                sources.append(source)
        return sources

    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """
        Discover latest news from monitored Twitter accounts.
        
        Args:
            max_results: Maximum number of news items to return
            categories: Filter by news categories
            min_relevance_score: Minimum relevance score
            
        Returns:
            List of NewsItem objects
        """
        try:
            self.logger.info(f"Discovering latest news from {len(self.news_sources)} sources")
            
            # Check cache first
            cached_news = await self._get_cached_news()
            if cached_news:
                self.logger.info(f"Returning {len(cached_news)} cached news items")
                filtered_news = self._filter_news(cached_news, categories, min_relevance_score)
                return filtered_news[:max_results]
            
            # Fetch fresh news from Twitter
            fresh_news = await self._fetch_fresh_news()
            
            # Cache the results
            await self._cache_news(fresh_news)
            
            # Filter and return
            filtered_news = self._filter_news(fresh_news, categories, min_relevance_score)
            self.logger.info(f"Discovered {len(filtered_news)} filtered news items")
            return filtered_news[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error discovering news: {str(e)}")
            # Return cached news as fallback
            cached_news = await self._get_cached_news()
            if cached_news:
                filtered_news = self._filter_news(cached_news, categories, min_relevance_score)
                return filtered_news[:max_results]
            return []

    async def get_trending_topics(self, max_topics: int = 10) -> List[TrendingTopic]:
        """
        Get trending topics from Twitter.
        
        Args:
            max_topics: Maximum number of trending topics to return
            
        Returns:
            List of TrendingTopic objects
        """
        try:
            # Check cache first
            cache_key = "trending_topics"
            cached_topics = await self.redis.get(cache_key)
            if cached_topics:
                topics_data = json.loads(cached_topics)
                return [TrendingTopic(**topic) for topic in topics_data[:max_topics]]
            
            # Extract trending topics from recent news
            news_items = await self.discover_latest_news(max_results=50)
            trending_topics = self._extract_trending_topics(news_items)
            
            # Cache trending topics
            topics_data = [topic.dict() for topic in trending_topics]
            await self.redis.setex(cache_key, self.cache_ttl, json.dumps(topics_data))
            
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
            
            # Add to cache
            await self._add_to_cache(news_item)
            
            self.logger.info(f"Ingested news item: {headline}")
            return news_item
            
        except Exception as e:
            self.logger.error(f"Error ingesting news item: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """
        Check if the Twitter news provider is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check Twitter API health
            twitter_healthy = await self.twitter.health_check()
            
            # Check Redis health
            redis_healthy = await self.redis.ping()
            
            return twitter_healthy and redis_healthy
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    async def get_provider_info(self) -> NewsProviderInfo:
        """
        Get information about the Twitter news provider.
        
        Returns:
            NewsProviderInfo object with provider details
        """
        return NewsProviderInfo(
            name="Twitter News Provider",
            type="twitter",
            description="Discovers news from configured Puerto Rican Twitter accounts",
            capabilities=[
                "news_discovery",
                "trending_topics",
                "relevance_scoring",
                "caching",
                "category_filtering"
            ],
            rate_limits={
                "twitter_api": "15 requests per 15 minutes",
                "cache_ttl": f"{self.cache_ttl} seconds"
            },
            metadata={
                "sources_count": len(self.news_sources),
                "active_sources": len([s for s in self.news_sources if s.is_active])
            }
        )

    async def _fetch_fresh_news(self) -> List[NewsItem]:
        """Fetch fresh news from Twitter accounts."""
        all_news = []
        
        for source in self.news_sources:
            if not source.is_active:
                continue
                
            try:
                # Fetch latest tweets from this account
                tweets = await self._fetch_account_tweets(source.username, max_results=5)
                
                for tweet in tweets:
                    # Convert tweet to news item
                    news_item = await self._tweet_to_news_item(tweet, source)
                    if news_item:
                        all_news.append(news_item)
                
                # Rate limiting - small delay between accounts
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error fetching tweets from {source.username}: {str(e)}")
                continue
        
        # Sort by relevance and recency
        all_news.sort(key=lambda x: (x.relevance_score, x.published_at), reverse=True)
        
        return all_news

    async def _fetch_account_tweets(self, username: str, max_results: int = 5) -> List[Dict]:
        """Fetch latest tweets from a specific account."""
        try:
            # Get user ID first
            user = await self.twitter.get_user_by_username(username)
            if not user:
                self.logger.warning(f"User {username} not found")
                return []
            
            # Get user's tweets
            tweets = await self.twitter.get_user_tweets(
                user_id=user["id"],
                max_results=max_results,
                exclude_retweets=True,
                exclude_replies=True
            )
            
            return tweets
            
        except Exception as e:
            self.logger.error(f"Error fetching tweets from {username}: {str(e)}")
            return []

    async def _tweet_to_news_item(self, tweet: Dict, source: NewsSource) -> Optional[NewsItem]:
        """Convert a tweet to a NewsItem if it's news-worthy."""
        try:
            content = tweet.get("text", "")
            
            # Skip if content is too short or doesn't seem like news
            if len(content) < 20:
                return None
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content, source.category)
            
            # Skip if relevance is too low
            if relevance_score < 0.3:
                return None
            
            # Create news item
            news_item = NewsItem(
                id=f"tweet_{tweet.get('id', 'unknown')}",
                headline=self._generate_headline(content, source),
                content=content,
                source=source.display_name,
                url=f"https://twitter.com/{source.username}/status/{tweet.get('id')}",
                published_at=tweet.get("created_at", datetime.now(timezone.utc).isoformat()),
                relevance_score=relevance_score
            )
            
            return news_item
            
        except Exception as e:
            self.logger.error(f"Error converting tweet to news item: {str(e)}")
            return None

    def _calculate_relevance_score(self, content: str, category: str) -> float:
        """Calculate relevance score for content."""
        score = 0.0
        content_lower = content.lower()
        
        # Base score from source category
        if category == "news":
            score += 0.3
        elif category == "politics":
            score += 0.4
        elif category == "entertainment":
            score += 0.2
        elif category == "culture":
            score += 0.25
        
        # Add score for news keywords
        for keyword, weight in self.news_keywords.items():
            if keyword.lower() in content_lower:
                score += weight * 0.1
        
        # Add score for Puerto Rican hashtags
        for hashtag, weight in self.pr_hashtags.items():
            if hashtag.lower() in content_lower:
                score += weight * 0.2
        
        # Cap at 1.0
        return min(score, 1.0)

    def _generate_headline(self, content: str, source: NewsSource) -> str:
        """Generate a headline from tweet content."""
        # Simple headline generation - take first sentence or first 100 chars
        if len(content) <= 100:
            return content
        
        # Try to find sentence boundary
        for i, char in enumerate(content[:100]):
            if char in '.!?':
                return content[:i+1].strip()
        
        return content[:100].strip() + "..."

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
                # For now, we'll use a simple approach - check if any category keywords are in the content
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
            if data["count"] >= 2:  # Only include terms that appear multiple times
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

    async def _cache_news(self, news_items: List[NewsItem]):
        """Cache news items in Redis."""
        try:
            cache_key = "cached_news"
            news_data = []
            
            for item in news_items:
                news_data.append({
                    "id": item.id,
                    "headline": item.headline,
                    "content": item.content,
                    "source": item.source,
                    "url": item.url,
                    "published_at": item.published_at,
                    "relevance_score": item.relevance_score
                })
            
            await self.redis.setex(cache_key, self.cache_ttl, json.dumps(news_data))
            self.logger.info(f"Cached {len(news_items)} news items")
            
        except Exception as e:
            self.logger.error(f"Error caching news: {str(e)}")

    async def _get_cached_news(self) -> List[NewsItem]:
        """Get cached news items from Redis."""
        try:
            cache_key = "cached_news"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                news_data = json.loads(cached_data)
                news_items = []
                
                for item_data in news_data:
                    news_item = NewsItem(**item_data)
                    news_items.append(news_item)
                
                return news_items
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting cached news: {str(e)}")

    async def _add_to_cache(self, news_item: NewsItem):
        """Add a single news item to cache."""
        try:
            # Get existing cached news
            cached_news = await self._get_cached_news()
            
            # Add new item
            cached_news.append(news_item)
            
            # Sort by relevance and recency
            cached_news.sort(key=lambda x: (x.relevance_score, x.published_at), reverse=True)
            
            # Keep only top 50 items
            cached_news = cached_news[:50]
            
            # Update cache
            await self._cache_news(cached_news)
            
        except Exception as e:
            self.logger.error(f"Error adding to cache: {str(e)}") 