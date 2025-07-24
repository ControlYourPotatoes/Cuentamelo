"""
El Nuevo Día News Adapter - Monitors @ElNuevodia Twitter feed for news.
Converts tweets into structured news items for AI character reactions.
"""
import asyncio
import logging
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from app.ports.news_provider import NewsProviderPort, NewsItem, TrendingTopic, NewsProviderInfo
from app.tools.twitter_connector import TwitterConnector
from app.services.redis_client import RedisClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ElNuevoDiaTweet:
    """Represents a tweet from El Nuevo Día with parsed content."""
    tweet_id: str
    content: str
    created_at: datetime
    engagement_metrics: Dict[str, Any]
    is_news: bool
    headline: Optional[str] = None
    topics: Optional[List[str]] = None
    relevance_score: float = 0.0
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.topics is None:
            self.topics = []


class ElNuevoDiaNewsAdapter(NewsProviderPort):
    """
    News adapter for El Nuevo Día Twitter feed.
    
    Monitors @ElNuevoDia tweets and converts them into structured news items
    for AI character reactions. Filters for relevant Puerto Rican news.
    """
    
    def __init__(self, twitter_connector: Optional[TwitterConnector] = None, redis_client: Optional[RedisClient] = None):
        """Initialize the El Nuevo Día news adapter."""
        self.twitter_connector = twitter_connector or TwitterConnector()
        self.redis_client = redis_client or RedisClient()
        self.last_processed_tweet_id: Optional[str] = None
        
        # Cache configuration
        self.cache_ttl = {
            "tweets": 300,  # 5 minutes for tweets
            "trending_topics": 600,  # 10 minutes for trending topics
            "user_info": 3600,  # 1 hour for user info
        }
        self.news_keywords = [
            # Breaking news indicators
            "BREAKING", "ÚLTIMA HORA", "URGENTE", "NOTICIA",
            "ANUNCIO", "DECLARACIÓN", "CONFERENCIA",
            
            # News categories
            "POLÍTICA", "GOBIERNO", "ECONOMÍA", "SALUD",
            "EDUCACIÓN", "DEPORTES", "ENTRETENIMIENTO", "CULTURA",
            "TECNOLOGÍA", "MEDIO AMBIENTE", "SEGURIDAD",
            
            # Puerto Rico specific
            "PUERTO RICO", "SAN JUAN", "GUBERNADOR", "ASAMBLEA",
            "FORTALEZA", "CONGRESO", "SENADO", "CÁMARA",
            "MUNICIPIO", "ALCALDE", "LEGISLATURA"
        ]
        
        # Topics mapping for categorization
        self.topic_keywords = {
            "politics": ["gobierno", "política", "gobernador", "asamblea", "congreso", "senado", "cámara", "legislatura", "fortaleza"],
            "economy": ["economía", "finanzas", "presupuesto", "impuestos", "negocios", "comercio", "empleo"],
            "health": ["salud", "hospital", "médico", "vacuna", "covid", "enfermedad", "tratamiento"],
            "education": ["educación", "escuela", "universidad", "estudiante", "maestro", "departamento de educación"],
            "sports": ["deportes", "baloncesto", "béisbol", "fútbol", "atleta", "equipo", "liga"],
            "entertainment": ["entretenimiento", "música", "artista", "concierto", "película", "teatro", "festival"],
            "culture": ["cultura", "arte", "museo", "tradición", "historia", "patrimonio"],
            "technology": ["tecnología", "internet", "digital", "app", "software", "innovación"],
            "environment": ["medio ambiente", "clima", "energía", "solar", "renovable", "contaminación"],
            "crime": ["crimen", "policía", "investigación", "arresto", "delito", "seguridad"]
        }
        
        logger.info("El Nuevo Día news adapter initialized")
    
    def _get_cache_key(self, key_type: str, **kwargs) -> str:
        """Generate cache key for different types of data."""
        base_key = f"elnuevodia:{key_type}"
        if kwargs:
            # Create a deterministic key from kwargs
            sorted_items = sorted(kwargs.items())
            param_str = ":".join(f"{k}={v}" for k, v in sorted_items)
            return f"{base_key}:{param_str}"
        return base_key
    
    async def _get_cached_tweets(self, username: str, max_results: int, since_id: Optional[str] = None) -> Optional[List]:
        """Get cached tweets if available."""
        try:
            # Test Redis connection first
            if not await self.redis_client.ping():
                logger.warning("Redis not available, skipping cache")
                return None
                
            cache_key = self._get_cache_key("tweets", username=username, max_results=max_results, since_id=since_id)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for tweets: {cache_key}")
                return json.loads(cached_data)
            
            logger.info(f"Cache miss for tweets: {cache_key}")
            return None
            
        except Exception as e:
            logger.warning(f"Cache error when getting tweets: {str(e)}")
            return None
    
    async def _cache_tweets(self, username: str, max_results: int, since_id: Optional[str] = None, tweets: Optional[List] = None):
        """Cache tweets with appropriate TTL."""
        try:
            if not tweets:
                return
                
            # Test Redis connection first
            if not await self.redis_client.ping():
                logger.warning("Redis not available, skipping cache storage")
                return
                
            cache_key = self._get_cache_key("tweets", username=username, max_results=max_results, since_id=since_id)
            cache_data = json.dumps([tweet.__dict__ for tweet in tweets], default=str)
            
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl["tweets"], 
                cache_data
            )
            
            logger.info(f"Cached {len(tweets)} tweets with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache error when storing tweets: {str(e)}")
    
    async def _get_cached_trending_topics(self, max_topics: int) -> Optional[List]:
        """Get cached trending topics if available."""
        try:
            # Test Redis connection first
            if not await self.redis_client.ping():
                logger.warning("Redis not available, skipping cache")
                return None
                
            cache_key = self._get_cache_key("trending_topics", max_topics=max_topics)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for trending topics: {cache_key}")
                return json.loads(cached_data)
            
            logger.info(f"Cache miss for trending topics: {cache_key}")
            return None
            
        except Exception as e:
            logger.warning(f"Cache error when getting trending topics: {str(e)}")
            return None
    
    async def _cache_trending_topics(self, max_topics: int, topics: Optional[List] = None):
        """Cache trending topics with appropriate TTL."""
        try:
            if not topics:
                return
                
            # Test Redis connection first
            if not await self.redis_client.ping():
                logger.warning("Redis not available, skipping cache storage")
                return
                
            cache_key = self._get_cache_key("trending_topics", max_topics=max_topics)
            cache_data = json.dumps([topic.dict() for topic in topics], default=str)
            
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl["trending_topics"], 
                cache_data
            )
            
            logger.info(f"Cached {len(topics)} trending topics with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache error when storing trending topics: {str(e)}")
    
    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """Discover latest news from El Nuevo Día Twitter feed."""
        try:
            # Try to get cached tweets first
            cached_tweets = await self._get_cached_tweets(
                username="ElNuevoDia",
                max_results=max_results * 2,
                since_id=self.last_processed_tweet_id
            )
            
            if cached_tweets:
                logger.info("Using cached tweets for news discovery")
                tweets = cached_tweets
            else:
                # Get recent tweets from @ElNuevoDia
                tweets = await self.twitter_connector.get_user_tweets(
                    username="ElNuevoDia",
                    max_results=max_results * 2,  # Get more to filter
                    since_id=self.last_processed_tweet_id
                )
                
                # Cache the tweets for future use
                await self._cache_tweets(
                    username="ElNuevoDia",
                    max_results=max_results * 2,
                    since_id=self.last_processed_tweet_id,
                    tweets=tweets
                )
            
            if not tweets:
                logger.info("No new tweets found from El Nuevo Día")
                return []
            
            # Parse tweets into news items
            news_items = []
            for tweet in tweets:
                parsed_tweet = self._parse_tweet(tweet)
                
                if parsed_tweet.is_news and parsed_tweet.relevance_score >= min_relevance_score:
                    # Apply category filtering if specified
                    if categories and parsed_tweet.topics and not any(cat.lower() in [topic.lower() for topic in parsed_tweet.topics] for cat in categories):
                        continue
                    
                    news_item = self._convert_to_news_item(parsed_tweet)
                    news_items.append(news_item)
                    
                    # Update last processed tweet ID
                    if not self.last_processed_tweet_id or tweet.tweet_id > self.last_processed_tweet_id:
                        self.last_processed_tweet_id = tweet.tweet_id
            
            # Sort by relevance and limit results
            news_items.sort(key=lambda x: x.relevance_score, reverse=True)
            news_items = news_items[:max_results]
            
            logger.info(f"Discovered {len(news_items)} news items from El Nuevo Día")
            return news_items
            
        except Exception as e:
            logger.error(f"Error discovering news from El Nuevo Día: {str(e)}")
            return []
    
    async def get_trending_topics(self, max_topics: int = 10) -> List[TrendingTopic]:
        """Get trending topics from El Nuevo Día tweets."""
        try:
            # Try to get cached trending topics first
            cached_topics = await self._get_cached_trending_topics(max_topics)
            
            if cached_topics:
                logger.info("Using cached trending topics")
                # Convert back to TrendingTopic objects
                return [TrendingTopic(**topic) for topic in cached_topics]
            
            # Get recent tweets to analyze trending topics
            tweets = await self.twitter_connector.get_user_tweets(
                username="ElNuevoDia",
                max_results=50
            )
            
            if not tweets:
                return []
            
            # Extract hashtags and keywords
            topic_counts = {}
            for tweet in tweets:
                # Extract hashtags
                hashtags = re.findall(r'#(\w+)', tweet.content, re.IGNORECASE)
                for hashtag in hashtags:
                    hashtag_lower = hashtag.lower()
                    topic_counts[hashtag_lower] = topic_counts.get(hashtag_lower, 0) + 1
                
                # Extract keywords from content
                keywords = self._extract_keywords(tweet.content)
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    topic_counts[keyword_lower] = topic_counts.get(keyword_lower, 0) + 1
            
            # Convert to trending topics
            trending_topics = []
            for term, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
                if count >= 2:  # Only include topics mentioned multiple times
                    relevance = min(count / 10.0, 1.0)  # Normalize relevance
                    category = self._categorize_topic(term)
                    
                    trending_topics.append(TrendingTopic(
                        term=term,
                        count=count,
                        relevance=relevance,
                        category=category
                    ))
            
            # Cache the trending topics for future use
            await self._cache_trending_topics(max_topics, trending_topics[:max_topics])
            
            return trending_topics[:max_topics]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
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
        """Ingest a custom news item (not typically used for El Nuevo Día adapter)."""
        # This method is not typically used for El Nuevo Día adapter
        # as we get news from their Twitter feed
        logger.warning("ingest_news_item not typically used for El Nuevo Día adapter")
        
        topics = tags or []
        if category:
            topics.append(category)
        
        return NewsItem(
            headline=headline,
            content=content,
            source=source,
            url=url,
            published_at=published_at or datetime.now(timezone.utc),
            topics=topics,
            relevance_score=relevance_score or 0.5
        )
    
    def _parse_tweet(self, tweet) -> ElNuevoDiaTweet:
        """Parse a tweet to determine if it's news and extract information."""
        content = tweet.content
        content_lower = content.lower()
        
        # Check if this looks like a news tweet
        is_news = any(keyword.lower() in content_lower for keyword in self.news_keywords)
        
        # Extract headline (first sentence or first 100 characters)
        headline = None
        if is_news:
            # Try to extract a clean headline
            sentences = re.split(r'[.!?]+', content)
            if sentences:
                headline = sentences[0].strip()
                if len(headline) > 100:
                    headline = headline[:97] + "..."
        
        # Extract topics
        topics = self._extract_topics(content)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(content, topics)
        
        return ElNuevoDiaTweet(
            tweet_id=tweet.tweet_id,
            content=content,
            created_at=tweet.created_at,
            engagement_metrics=tweet.engagement_metrics,
            is_news=is_news,
            headline=headline,
            topics=topics,
            relevance_score=relevance_score
        )
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from tweet content."""
        content_lower = content.lower()
        topics = []
        
        # Check each topic category
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        # Extract hashtags as topics
        hashtags = re.findall(r'#(\w+)', content, re.IGNORECASE)
        topics.extend(hashtags)
        
        return list(set(topics))  # Remove duplicates
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content."""
        # Remove URLs, mentions, and hashtags
        clean_content = re.sub(r'http\S+|@\w+|#\w+', '', content)
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', clean_content.lower())
        
        # Filter out common words and short words
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _categorize_topic(self, term: str) -> str:
        """Categorize a trending topic."""
        term_lower = term.lower()
        
        for category, keywords in self.topic_keywords.items():
            if any(keyword in term_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _calculate_relevance_score(self, content: str, topics: List[str]) -> float:
        """Calculate relevance score for a news item."""
        content_lower = content.lower()
        score = 0.0
        
        # Base score for having topics
        if topics:
            score += 0.3
        
        # Score for Puerto Rico relevance
        pr_keywords = ["puerto rico", "puerto rican", "boricua", "san juan", "pr", "🇵🇷"]
        if any(keyword in content_lower for keyword in pr_keywords):
            score += 0.4
        
        # Score for breaking news indicators
        breaking_keywords = ["breaking", "última hora", "urgente", "noticia", "anuncio"]
        if any(keyword in content_lower for keyword in breaking_keywords):
            score += 0.3
        
        # Score for engagement (if available)
        # This would require access to engagement metrics
        
        return min(score, 1.0)
    
    def _convert_to_news_item(self, parsed_tweet: ElNuevoDiaTweet) -> NewsItem:
        """Convert parsed tweet to NewsItem."""
        return NewsItem(
            headline=parsed_tweet.headline or parsed_tweet.content[:100] + "...",
            content=parsed_tweet.content,
            source="El Nuevo Día",
            topics=parsed_tweet.topics or [],
            relevance_score=parsed_tweet.relevance_score,
            published_at=parsed_tweet.created_at
        )
    
    async def clear_cache(self, cache_type: Optional[str] = None) -> bool:
        """
        Clear cache for the El Nuevo Día adapter.
        
        Args:
            cache_type: Specific cache type to clear ('tweets', 'trending_topics', 'user_info')
                        If None, clears all caches
                        
        Returns:
            True if successful, False otherwise
        """
        try:
            if cache_type:
                # Clear specific cache type
                pattern = f"elnuevodia:{cache_type}:*"
                await self.redis_client.delete(pattern)
                logger.info(f"Cleared cache for type: {cache_type}")
            else:
                # Clear all El Nuevo Día caches
                pattern = "elnuevodia:*"
                await self.redis_client.delete(pattern)
                logger.info("Cleared all El Nuevo Día caches")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check if El Nuevo Día news adapter is working."""
        try:
            # Try to get recent tweets as a health check
            tweets = await self.twitter_connector.get_user_tweets(
                username="ElNuevoDia",
                max_results=5  # Minimum required by Twitter API
            )
            return len(tweets) >= 0  # Success if we can connect
        except Exception as e:
            logger.error(f"El Nuevo Día health check failed: {str(e)}")
            return False
    
    async def get_provider_info(self) -> NewsProviderInfo:
        """Get information about the El Nuevo Día news provider."""
        return NewsProviderInfo(
            name="El Nuevo Día",
            type="twitter",
            description="News adapter for El Nuevo Día Twitter feed (@ElNuevoDia)",
            capabilities=[
                "news_discovery",
                "trending_topics",
                "puerto_rico_news",
                "real_time_updates"
            ],
            rate_limits={
                "tweets_per_request": 100,
                "requests_per_15min": 300
            },
            metadata={
                "twitter_username": "ElNuevoDia",
                "language": "es",
                "region": "Puerto Rico",
                "news_categories": list(self.topic_keywords.keys())
            }
        ) 