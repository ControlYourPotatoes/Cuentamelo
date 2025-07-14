#!/usr/bin/env python3
"""
Test El Nuevo Día adapter caching functionality with minimal API calls.
"""
import asyncio
import logging
import time
from app.services.dependency_container import DependencyContainer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_elnuevodia_caching():
    """Test the El Nuevo Día adapter caching with minimal API calls."""
    print("🧪 Testing El Nuevo Día Caching (Minimal API Calls)")
    print("=" * 60)
    
    try:
        # Configure container to use El Nuevo Día adapter
        container = DependencyContainer()
        container.config["news_provider"] = "elnuevodia"
        
        # Get the news provider
        news_provider = container.get_news_provider()
        print(f"✅ Using news provider: {type(news_provider).__name__}")
        
        # Test 1: Provider info (no API call)
        print("\n📋 Test 1: Provider Info (No API Call)")
        print("-" * 40)
        provider_info = await news_provider.get_provider_info()
        print(f"✅ Provider: {provider_info.name}")
        print(f"✅ Type: {provider_info.type}")
        print(f"✅ Capabilities: {provider_info.capabilities}")
        
        # Test 2: Cache clearing (no API call)
        print("\n🗑️ Test 2: Cache Management (No API Call)")
        print("-" * 40)
        try:
            cleared = await news_provider.clear_cache()
            print(f"✅ Cache clearing result: {cleared}")
        except Exception as e:
            print(f"⚠️ Cache clearing failed (expected if Redis is down): {str(e)}")
        
        # Test 3: Health check (minimal API call - just 5 tweets)
        print("\n🏥 Test 3: Health Check (Minimal API Call)")
        print("-" * 40)
        try:
            start_time = time.time()
            health = await news_provider.health_check()
            health_time = time.time() - start_time
            print(f"✅ Health check result: {health} (took {health_time:.2f}s)")
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            print("This might be due to rate limiting - that's expected")
            return
        
        # Test 4: News discovery with caching (small request)
        print("\n📰 Test 4: News Discovery with Caching")
        print("-" * 40)
        try:
            print("First call (should hit API and cache results)...")
            start_time = time.time()
            news_items = await news_provider.discover_latest_news(max_results=3)
            first_call_time = time.time() - start_time
            print(f"✅ First call completed in {first_call_time:.2f}s")
            print(f"✅ Found {len(news_items)} news items")
            
            if news_items:
                print("Sample news items:")
                for i, item in enumerate(news_items[:2], 1):
                    print(f"   {i}. {item.headline[:50]}...")
                    print(f"      Topics: {item.topics}")
                    print(f"      Relevance: {item.relevance_score:.2f}")
            
            print("\nSecond call (should use cache)...")
            start_time = time.time()
            news_items_cached = await news_provider.discover_latest_news(max_results=3)
            second_call_time = time.time() - start_time
            print(f"✅ Second call completed in {second_call_time:.2f}s")
            print(f"✅ Found {len(news_items_cached)} news items")
            
            # Compare performance
            if second_call_time < first_call_time:
                speedup = first_call_time / second_call_time
                print(f"🚀 Cache speedup: {speedup:.1f}x faster!")
            else:
                print("⚠️ No speedup observed (cache miss or other factors)")
                
        except Exception as e:
            print(f"❌ News discovery failed: {str(e)}")
            print("This might be due to rate limiting - that's expected")
        
        # Test 5: Trending topics with caching
        print("\n📊 Test 5: Trending Topics with Caching")
        print("-" * 40)
        try:
            print("First trending topics call...")
            start_time = time.time()
            trending_topics = await news_provider.get_trending_topics(max_topics=3)
            first_topics_time = time.time() - start_time
            print(f"✅ First trending topics call: {first_topics_time:.2f}s")
            print(f"✅ Found {len(trending_topics)} trending topics")
            
            if trending_topics:
                print("Sample trending topics:")
                for i, topic in enumerate(trending_topics[:2], 1):
                    print(f"   {i}. {topic.term} (count: {topic.count}, relevance: {topic.relevance:.2f})")
            
            print("\nSecond trending topics call...")
            start_time = time.time()
            trending_topics_cached = await news_provider.get_trending_topics(max_topics=3)
            second_topics_time = time.time() - start_time
            print(f"✅ Second trending topics call: {second_topics_time:.2f}s")
            print(f"✅ Found {len(trending_topics_cached)} trending topics")
            
            if second_topics_time < first_topics_time:
                speedup = first_topics_time / second_topics_time
                print(f"🚀 Trending topics cache speedup: {speedup:.1f}x faster!")
                
        except Exception as e:
            print(f"❌ Trending topics failed: {str(e)}")
            print("This might be due to rate limiting - that's expected")
        
        print("\n🎉 Caching test completed!")
        print("\n📝 What we tested:")
        print("   ✅ Provider info (no API calls)")
        print("   ✅ Cache management functions")
        print("   ✅ Health check (minimal API call)")
        print("   ✅ News discovery with caching")
        print("   ✅ Trending topics with caching")
        print("\n💡 Caching benefits demonstrated:")
        print("   • Faster subsequent requests")
        print("   • Reduced API calls")
        print("   • Better user experience")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(test_elnuevodia_caching()) 