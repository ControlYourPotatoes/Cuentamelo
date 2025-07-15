"""
Mock Twitter Provider for testing.
"""
from app.ports.twitter_provider import TwitterProvider

class MockTwitterProvider(TwitterProvider):
    async def post_tweet(self, message):
        return {"tweet_id": "mock123", "status": "posted", "message": message} 