"""
Mock Twitter Provider for testing.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.ports.twitter_provider import TwitterProviderPort, TwitterPostResult, TwitterSearchResult, TwitterRateLimit, TwitterPost


class MockTwitterProvider(TwitterProviderPort):
    async def post_tweet(
        self,
        content: str,
        character_id: str,
        character_name: str,
        reply_to_tweet_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> TwitterPostResult:
        return TwitterPostResult(
            success=True,
            twitter_tweet_id="mock_tweet_123",
            post=TwitterPost(
                id="mock_post_123",
                content=content,
                character_id=character_id,
                character_name=character_name,
                reply_to_tweet_id=reply_to_tweet_id,
                quote_tweet_id=quote_tweet_id,
                thread_id=thread_id,
                status="posted",
                posted_at=datetime.now()
            ),
            metadata={"mock": True}
        )
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        return [
            TwitterSearchResult(
                tweet_id="mock_search_123",
                content=f"Mock tweet about {query}",
                author_username="mock_user",
                author_name="Mock User",
                created_at=datetime.now(),
                relevance_score=0.8,
                puerto_rico_relevance=0.6
            )
        ]
    
    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 100,
        since_id: Optional[str] = None
    ) -> List[TwitterSearchResult]:
        return [
            TwitterSearchResult(
                tweet_id="mock_user_123",
                content=f"Mock tweet from {username}",
                author_username=username,
                author_name=f"Mock {username}",
                created_at=datetime.now(),
                relevance_score=0.7,
                puerto_rico_relevance=0.5
            )
        ]
    
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[TwitterSearchResult]:
        return TwitterSearchResult(
            tweet_id=tweet_id,
            content="Mock tweet content",
            author_username="mock_user",
            author_name="Mock User",
            created_at=datetime.now(),
            relevance_score=0.8,
            puerto_rico_relevance=0.6
        )
    
    async def delete_tweet(self, tweet_id: str) -> bool:
        return True
    
    async def get_rate_limit_status(self, endpoint: str) -> Optional[TwitterRateLimit]:
        return TwitterRateLimit(
            endpoint=endpoint,
            limit=100,
            remaining=95,
            reset_time=datetime.now()
        )
    
    async def health_check(self) -> bool:
        return True
    
    async def validate_content(self, content: str) -> Dict[str, Any]:
        return {
            "valid": True,
            "length": len(content),
            "warnings": [],
            "errors": []
        } 