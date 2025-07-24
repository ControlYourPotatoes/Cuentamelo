"""
Twitter Adapter - Implements TwitterProviderPort using TwitterConnector.
This is the "adapter" that connects our port to the external Twitter service.
"""
from typing import List, Dict, Any, Optional
import logging

from app.ports.twitter_provider import (
    TwitterProviderPort, TwitterPost, TwitterPostResult, TwitterSearchResult,
    TwitterRateLimit, TwitterPostType, TwitterPostStatus
)
from app.tools.twitter_connector import TwitterConnector

logger = logging.getLogger(__name__)


class TwitterAdapter(TwitterProviderPort):
    """
    Adapter that implements TwitterProviderPort using TwitterConnector.
    
    This demonstrates the Adapter pattern by:
    - Implementing the standard TwitterProviderPort interface
    - Translating between our domain models and Twitter's API
    - Handling Twitter-specific logic and error handling
    """
    
    def __init__(self, twitter_connector: Optional[TwitterConnector] = None):
        """
        Initialize with dependency injection.
        
        Args:
            twitter_connector: Injected Twitter connector (for testing/flexibility)
        """
        self.twitter_connector = twitter_connector or TwitterConnector()
    
    async def post_tweet(
        self,
        content: str,
        character_id: str,
        character_name: str,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> TwitterPostResult:
        """Post a tweet using Twitter connector with enhanced error handling."""
        try:
            # Add character-specific metadata
            enhanced_content = self._enhance_content_with_character_context(
                content, character_id, character_name
            )
            
            # Post using connector
            result = await self.twitter_connector.post_tweet(
                content=enhanced_content,
                character_id=character_id,
                character_name=character_name,
                reply_to_tweet_id=reply_to_tweet_id,
                quote_tweet_id=quote_tweet_id,
                thread_id=thread_id
            )
            
            # Add adapter-specific metadata
            if result.success:
                result.metadata.update({
                    "adapter": "twitter",
                    "character_id": character_id,
                    "content_enhanced": enhanced_content != content,
                    "thread_aware": thread_id is not None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter post_tweet: {str(e)}")
            # Return fallback result
            return TwitterPostResult(
                success=False,
                post=TwitterPost(
                    content=content,
                    character_id=character_id,
                    character_name=character_name,
                    status=TwitterPostStatus.FAILED
                ),
                error_message=f"Adapter error: {str(e)}",
                metadata={"adapter": "twitter", "error": str(e)}
            )
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """Search tweets using Twitter connector with Puerto Rico relevance filtering."""
        try:
            # Enhance query for Puerto Rico relevance
            enhanced_query = self._enhance_search_query(query)
            
            # Search using connector
            results = await self.twitter_connector.search_tweets(
                query=enhanced_query,
                max_results=max_results,
                since_id=since_id,
                until_id=until_id
            )
            
            # Filter and sort by Puerto Rico relevance
            filtered_results = self._filter_by_pr_relevance(results)
            
            logger.info(f"Twitter adapter found {len(filtered_results)} relevant tweets for query: {query}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter search_tweets: {str(e)}")
            return []
    
    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 100,
        since_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """Get user tweets using Twitter connector."""
        try:
            results = await self.twitter_connector.get_user_tweets(
                username=username,
                max_results=max_results,
                since_id=since_id
            )
            
            # Add adapter metadata
            for result in results:
                result.metadata = result.metadata or {}
                result.metadata.update({
                    "adapter": "twitter",
                    "source": "user_timeline"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter get_user_tweets: {str(e)}")
            return []
    
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[TwitterSearchResult]:
        """Get tweet by ID using Twitter connector."""
        try:
            result = await self.twitter_connector.get_tweet_by_id(tweet_id)
            
            if result:
                result.metadata = result.metadata or {}
                result.metadata.update({
                    "adapter": "twitter",
                    "source": "tweet_by_id"
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter get_tweet_by_id: {str(e)}")
            return None
    
    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete tweet using Twitter connector."""
        try:
            success = await self.twitter_connector.delete_tweet(tweet_id)
            
            if success:
                logger.info(f"Twitter adapter successfully deleted tweet: {tweet_id}")
            else:
                logger.warning(f"Twitter adapter failed to delete tweet: {tweet_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter delete_tweet: {str(e)}")
            return False
    
    async def get_rate_limit_status(self, endpoint: str) -> Optional[TwitterRateLimit]:
        """Get rate limit status using Twitter connector."""
        try:
            return await self.twitter_connector.get_rate_limit_status(endpoint)
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter get_rate_limit_status: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """Check Twitter API health using connector."""
        try:
            return await self.twitter_connector.health_check()
            
        except Exception as e:
            logger.error(f"Twitter adapter health check failed: {str(e)}")
            return False
    
    async def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content using Twitter connector with character-specific rules."""
        try:
            # Get base validation from connector
            validation = await self.twitter_connector.validate_content(content)
            
            # Add character-specific validation rules
            character_validation = self._validate_character_content(content)
            
            # Merge validation results
            validation["warnings"].extend(character_validation.get("warnings", []))
            validation["errors"].extend(character_validation.get("errors", []))
            validation["valid"] = validation["valid"] and len(character_validation.get("errors", [])) == 0
            
            # Add adapter metadata
            validation["adapter"] = "twitter"
            validation["character_validation"] = character_validation
            
            return validation
            
        except Exception as e:
            logger.error(f"Error in Twitter adapter validate_content: {str(e)}")
            return {
                "valid": False,
                "length": len(content),
                "warnings": [],
                "errors": [f"Validation error: {str(e)}"],
                "adapter": "twitter"
            }
    
    def _enhance_content_with_character_context(
        self,
        content: str,
        character_id: str,
        character_name: str
    ) -> str:
        """Enhance tweet content with character-specific context and signature."""
        
        # Add character signature
        signature = self._get_character_signature(character_id, character_name)
        
        # Calculate available space for content (280 - signature length - 1 space)
        max_content_length = 280 - len(signature) - 1
        
        # Truncate content if needed to make room for signature
        if len(content) > max_content_length:
            content = content[:max_content_length-3] + "..."
        
        # Add character-specific hashtags based on character type
        character_hashtags = self._get_character_hashtags(character_id)
        
        # Add Puerto Rico hashtags if not present
        pr_hashtags = self._get_pr_hashtags(content)
        
        # Combine hashtags
        all_hashtags = character_hashtags + pr_hashtags
        
        # Calculate total length with hashtags
        hashtag_text = " ".join(all_hashtags) if all_hashtags else ""
        total_length = len(content) + len(signature) + 1 + len(hashtag_text) + (1 if hashtag_text else 0)
        
        # Add hashtags if there's space and they're not already present
        if hashtag_text and total_length <= 280 and hashtag_text not in content:
            content += f" {hashtag_text}"
        
        # Add signature at the end
        content += f" {signature}"
        
        return content
    
    def _enhance_search_query(self, query: str) -> str:
        """Enhance search query for better Puerto Rico relevance."""
        
        # Add Puerto Rico context if not present
        pr_indicators = ["puerto rico", "boricua", "pr", "🇵🇷"]
        has_pr_context = any(indicator in query.lower() for indicator in pr_indicators)
        
        if not has_pr_context:
            # Add Puerto Rico context
            enhanced_query = f"{query} (Puerto Rico OR boricua OR PR)"
        else:
            enhanced_query = query
        
        return enhanced_query
    
    def _filter_by_pr_relevance(self, results: List[TwitterSearchResult]) -> List[TwitterSearchResult]:
        """Filter and sort results by Puerto Rico relevance."""
        
        # Sort by Puerto Rico relevance (highest first)
        sorted_results = sorted(
            results,
            key=lambda x: x.puerto_rico_relevance,
            reverse=True
        )
        
        # Filter out very low relevance results
        filtered_results = [
            result for result in sorted_results
            if result.puerto_rico_relevance > 0.1 or result.relevance_score > 0.5
        ]
        
        return filtered_results
    
    def _validate_character_content(self, content: str) -> Dict[str, Any]:
        """Validate content for character-specific rules."""
        warnings = []
        errors = []
        
        # Check for character-specific requirements
        if len(content) < 10:
            warnings.append("Tweet is very short - may not be engaging")
        
        # Check for appropriate emoji usage
        emoji_count = sum(1 for char in content if ord(char) > 127 and len(char.encode('utf-8')) > 1)
        if emoji_count > 5:
            warnings.append("Many emojis detected - may affect readability")
        
        # Check for Puerto Rico context
        pr_indicators = ["puerto rico", "boricua", "pr", "🇵🇷", "san juan", "coquí"]
        has_pr_context = any(indicator in content.lower() for indicator in pr_indicators)
        
        if not has_pr_context:
            warnings.append("No Puerto Rico context detected")
        
        return {
            "warnings": warnings,
            "errors": errors
        }
    
    def _get_character_hashtags(self, character_id: str) -> List[str]:
        """Get character-specific hashtags."""
        character_hashtags = {
            "jovani_vazquez": ["#JovaniVazquez", "#PRInfluencer", "#BoricuaVibes"],
            "politico_boricua": ["#PoliticoBoricua", "#PRPolitics", "#PuertoRico"],
            "ciudadano_boricua": ["#CiudadanoBoricua", "#VidaBoricua", "#PRDaily"],
            "historiador_cultural": ["#HistoriaPR", "#CulturaBoricua", "#PatrimonioPR"]
        }
        
        return character_hashtags.get(character_id, ["#PuertoRico"])
    
    def _get_pr_hashtags(self, content: str) -> List[str]:
        """Get Puerto Rico hashtags based on content."""
        hashtags = []
        
        # Add general Puerto Rico hashtag if not present
        if "🇵🇷" not in content and "puerto rico" not in content.lower():
            hashtags.append("#PuertoRico")
        
        # Add specific hashtags based on content
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["música", "music", "reggaeton", "salsa"]):
            hashtags.append("#MusicaPR")
        
        if any(word in content_lower for word in ["comida", "food", "mofongo", "lechón"]):
            hashtags.append("#ComidaBoricua")
        
        if any(word in content_lower for word in ["cultura", "culture", "tradición"]):
            hashtags.append("#CulturaBoricua")
        
        return hashtags
    
    def _get_character_signature(self, character_id: str, character_name: str) -> str:
        """Get character-specific signature for tweets."""
        signatures = {
            "jovani_vazquez": "🔥 Jovani",
            "politico_boricua": "🇵🇷 Político",
            "ciudadano_boricua": "💪 Ciudadano",
            "historiador_cultural": "📚 Historiador"
        }
        
        # Return character-specific signature or fallback
        return signatures.get(character_id, f"🤖 {character_name}") 