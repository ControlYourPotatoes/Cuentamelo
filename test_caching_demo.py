#!/usr/bin/env python3
"""
Demo script to test El Nuevo Día news adapter caching functionality.
"""
import asyncio
import logging
import time
from app.services.dependency_container import DependencyContainer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_caching_demo():
    """Test the caching functionality of the El Nuevo Día adapter."""
    print("🧪 El Nuevo Día Caching Demo")
    print("=" * 50)
    
    try:
        # Configure container to use El Nuevo Día adapter
        container = DependencyContainer()
        container.config["news_provider"] = "elnuevodia"
        
        # Get the news provider
        news_provider = container.get_news_provider()
        print(f"✅ Using news provider: {type(news_provider).__name__}")
        
        # Test 1: First call (should hit Twitter API)
        print("\n📰 Test 1: First call (should hit Twitter API)")
        print("-" * 40)
        start_time = time.time()
        
        try:
            news_items = await news_provider.discover_latest_news(max_results=5)
            first_call_time = time.time() - start_time
            print(f"✅ First call completed in {first_call_time:.2f}s")
            print(f"✅ Found {len(news_items)} news items")
        except Exception as e:
            print(f"⚠️ First call failed (likely rate limit): {str(e)}")
            print("This is expected if Twitter API is rate limited")
            return
        
        # Test 2: Second call (should use cache)
        print("\n📰 Test 2: Second call (should use cache)")
        print("-" * 40)
        start_time = time.time()
        
        try:
            news_items_cached = await news_provider.discover_latest_news(max_results=5)
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
            print(f"❌ Second call failed: {str(e)}")
        
        # Test 3: Trending topics caching
        print("\n📊 Test 3: Trending topics caching")
        print("-" * 40)
        
        try:
            start_time = time.time()
            trending_topics = await news_provider.get_trending_topics(max_topics=5)
            first_topics_time = time.time() - start_time
            print(f"✅ First trending topics call: {first_topics_time:.2f}s")
            print(f"✅ Found {len(trending_topics)} trending topics")
            
            start_time = time.time()
            trending_topics_cached = await news_provider.get_trending_topics(max_topics=5)
            second_topics_time = time.time() - start_time
            print(f"✅ Second trending topics call: {second_topics_time:.2f}s")
            print(f"✅ Found {len(trending_topics_cached)} trending topics")
            
            if second_topics_time < first_topics_time:
                speedup = first_topics_time / second_topics_time
                print(f"🚀 Trending topics cache speedup: {speedup:.1f}x faster!")
                
        except Exception as e:
            print(f"❌ Trending topics test failed: {str(e)}")
        
        # Test 4: Cache clearing
        print("\n🗑️ Test 4: Cache clearing")
        print("-" * 40)
        
        try:
            # Clear cache
            cleared = await news_provider.clear_cache()
            if cleared:
                print("✅ Cache cleared successfully")
                
                # Test that cache is cleared by making another call
                start_time = time.time()
                news_items_after_clear = await news_provider.discover_latest_news(max_results=5)
                clear_call_time = time.time() - start_time
                print(f"✅ Call after cache clear: {clear_call_time:.2f}s")
                print(f"✅ Found {len(news_items_after_clear)} news items")
                
            else:
                print("❌ Failed to clear cache")
                
        except Exception as e:
            print(f"❌ Cache clearing test failed: {str(e)}")
        
        print("\n🎉 Caching demo completed!")
        print("\n💡 Benefits of caching:")
        print("   • Reduced Twitter API calls (avoid rate limits)")
        print("   • Faster response times for repeated requests")
        print("   • Lower costs (fewer API calls)")
        print("   • Better user experience (consistent performance)")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        logger.exception("Demo error")

if __name__ == "__main__":
    asyncio.run(test_caching_demo()) 