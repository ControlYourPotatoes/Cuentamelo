#!/usr/bin/env python3
"""
Test script using simulated news provider to avoid Twitter API rate limits.
"""
import asyncio
import logging
import time
from app.services.dependency_container import DependencyContainer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_without_rate_limits():
    """Test the news system using simulated provider to avoid rate limits."""
    print("🧪 Testing News System (No Rate Limits)")
    print("=" * 50)
    
    try:
        # Configure container to use simulated news provider
        container = DependencyContainer()
        container.config["news_provider"] = "simulated"
        
        # Get the news provider
        news_provider = container.get_news_provider()
        print(f"✅ Using news provider: {type(news_provider).__name__}")
        
        # Test 1: Provider info
        print("\n📋 Test 1: Provider Info")
        print("-" * 30)
        provider_info = await news_provider.get_provider_info()
        print(f"✅ Provider: {provider_info.name}")
        print(f"✅ Type: {provider_info.type}")
        print(f"✅ Capabilities: {provider_info.capabilities}")
        
        # Test 2: Health check
        print("\n🏥 Test 2: Health Check")
        print("-" * 30)
        health = await news_provider.health_check()
        print(f"✅ Health check result: {health}")
        
        # Test 3: News discovery (should be instant)
        print("\n📰 Test 3: News Discovery")
        print("-" * 30)
        start_time = time.time()
        news_items = await news_provider.discover_latest_news(max_results=5)
        discovery_time = time.time() - start_time
        print(f"✅ News discovery completed in {discovery_time:.2f}s")
        print(f"✅ Found {len(news_items)} news items")
        
        # Show some news items
        for i, item in enumerate(news_items[:3], 1):
            print(f"   {i}. {item.headline[:60]}...")
            print(f"      Topics: {item.topics}")
            print(f"      Relevance: {item.relevance_score:.2f}")
        
        # Test 4: Trending topics
        print("\n📊 Test 4: Trending Topics")
        print("-" * 30)
        start_time = time.time()
        trending_topics = await news_provider.get_trending_topics(max_topics=5)
        topics_time = time.time() - start_time
        print(f"✅ Trending topics completed in {topics_time:.2f}s")
        print(f"✅ Found {len(trending_topics)} trending topics")
        
        # Show trending topics
        for i, topic in enumerate(trending_topics[:3], 1):
            print(f"   {i}. {topic.term} (count: {topic.count}, relevance: {topic.relevance:.2f})")
        
        # Test 5: News ingestion
        print("\n📝 Test 5: News Ingestion")
        print("-" * 30)
        custom_news = await news_provider.ingest_news_item(
            headline="Test News Item",
            content="This is a test news item for testing purposes.",
            source="Test Source",
            tags=["test", "demo"],
            relevance_score=0.8
        )
        print(f"✅ Ingested custom news item: {custom_news.headline}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Benefits of simulated provider:")
        print("   • No API rate limits")
        print("   • Instant responses")
        print("   • Perfect for development and testing")
        print("   • Consistent demo data")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(test_without_rate_limits()) 