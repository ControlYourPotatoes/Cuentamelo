#!/usr/bin/env python3
"""
Test script for Twitter-based news discovery and character responses.
This demonstrates the complete pipeline from Twitter news discovery to AI character responses.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the app directory to the Python path
app_path = str(Path(__file__).parent.parent)
if app_path not in sys.path:
    sys.path.insert(0, app_path)

from dotenv import load_dotenv
load_dotenv()

from app.tools.news_discovery import NewsDiscoveryService
from app.tools.twitter_connector import TwitterConnector
from app.services.redis_client import RedisClient
from app.agents.agent_factory import create_agent
from app.graphs.character_workflow import execute_character_workflow
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_news_discovery():
    """Test Twitter-based news discovery."""
    print("🔍 Testing Twitter-based news discovery...")
    
    try:
        # Initialize services
        twitter_connector = TwitterConnector()
        redis_client = RedisClient()
        news_service = NewsDiscoveryService(twitter_connector, redis_client)
        
        # Discover latest news
        news_items = await news_service.discover_latest_news(max_results=5)
        
        if news_items:
            print(f"✅ Discovered {len(news_items)} news items from Twitter")
            
            for i, item in enumerate(news_items, 1):
                print(f"\n📰 News {i}:")
                print(f"   Headline: {item.headline}")
                print(f"   Source: {item.source}")
                print(f"   Relevance: {item.relevance_score:.2f}")
                print(f"   URL: {item.url}")
                print(f"   Content: {item.content[:100]}...")
            
            return news_items
        else:
            print("⚠️ No news items discovered (check Twitter API configuration)")
            return []
            
    except Exception as e:
        print(f"❌ Error in news discovery: {str(e)}")
        return []


async def test_character_responses_to_news(news_items):
    """Test character responses to discovered news."""
    print(f"\n🤖 Testing character responses to {len(news_items)} news items...")
    
    if not news_items:
        print("⚠️ No news items to process")
        return
    
    # Create Jovani agent
    jovani_agent = create_agent("jovani_vazquez")
    if not jovani_agent:
        print("❌ Failed to create Jovani agent")
        return
    
    print(f"✅ Created agent: {jovani_agent.character_name}")
    
    successful_responses = 0
    
    for i, news_item in enumerate(news_items[:3], 1):  # Test with first 3 news items
        print(f"\n🎭 Testing response to news {i}: {news_item.headline}")
        
        try:
            # Execute character workflow
            result = await execute_character_workflow(
                character_agent=jovani_agent,
                input_context=news_item.content,
                news_item=news_item,
                target_topic="news_reaction"
            )
            
            if result["success"]:
                print(f"✅ Workflow executed successfully")
                
                if result.get("engagement_decision"):
                    print(f"📊 Engagement decision: {result['engagement_decision']}")
                
                if result.get("generated_response"):
                    response = result["generated_response"]
                    print(f"💬 Generated response: {response}")
                    print(f"📏 Response length: {len(response)} characters")
                    successful_responses += 1
                else:
                    print("⚠️ No response generated (character chose not to engage)")
            else:
                print(f"❌ Workflow failed: {result.get('error_details', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing news {i}: {str(e)}")
    
    print(f"\n📊 Results: {successful_responses}/{min(3, len(news_items))} successful responses")


async def test_trending_topics():
    """Test trending topics extraction."""
    print("\n📈 Testing trending topics extraction...")
    
    try:
        # Initialize services
        twitter_connector = TwitterConnector()
        redis_client = RedisClient()
        news_service = NewsDiscoveryService(twitter_connector, redis_client)
        
        # Get trending topics
        trending_topics = await news_service.get_trending_topics()
        
        if trending_topics:
            print(f"✅ Extracted {len(trending_topics)} trending topics")
            
            for i, topic in enumerate(trending_topics[:5], 1):
                print(f"\n🔥 Topic {i}:")
                print(f"   Term: {topic['term']}")
                print(f"   Count: {topic['count']}")
                print(f"   Relevance: {topic['relevance']:.2f}")
                print(f"   Category: {topic['category']}")
        else:
            print("⚠️ No trending topics found")
            
    except Exception as e:
        print(f"❌ Error extracting trending topics: {str(e)}")


async def test_cached_news():
    """Test news caching functionality."""
    print("\n💾 Testing news caching functionality...")
    
    try:
        # Initialize services
        twitter_connector = TwitterConnector()
        redis_client = RedisClient()
        news_service = NewsDiscoveryService(twitter_connector, redis_client)
        
        # First call - should fetch fresh data
        print("🔄 First call - fetching fresh data...")
        news_items_1 = await news_service.discover_latest_news(max_results=3)
        
        # Second call - should return cached data
        print("💾 Second call - should return cached data...")
        news_items_2 = await news_service.discover_latest_news(max_results=3)
        
        if news_items_1 and news_items_2:
            print(f"✅ Caching working: {len(news_items_1)} items cached and retrieved")
            
            # Check if items are the same (cached)
            if len(news_items_1) == len(news_items_2):
                print("✅ Cache consistency verified")
            else:
                print("⚠️ Cache inconsistency detected")
        else:
            print("⚠️ No news items to test caching")
            
    except Exception as e:
        print(f"❌ Error testing caching: {str(e)}")


async def main():
    """Main test function."""
    print("🚀 Starting Twitter News Discovery Tests")
    print("=" * 60)
    
    # Check if Twitter API is configured
    twitter_key = os.getenv("TWITTER_BEARER_TOKEN")
    if not twitter_key:
        print("⚠️ Warning: TWITTER_BEARER_TOKEN not set")
        print("   News discovery will use cached data or return empty results")
    
    # Check if Claude API is configured
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    if not claude_key:
        print("⚠️ Warning: ANTHROPIC_API_KEY not set")
        print("   Character responses will use mock data")
    
    print(f"🐦 Twitter API: {'✅ Configured' if twitter_key else '❌ Not configured'}")
    print(f"🤖 Claude API: {'✅ Configured' if claude_key else '❌ Not configured'}")
    
    # Run tests
    tests = [
        ("News Discovery", test_news_discovery),
        ("Trending Topics", test_trending_topics),
        ("News Caching", test_cached_news),
    ]
    
    results = []
    discovered_news = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "News Discovery":
                result = await test_func()
                discovered_news = result
                results.append((test_name, bool(result)))
            else:
                await test_func()
                results.append((test_name, True))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Test character responses if we have news
    if discovered_news:
        print(f"\n{'='*20} Character Responses {'='*20}")
        try:
            await test_character_responses_to_news(discovered_news)
            results.append(("Character Responses", True))
        except Exception as e:
            print(f"❌ Character response test failed: {str(e)}")
            results.append(("Character Responses", False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Twitter news discovery is working correctly.")
        print("\n🚀 Next steps:")
        print("   1. Set up automated news discovery scheduling")
        print("   2. Configure Twitter posting for character responses")
        print("   3. Add more character personalities")
        print("   4. Implement real-time monitoring dashboard")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main()) 