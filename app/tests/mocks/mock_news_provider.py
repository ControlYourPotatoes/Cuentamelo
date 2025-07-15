"""
Mock News Provider for testing.
"""
from app.ports.news_provider import NewsProviderPort

class MockNewsProvider(NewsProviderPort):
    async def get_latest_news(self):
        return [{"title": "Mock News", "content": "This is a mock news item."}] 