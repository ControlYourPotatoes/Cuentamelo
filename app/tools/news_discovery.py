"""
Twitter-based news discovery tool with smart caching.
Discovers news from Puerto Rican Twitter accounts and caches results to avoid rate limits.
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import hashlib

from app.tools.twitter_connector import TwitterConnector
from app.models.conversation import NewsItem
from app.services.redis_client import RedisClient

logger = logging.getLogger(__name__)


@dataclass
class NewsSource:
    """Configuration for a news source account."""
    username: str
    display_name: str
    category: str  # 'news', 'politics', 'culture', 'entertainment'
    relevance_score: float  # 0.0 to 1.0
    is_active: bool = True


@dataclass
class CachedNewsItem:
    """Cached news item with metadata."""
    tweet_id: str
    username: str
    content: str
    created_at: str
    hashtags: List[str]
    mentions: List[str]
    relevance_score: float
    category: str
    cached_at: str
    processed: bool = False


class NewsDiscoveryService:
    """
    Service for discovering news from Twitter accounts with smart caching.
    
    Features:
    - Monitors Puerto Rican news accounts
    - Smart caching to avoid rate limits
    - Relevance scoring for news items
    - Category-based filtering
    """
    
    def __init__(self, twitter_connector: TwitterConnector, redis_client: RedisClient):
        self.twitter = twitter_connector
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour cache
        
        # Puerto Rican news sources to monitor
        self.news_sources = [
            NewsSource("ElNuevoDia", "El Nuevo Día", "news", 0.9),
            NewsSource("PrimeraHora", "Primera Hora", "news", 0.9),
            NewsSource("MetroPR", "Metro Puerto Rico", "news", 0.8),
            NewsSource("NotiCel", "NotiCel", "news", 0.8),
            NewsSource("WIPR", "WIPR TV", "news", 0.7),
            NewsSource("RadioIsla", "Radio Isla", "news", 0.7),
            NewsSource("TelemundoPR", "Telemundo Puerto Rico", "news", 0.8),
            NewsSource("WAPA_TV", "WAPA TV", "news", 0.8),
            NewsSource("GobiernoPR", "Gobierno de Puerto Rico", "politics", 0.9),
            NewsSource("FortalezaPR", "La Fortaleza", "politics", 0.9),
            NewsSource("SenadoPR", "Senado de Puerto Rico", "politics", 0.8),
            NewsSource("CamaraRepPR", "Cámara de Representantes", "politics", 0.8),
            NewsSource("BadBunnyPR", "Bad Bunny", "entertainment", 0.95),
            NewsSource("Residente", "Residente", "entertainment", 0.9),
            NewsSource("Calle13", "Calle 13", "entertainment", 0.9),
            NewsSource("TurismoPR", "Puerto Rico Tourism", "culture", 0.8),
            NewsSource("MuseoPR", "Museo de Arte de Puerto Rico", "culture", 0.7),
        ]
        
        # Keywords that indicate news content
        self.news_keywords = {
            "breaking": 0.9,
            "última hora": 0.9,
            "breaking news": 0.9,
            "noticia": 0.8,
            "anuncio": 0.8,
            "declaración": 0.8,
            "comunicado": 0.8,
            "informe": 0.7,
            "reporte": 0.7,
            "actualización": 0.7,
            "desarrollo": 0.7,
            "confirmado": 0.8,
            "oficial": 0.8,
            "gobierno": 0.8,
            "política": 0.8,
            "economía": 0.8,
            "turismo": 0.7,
            "cultura": 0.7,
            "entretenimiento": 0.7,
            "música": 0.7,
            "deportes": 0.7,
        }
        
        # Hashtags that indicate Puerto Rican relevance
        self.pr_hashtags = {
            "#PuertoRico": 0.9,
            "#PR": 0.8,
            "#Boricua": 0.8,
            "#Borinquen": 0.8,
            "#SanJuan": 0.7,
            "#Ponce": 0.7,
            "#Mayaguez": 0.7,
            "#Arecibo": 0.7,
            "#Bayamon": 0.7,
            "#Caguas": 0.7,
            "#Carolina": 0.7,
            "#Guaynabo": 0.7,
            "#Humacao": 0.7,
            "#Levittown": 0.7,
            "#Manati": 0.7,
            "#VegaBaja": 0.7,
            "#Yauco": 0.7,
        }
    
    async def discover_latest_news(self, max_results: int = 10) -> List[NewsItem]:
        """
        Discover latest news from monitored Twitter accounts.
        
        Args:
            max_results: Maximum number of news items to return
            
        Returns:
            List of NewsItem objects
        """
        try:
            logger.info(f"Discovering latest news from {len(self.news_sources)} sources")
            
            # Check cache first
            cached_news = await self._get_cached_news()
            if cached_news:
                logger.info(f"Returning {len(cached_news)} cached news items")
                return cached_news[:max_results]
            
            # Fetch fresh news from Twitter
            fresh_news = await self._fetch_fresh_news()
            
            # Cache the results
            await self._cache_news(fresh_news)
            
            logger.info(f"Discovered {len(fresh_news)} fresh news items")
            return fresh_news[:max_results]
            
        except Exception as e:
            logger.error(f"Error discovering news: {str(e)}")
            # Return cached news as fallback
            cached_news = await self._get_cached_news()
            return cached_news[:max_results] if cached_news else []
    
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
                logger.error(f"Error fetching tweets from {source.username}: {str(e)}")
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
                logger.warning(f"User {username} not found")
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
            logger.error(f"Error fetching tweets from {username}: {str(e)}")
            return []
    
    async def _tweet_to_news_item(self, tweet: Dict, source: NewsSource) -> Optional[NewsItem]:
        """Convert a tweet to a NewsItem if it's news-worthy."""
        try:
            content = tweet.get("text", "")
            
            # Skip if content is too short or doesn't seem like news
            if len(content) < 20:
                return None
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content, source)
            
            # Skip if relevance is too low
            if relevance_score < 0.3:
                return None
            
            # Extract hashtags and mentions
            hashtags = self._extract_hashtags(content)
            mentions = self._extract_mentions(content)
            
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
            logger.error(f"Error converting tweet to news item: {str(e)}")
            return None
    
    def _calculate_relevance_score(self, content: str, source: NewsSource) -> float:
        """Calculate relevance score for a tweet."""
        content_lower = content.lower()
        score = source.relevance_score * 0.5  # Base score from source
        
        # Add points for news keywords
        for keyword, weight in self.news_keywords.items():
            if keyword.lower() in content_lower:
                score += weight * 0.3
        
        # Add points for Puerto Rican hashtags
        for hashtag, weight in self.pr_hashtags.items():
            if hashtag.lower() in content_lower:
                score += weight * 0.4
        
        # Add points for content length (longer content tends to be more informative)
        if len(content) > 100:
            score += 0.1
        elif len(content) > 50:
            score += 0.05
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content."""
        import re
        hashtags = re.findall(r'#\w+', content)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract mentions from content."""
        import re
        mentions = re.findall(r'@\w+', content)
        return [mention.lower() for mention in mentions]
    
    def _generate_headline(self, content: str, source: NewsSource) -> str:
        """Generate a headline from tweet content."""
        # Remove hashtags and mentions for cleaner headline
        import re
        clean_content = re.sub(r'#\w+', '', content)
        clean_content = re.sub(r'@\w+', '', clean_content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Truncate if too long
        if len(clean_content) > 100:
            clean_content = clean_content[:97] + "..."
        
        return clean_content
    
    async def _cache_news(self, news_items: List[NewsItem]):
        """Cache news items in Redis."""
        try:
            cache_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "news_items": [asdict(item) for item in news_items]
            }
            
            await self.redis.set(
                "news_discovery_cache",
                json.dumps(cache_data),
                ex=self.cache_ttl
            )
            
            logger.info(f"Cached {len(news_items)} news items")
            
        except Exception as e:
            logger.error(f"Error caching news: {str(e)}")
    
    async def _get_cached_news(self) -> List[NewsItem]:
        """Get cached news items from Redis."""
        try:
            cached_data = await self.redis.get("news_discovery_cache")
            if not cached_data:
                return []
            
            data = json.loads(cached_data)
            news_items = []
            
            for item_data in data.get("news_items", []):
                try:
                    news_item = NewsItem(**item_data)
                    news_items.append(news_item)
                except Exception as e:
                    logger.error(f"Error parsing cached news item: {str(e)}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting cached news: {str(e)}")
            return []
    
    async def get_trending_topics(self) -> List[Dict]:
        """Get trending topics from discovered news."""
        try:
            news_items = await self.discover_latest_news(max_results=20)
            
            # Extract topics from news items
            topics = {}
            for item in news_items:
                # Extract key terms from content
                terms = self._extract_key_terms(item.content)
                
                for term in terms:
                    if term in topics:
                        topics[term]["count"] += 1
                        topics[term]["relevance"] = max(topics[term]["relevance"], item.relevance_score)
                    else:
                        topics[term] = {
                            "term": term,
                            "count": 1,
                            "relevance": item.relevance_score,
                            "category": self._categorize_term(term)
                        }
            
            # Sort by count and relevance
            trending = sorted(
                topics.values(),
                key=lambda x: (x["count"], x["relevance"]),
                reverse=True
            )
            
            return trending[:10]  # Top 10 trending topics
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return []
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from content."""
        import re
        
        # Remove URLs, hashtags, mentions
        clean_content = re.sub(r'http\S+', '', content)
        clean_content = re.sub(r'#\w+', '', clean_content)
        clean_content = re.sub(r'@\w+', '', clean_content)
        
        # Extract words (Spanish and English)
        words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', clean_content.lower())
        
        # Filter out common words
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da',
            'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero',
            'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde',
            'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese',
            'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo',
            'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada',
            'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros',
            'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros',
            'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas',
            'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras',
            'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás',
            'está', 'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis',
            'estén', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán',
            'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba',
            'estabas', 'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo',
            'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras',
            'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses',
            'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada',
            'estados', 'estadas', 'estad', 'he', 'has', 'ha', 'hemos', 'habéis', 'han',
            'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá',
            'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais',
            'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube',
            'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
            'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos',
            'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
            'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis',
            'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería',
            'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais',
            'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera',
            'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos',
            'fueseis', 'fuesen', 'sintiendo', 'sentido', 'sentida', 'sentidos', 'sentidas',
            'siente', 'sentid', 'tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen',
            'tenga', 'tengas', 'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás',
            'tendrá', 'tendremos', 'tendréis', 'tendrán', 'tendría', 'tendrías',
            'tendríamos', 'tendríais', 'tendrían', 'tenía', 'tenías', 'teníamos',
            'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis',
            'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran',
            'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo',
            'tenido', 'tenida', 'tenidos', 'tenidas', 'tened', 'the', 'be', 'to', 'of',
            'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
            'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would',
            'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just',
            'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some',
            'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only',
            'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two',
            'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want',
            'because', 'any', 'these', 'give', 'day', 'most', 'us'
        }
        
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms[:10]  # Return top 10 terms
    
    def _categorize_term(self, term: str) -> str:
        """Categorize a term based on content."""
        term_lower = term.lower()
        
        # Politics
        if any(pol in term_lower for pol in ['gobierno', 'política', 'senado', 'cámara', 'gobernador']):
            return 'politics'
        
        # Entertainment
        if any(ent in term_lower for ent in ['música', 'artista', 'concierto', 'película', 'teatro']):
            return 'entertainment'
        
        # Culture
        if any(cul in term_lower for cul in ['cultura', 'arte', 'museo', 'festival', 'tradición']):
            return 'culture'
        
        # Economy
        if any(eco in term_lower for eco in ['economía', 'negocio', 'turismo', 'comercio']):
            return 'economy'
        
        # Sports
        if any(sport in term_lower for sport in ['deporte', 'fútbol', 'béisbol', 'baloncesto']):
            return 'sports'
        
        return 'general' 