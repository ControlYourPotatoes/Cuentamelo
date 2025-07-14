#!/usr/bin/env python3
"""
Simple test script for El Nuevo Día news discovery.
This script tests just the news discovery functionality without the full workflow.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.dependency_container import DependencyContainer


async def test_news_discovery():
    """Test discovering news from El Nuevo Día."""
    print("📰 Testing El Nuevo Día News Discovery")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Get news provider
    news_provider = container.get_news_provider()
    print("🔍 Discovering latest news from @ElNuevoDia...")
    
    try:
        # Test news discovery
        news_items = await news_provider.discover_latest_news(max_results=10)
        
        if not news_items:
            print("❌ No news items found from El Nuevo Día!")
            print("This could mean:")
            print("- No recent news tweets")
            print("- Twitter API rate limits")
            print("- Network connectivity issues")
            return
        
        print(f"✅ Found {len(news_items)} news items from El Nuevo Día")
        print()
        
        # Display news items
        for i, news_item in enumerate(news_items, 1):
            print(f"📰 News Item {i}:")
            print(f"   Headline: {news_item.headline}")
            print(f"   Content: {news_item.content[:150]}...")
            print(f"   Source: {news_item.source}")
            print(f"   Topics: {', '.join(news_item.topics) if news_item.topics else 'None'}")
            print(f"   Relevance Score: {news_item.relevance_score:.2f}")
            print(f"   Published: {news_item.published_at}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Error discovering news: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_trending_topics():
    """Test trending topics discovery."""
    print("\n🔥 Testing El Nuevo Día Trending Topics Discovery")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Get news provider
    news_provider = container.get_news_provider()
    print("🔍 Getting trending topics from @ElNuevoDia...")
    
    try:
        # Test trending topics
        trending_topics = await news_provider.get_trending_topics(max_topics=10)
        
        if not trending_topics:
            print("❌ No trending topics found!")
            return
        
        print(f"✅ Found {len(trending_topics)} trending topics")
        print()
        
        # Display trending topics
        for i, topic in enumerate(trending_topics, 1):
            print(f"🔥 Trending Topic {i}:")
            print(f"   Term: {topic.term}")
            print(f"   Count: {topic.count}")
            print(f"   Relevance: {topic.relevance:.2f}")
            print(f"   Category: {topic.category}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error getting trending topics: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_health_check():
    """Test the health check."""
    print("\n🏥 Testing El Nuevo Día Health Check")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Get news provider
    news_provider = container.get_news_provider()
    
    try:
        # Test health check
        is_healthy = await news_provider.health_check()
        
        if is_healthy:
            print("✅ El Nuevo Día news adapter is healthy!")
            print("✅ Twitter API connection is working")
            print("✅ Can access @ElNuevoDia tweets")
        else:
            print("❌ El Nuevo Día news adapter health check failed!")
            print("This could indicate:")
            print("- Twitter API authentication issues")
            print("- Rate limiting")
            print("- Network connectivity problems")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all discovery tests."""
    print("📰 El Nuevo Día News Discovery Test")
    print("=" * 60)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        # Test health check first
        await test_health_check()
        
        # Test news discovery
        await test_news_discovery()
        
        # Test trending topics
        await test_trending_topics()
        
        print("\n🎉 All discovery tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 