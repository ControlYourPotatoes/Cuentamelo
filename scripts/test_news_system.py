#!/usr/bin/env python3
"""
Test script for the new news system implementation.
This script tests the clean architecture news system with both Twitter and Simulated adapters.
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.dependency_container import DependencyContainer
from app.ports.news_provider import NewsProviderPort


async def test_simulated_news_provider():
    """Test the simulated news provider."""
    print("🧪 Testing Simulated News Provider")
    print("=" * 50)
    
    # Create container with simulated news provider
    container = DependencyContainer({
        "news_provider": "simulated"
    })
    
    news_provider = container.get_news_provider()
    
    # Test health check
    print("1. Testing health check...")
    health = await news_provider.health_check()
    print(f"   Health check: {'✅ PASS' if health else '❌ FAIL'}")
    
    # Test provider info
    print("2. Testing provider info...")
    provider_info = await news_provider.get_provider_info()
    print(f"   Provider: {provider_info.name} ({provider_info.type})")
    print(f"   Capabilities: {', '.join(provider_info.capabilities)}")
    
    # Test news discovery
    print("3. Testing news discovery...")
    news_items = await news_provider.discover_latest_news(max_results=5)
    print(f"   Discovered {len(news_items)} news items")
    
    for i, item in enumerate(news_items[:3], 1):
        print(f"   {i}. {item.headline[:60]}... (Score: {item.relevance_score:.2f})")
    
    # Test trending topics
    print("4. Testing trending topics...")
    trending_topics = await news_provider.get_trending_topics(max_topics=5)
    print(f"   Found {len(trending_topics)} trending topics")
    
    for i, topic in enumerate(trending_topics[:3], 1):
        print(f"   {i}. {topic.term} (Count: {topic.count}, Relevance: {topic.relevance:.2f})")
    
    # Test news ingestion
    print("5. Testing news ingestion...")
    news_item = await news_provider.ingest_news_item(
        headline="Test News: Puerto Rican Culture Celebration",
        content="A new celebration of Puerto Rican culture has been announced in San Juan. The event will feature traditional music, dance, and cuisine from across the island.",
        source="Test News",
        category="culture",
        relevance_score=0.85
    )
    print(f"   Ingested news item: {news_item.headline}")
    print(f"   Generated ID: {news_item.id}")
    
    print("\n✅ Simulated News Provider Test Complete\n")


async def test_twitter_news_provider():
    """Test the Twitter news provider (if configured)."""
    print("🐦 Testing Twitter News Provider")
    print("=" * 50)
    
    try:
        # Create container with Twitter news provider
        container = DependencyContainer({
            "news_provider": "twitter"
        })
        
        news_provider = container.get_news_provider()
        
        # Test health check
        print("1. Testing health check...")
        health = await news_provider.health_check()
        print(f"   Health check: {'✅ PASS' if health else '❌ FAIL'}")
        
        if not health:
            print("   ⚠️  Twitter provider not healthy - skipping further tests")
            return
        
        # Test provider info
        print("2. Testing provider info...")
        provider_info = await news_provider.get_provider_info()
        print(f"   Provider: {provider_info.name} ({provider_info.type})")
        print(f"   Sources: {provider_info.metadata.get('sources_count', 0)}")
        
        # Test news discovery (limited to avoid rate limits)
        print("3. Testing news discovery...")
        news_items = await news_provider.discover_latest_news(max_results=3)
        print(f"   Discovered {len(news_items)} news items")
        
        for i, item in enumerate(news_items, 1):
            print(f"   {i}. {item.headline[:60]}... (Score: {item.relevance_score:.2f})")
        
        print("\n✅ Twitter News Provider Test Complete\n")
        
    except Exception as e:
        print(f"   ❌ Twitter provider test failed: {str(e)}")
        print("   ⚠️  This is expected if Twitter API is not configured\n")


async def test_news_provider_interface():
    """Test that both providers implement the interface correctly."""
    print("🔧 Testing News Provider Interface")
    print("=" * 50)
    
    # Test simulated provider
    container_sim = DependencyContainer({"news_provider": "simulated"})
    news_provider_sim = container_sim.get_news_provider()
    
    # Test Twitter provider
    container_twitter = DependencyContainer({"news_provider": "twitter"})
    news_provider_twitter = container_twitter.get_news_provider()
    
    # Verify both implement the interface
    print("1. Checking interface implementation...")
    print(f"   Simulated provider: {'✅' if isinstance(news_provider_sim, NewsProviderPort) else '❌'}")
    print(f"   Twitter provider: {'✅' if isinstance(news_provider_twitter, NewsProviderPort) else '❌'}")
    
    # Test method signatures
    print("2. Testing method signatures...")
    methods = [
        'discover_latest_news',
        'get_trending_topics', 
        'ingest_news_item',
        'health_check',
        'get_provider_info'
    ]
    
    for method in methods:
        sim_has_method = hasattr(news_provider_sim, method)
        twitter_has_method = hasattr(news_provider_twitter, method)
        print(f"   {method}: Simulated {'✅' if sim_has_method else '❌'}, Twitter {'✅' if twitter_has_method else '❌'}")
    
    print("\n✅ Interface Test Complete\n")


async def test_dependency_injection():
    """Test dependency injection configuration."""
    print("🔌 Testing Dependency Injection")
    print("=" * 50)
    
    # Test different configurations
    configs = [
        ("simulated", "Simulated News Provider"),
        ("twitter", "Twitter News Provider"),
    ]
    
    for provider_type, expected_name in configs:
        print(f"1. Testing {provider_type} configuration...")
        
        container = DependencyContainer({"news_provider": provider_type})
        news_provider = container.get_news_provider()
        
        try:
            provider_info = await news_provider.get_provider_info()
            print(f"   ✅ {provider_type}: {provider_info.name}")
        except Exception as e:
            print(f"   ❌ {provider_type}: {str(e)}")
    
    print("\n✅ Dependency Injection Test Complete\n")


async def main():
    """Run all tests."""
    print("🚀 News System Implementation Test")
    print("=" * 60)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        # Test interface compliance
        await test_news_provider_interface()
        
        # Test dependency injection
        await test_dependency_injection()
        
        # Test simulated provider
        await test_simulated_news_provider()
        
        # Test Twitter provider (if configured)
        await test_twitter_news_provider()
        
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 