"""
Twitter Provider Port - Interface for Twitter API services.
This abstracts away the specific Twitter API implementation (tweepy, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TwitterPostType(str, Enum):
    """Types of Twitter posts."""
    TWEET = "tweet"
    REPLY = "reply"
    QUOTE_TWEET = "quote_tweet"
    THREAD = "thread"


class TwitterPostStatus(str, Enum):
    """Status of a Twitter post."""
    DRAFT = "draft"
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


class TwitterPost(BaseModel):
    """Twitter post data model."""
    id: Optional[str] = None
    content: str
    post_type: TwitterPostType = TwitterPostType.TWEET
    status: TwitterPostStatus = TwitterPostStatus.DRAFT
    character_id: str
    character_name: str
    
    # Twitter-specific fields
    reply_to_tweet_id: Optional[str] = None
    quote_tweet_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    posted_at: Optional[datetime] = None
    twitter_tweet_id: Optional[str] = None
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TwitterSearchResult(BaseModel):
    """Result from Twitter search."""
    tweet_id: str
    content: str
    author_username: str
    author_name: str
    created_at: datetime
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: float = 0.0
    puerto_rico_relevance: float = 0.0


class TwitterRateLimit(BaseModel):
    """Twitter API rate limit information."""
    endpoint: str
    limit: int
    remaining: int
    reset_time: datetime
    window_seconds: int = 900  # 15 minutes default


class TwitterPostResult(BaseModel):
    """Result of posting to Twitter."""
    success: bool
    twitter_tweet_id: Optional[str] = None
    post: TwitterPost
    rate_limit_info: Optional[TwitterRateLimit] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TwitterProviderPort(ABC):
    """
    Port (Interface) for Twitter API services.
    
    This allows us to swap between different Twitter API implementations
    without changing the core business logic.
    """
    
    @abstractmethod
    async def post_tweet(
        self,
        content: str,
        character_id: str,
        character_name: str,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> TwitterPostResult:
        """
        Post a tweet to Twitter.
        
        Args:
            content: Tweet content (max 280 characters)
            character_id: ID of the character posting
            character_name: Name of the character posting
            reply_to_tweet_id: ID of tweet to reply to
            quote_tweet_id: ID of tweet to quote
            thread_id: ID of thread this belongs to
        """
        pass
    
    @abstractmethod
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """
        Search for tweets matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            since_id: Return tweets after this ID
            until_id: Return tweets before this ID
        """
        pass
    
    @abstractmethod
    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 100,
        since_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        """
        Get tweets from a specific user.
        
        Args:
            username: Twitter username (without @)
            max_results: Maximum number of results to return
            since_id: Return tweets after this ID
        """
        pass
    
    @abstractmethod
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[TwitterSearchResult]:
        """Get a specific tweet by ID."""
        pass
    
    @abstractmethod
    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID."""
        pass
    
    @abstractmethod
    async def get_rate_limit_status(self, endpoint: str) -> Optional[TwitterRateLimit]:
        """Get current rate limit status for an endpoint."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if Twitter API is available."""
        pass
    
    @abstractmethod
    async def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate tweet content before posting.
        
        Returns:
            Dict with validation results including:
            - valid: bool
            - length: int
            - warnings: List[str]
            - errors: List[str]
        """
        pass 