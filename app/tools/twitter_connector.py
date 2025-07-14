"""
Twitter Connector Tool - Implements TwitterProviderPort using tweepy.
Provides Twitter API integration for the Puerto Rican AI character platform.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re

import tweepy
from tweepy import Client, StreamingClient, StreamRule
from tweepy.errors import TweepyException, TooManyRequests, Unauthorized

from app.ports.twitter_provider import (
    TwitterProviderPort, TwitterPost, TwitterPostResult, TwitterSearchResult,
    TwitterRateLimit, TwitterPostType, TwitterPostStatus
)
from app.config import get_settings
from app.utils.event_decorators import emit_post_published

logger = logging.getLogger(__name__)
settings = get_settings()


class TwitterConnector(TwitterProviderPort):
    """
    Twitter API connector using tweepy library.
    
    Implements the TwitterProviderPort interface with:
    - Tweet posting and management
    - Search functionality
    - Rate limiting handling
    - Error management
    - Content validation
    """
    
    def __init__(
        self,
        bearer_token: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """
        Initialize Twitter connector with API credentials.
        
        Args:
            bearer_token: Twitter API v2 bearer token
            consumer_key: Twitter API consumer key
            consumer_secret: Twitter API consumer secret
            access_token: Twitter API access token
            access_token_secret: Twitter API access token secret
        """
        # Use environment variables if not provided
        self.bearer_token = bearer_token or settings.TWITTER_BEARER_TOKEN
        self.consumer_key = consumer_key or settings.TWITTER_API_KEY
        self.consumer_secret = consumer_secret or settings.TWITTER_API_SECRET
        self.access_token = access_token or settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = access_token_secret or settings.TWITTER_ACCESS_TOKEN_SECRET
        
        # Initialize tweepy client
        self.client = Client(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, TwitterRateLimit] = {}
        self.last_api_call: Dict[str, datetime] = {}
        
        logger.info("Twitter connector initialized")
    
    @emit_post_published()
    async def post_tweet(
        self,
        content: str,
        character_id: str,
        character_name: str,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> TwitterPostResult:
        """Post a tweet to Twitter."""
        try:
            # Validate content first
            validation = await self.validate_content(content)
            if not validation["valid"]:
                return TwitterPostResult(
                    success=False,
                    post=TwitterPost(
                        content=content,
                        character_id=character_id,
                        character_name=character_name,
                        status=TwitterPostStatus.FAILED
                    ),
                    error_message=f"Content validation failed: {validation['errors']}"
                )
            
            # Create post object
            post = TwitterPost(
                content=content,
                character_id=character_id,
                character_name=character_name,
                post_type=TwitterPostType.REPLY if reply_to_tweet_id else TwitterPostType.TWEET,
                reply_to_tweet_id=reply_to_tweet_id,
                quote_tweet_id=quote_tweet_id,
                thread_id=thread_id,
                status=TwitterPostStatus.PENDING
            )
            
            # Post to Twitter
            response = await asyncio.to_thread(
                self.client.create_tweet,
                text=content,
                in_reply_to_tweet_id=reply_to_tweet_id,
                quote_tweet_id=quote_tweet_id
            )
            
            # Update post with Twitter response
            post.status = TwitterPostStatus.POSTED
            post.twitter_tweet_id = response.data["id"]
            post.posted_at = datetime.now(timezone.utc)
            
            # Update rate limit info
            rate_limit = await self.get_rate_limit_status("tweets")
            
            logger.info(f"Successfully posted tweet for {character_name}: {post.twitter_tweet_id}")
            
            return TwitterPostResult(
                success=True,
                twitter_tweet_id=post.twitter_tweet_id,
                post=post,
                rate_limit_info=rate_limit
            )
            
        except TooManyRequests as e:
            logger.warning(f"Rate limited when posting tweet for {character_name}: {str(e)}")
            post.status = TwitterPostStatus.RATE_LIMITED
            return TwitterPostResult(
                success=False,
                post=post,
                error_message="Rate limited by Twitter API",
                rate_limit_info=await self.get_rate_limit_status("tweets")
            )
            
        except Unauthorized as e:
            logger.error(f"Unauthorized when posting tweet for {character_name}: {str(e)}")
            post.status = TwitterPostStatus.FAILED
            return TwitterPostResult(
                success=False,
                post=post,
                error_message="Twitter API authorization failed"
            )
            
        except TweepyException as e:
            logger.error(f"Twitter API error when posting tweet for {character_name}: {str(e)}")
            post.status = TwitterPostStatus.FAILED
            return TwitterPostResult(
                success=False,
                post=post,
                error_message=f"Twitter API error: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error when posting tweet for {character_name}: {str(e)}")
            post.status = TwitterPostStatus.FAILED
            return TwitterPostResult(
                success=False,
                post=post,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """Search for tweets matching the query."""
        try:
            # Build search parameters
            search_params = {
                "query": query,
                "max_results": max(5, min(max_results, 100)),  # Twitter API requires 5-100
                "tweet_fields": ["created_at", "public_metrics", "author_id"],
                "user_fields": ["username", "name"],
                "expansions": ["author_id"]
            }
            
            if since_id:
                search_params["since_id"] = since_id
            if until_id:
                search_params["until_id"] = until_id
            
            # Execute search
            response = await asyncio.to_thread(
                self.client.search_recent_tweets,
                **search_params
            )
            
            # Process results
            results = []
            if response.data:
                # Create user lookup
                users = {user.id: user for user in response.includes.get("users", [])}
                
                for tweet in response.data:
                    user = users.get(tweet.author_id)
                    if user:
                        # Calculate relevance scores
                        relevance_score = self._calculate_relevance_score(tweet.text, query)
                        pr_relevance = self._calculate_pr_relevance(tweet.text)
                        
                        result = TwitterSearchResult(
                            tweet_id=str(tweet.id),  # Convert to string
                            content=tweet.text,
                            author_username=user.username,
                            author_name=user.name,
                            created_at=tweet.created_at,
                            engagement_metrics=tweet.public_metrics,
                            relevance_score=relevance_score,
                            puerto_rico_relevance=pr_relevance
                        )
                        results.append(result)
            
            logger.info(f"Found {len(results)} tweets for query: {query}")
            return results
            
        except TweepyException as e:
            logger.error(f"Twitter API error when searching tweets: {str(e)}")
            return []
    
    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 100,
        since_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """Get tweets from a specific user."""
        try:
            # Get user ID first
            user_response = await asyncio.to_thread(
                self.client.get_user,
                username=username
            )
            
            if not user_response.data:
                logger.warning(f"User not found: {username}")
                return []
            
            user_id = user_response.data.id
            
            # Get user tweets
            params = {
                "id": user_id,
                "max_results": max(5, min(max_results, 100)),  # Twitter API requires 5-100
                "tweet_fields": ["created_at", "public_metrics"],
                "exclude": ["retweets", "replies"]
            }
            
            if since_id:
                params["since_id"] = since_id
            
            response = await asyncio.to_thread(
                self.client.get_users_tweets,
                **params
            )
            
            # Process results
            results = []
            if response.data:
                for tweet in response.data:
                    result = TwitterSearchResult(
                        tweet_id=str(tweet.id),  # Convert to string
                        content=tweet.text,
                        author_username=username,
                        author_name=user_response.data.name,
                        created_at=tweet.created_at,
                        engagement_metrics=tweet.public_metrics,
                        puerto_rico_relevance=self._calculate_pr_relevance(tweet.text)
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} tweets from user: {username}")
            return results
            
        except TweepyException as e:
            logger.error(f"Twitter API error when getting user tweets: {str(e)}")
            return []
    
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[TwitterSearchResult]:
        """Get a specific tweet by ID."""
        try:
            response = await asyncio.to_thread(
                self.client.get_tweet,
                id=tweet_id,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                user_fields=["username", "name"],
                expansions=["author_id"]
            )
            
            if not response.data:
                return None
            
            tweet = response.data
            user = response.includes.get("users", [{}])[0] if response.includes.get("users") else {}
            
            return TwitterSearchResult(
                tweet_id=str(tweet.id),  # Convert to string
                content=tweet.text,
                author_username=user.get("username", ""),
                author_name=user.get("name", ""),
                created_at=tweet.created_at,
                engagement_metrics=tweet.public_metrics,
                puerto_rico_relevance=self._calculate_pr_relevance(tweet.text)
            )
            
        except TweepyException as e:
            logger.error(f"Twitter API error when getting tweet {tweet_id}: {str(e)}")
            return None
    
    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID."""
        try:
            await asyncio.to_thread(self.client.delete_tweet, id=tweet_id)
            logger.info(f"Successfully deleted tweet: {tweet_id}")
            return True
            
        except TweepyException as e:
            logger.error(f"Twitter API error when deleting tweet {tweet_id}: {str(e)}")
            return False
    
    async def get_rate_limit_status(self, endpoint: str) -> Optional[TwitterRateLimit]:
        """Get current rate limit status for an endpoint."""
        try:
            # Note: Twitter API v2 doesn't provide rate limit info in response headers
            # This is a simplified implementation
            return TwitterRateLimit(
                endpoint=endpoint,
                limit=300,  # Default Twitter API v2 limits
                remaining=250,  # Approximate
                reset_time=datetime.now(timezone.utc),
                window_seconds=900
            )
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """Check if Twitter API is available."""
        try:
            # Try to get current user info as a health check
            await asyncio.to_thread(self.client.get_me)
            return True
            
        except Exception as e:
            logger.error(f"Twitter API health check failed: {str(e)}")
            return False
    
    async def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate tweet content before posting.
        
        Returns:
            Dict with validation results
        """
        warnings = []
        errors = []
        
        # Check length
        if len(content) > 280:
            errors.append(f"Tweet too long: {len(content)} characters (max 280)")
        elif len(content) > 250:
            warnings.append(f"Tweet is long: {len(content)} characters")
        
        # Check for empty content
        if not content.strip():
            errors.append("Tweet content cannot be empty")
        
        # Check for common issues
        if content.count("@") > 10:
            warnings.append("Many mentions detected")
        
        if content.count("#") > 10:
            warnings.append("Many hashtags detected")
        
        # Check for potentially problematic content
        problematic_patterns = [
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            r"RT @",
            r"Follow me",
            r"Click here"
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Potentially problematic content detected: {pattern}")
        
        return {
            "valid": len(errors) == 0,
            "length": len(content),
            "warnings": warnings,
            "errors": errors
        }
    
    def _calculate_relevance_score(self, tweet_text: str, query: str) -> float:
        """Calculate relevance score between tweet and query."""
        tweet_lower = tweet_text.lower()
        query_lower = query.lower()
        
        # Simple keyword matching
        query_words = set(query_lower.split())
        tweet_words = set(tweet_lower.split())
        
        if not query_words:
            return 0.0
        
        matches = len(query_words.intersection(tweet_words))
        return min(matches / len(query_words), 1.0)
    
    def _calculate_pr_relevance(self, tweet_text: str) -> float:
        """Calculate Puerto Rico relevance score for a tweet."""
        tweet_lower = tweet_text.lower()
        
        # Puerto Rico related keywords
        pr_keywords = [
            "puerto rico", "puerto rican", "boricua", "boricuas",
            "san juan", "bayamón", "carolina", "caguas", "ponce",
            "mayagüez", "arecibo", "aguadilla", "fajardo",
            "viejo san juan", "el yunque", "cayo", "isla",
            "coquí", "salsa", "reggaeton", "merengue", "bomba",
            "plena", "piragua", "lechón", "mofongo", "arroz con gandules",
            "🇵🇷", "pr", "puerto rico", "puertorriqueño"
        ]
        
        matches = sum(1 for keyword in pr_keywords if keyword in tweet_lower)
        return min(matches / 5.0, 1.0)  # Normalize to 0-1


async def get_twitter_connector() -> TwitterConnector:
    """Factory function to get Twitter connector instance."""
    return TwitterConnector() 