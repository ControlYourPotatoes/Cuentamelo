#!/usr/bin/env python3
"""
Test script for El Nuevo Día news integration.
This script tests how Jovani responds to real news from @ElNuevoDia.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.dependency_container import DependencyContainer
from app.agents.agent_factory import create_agent
from app.graphs.character_workflow import execute_character_workflow


async def test_elnuevodia_news():
    """Test Jovani's reaction to real El Nuevo Día news."""
    print("📰 Testing El Nuevo Día News Integration")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Get news provider and discover news
    news_provider = container.get_news_provider()
    print("🔍 Discovering latest news from @ElNuevoDia...")
    
    try:
        news_items = await news_provider.discover_latest_news(max_results=5)
        
        if not news_items:
            print("❌ No news items found from El Nuevo Día!")
            print("This could mean:")
            print("- No recent news tweets")
            print("- Twitter API rate limits")
            print("- Network connectivity issues")
            return
        
        print(f"✅ Found {len(news_items)} news items from El Nuevo Día")
        
        # Create Jovani agent
        print("\n1. Creating Jovani agent...")
        ai_provider = container.get_ai_provider()
        jovani = create_agent("jovani_vazquez", ai_provider=ai_provider)
        
        if not jovani:
            print("❌ Failed to create Jovani agent!")
            return
        
        print(f"   ✅ Jovani created: {jovani.character_name}")
        
        # Test reactions to each news item
        for i, news_item in enumerate(news_items, 1):
            print(f"\n📰 News Item {i}: {news_item.headline}")
            print("-" * 60)
            print(f"Content: {news_item.content}")
            print(f"Source: {news_item.source}")
            print(f"Topics: {', '.join(news_item.topics) if news_item.topics else 'None'}")
            print(f"Relevance Score: {news_item.relevance_score:.2f}")
            print(f"Published: {news_item.published_at}")
            
            try:
                # Execute character workflow with the news
                print(f"\n🤖 Jovani's Reaction:")
                print("-" * 30)
                
                result = await execute_character_workflow(
                    character_agent=jovani,
                    input_context=news_item.content,
                    news_item=news_item,
                    target_topic=None,
                    is_new_thread=True,  # Force new thread for each news item
                    thread_engagement_state=None  # Reset thread state
                )
                
                if result["success"]:
                    print(f"✅ Engagement Decision: {result.get('engagement_decision', 'unknown')}")
                    agent_state = result.get('agent_state')
                    if agent_state:
                        print(f"🎯 Confidence Score: {agent_state.decision_confidence:.2f}")
                    else:
                        print("🎯 Confidence Score: 0.00")
                    print(f"⏱️  Processing Time: {result.get('execution_time_ms', 0)}ms")
                    
                    if result.get("generated_response"):
                        print(f"\n💬 Jovani's Response:")
                        print(f"\"{result['generated_response']}\"")
                    else:
                        print("🤐 Jovani chose not to respond")
                else:
                    print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error processing news: {str(e)}")
            
            print("\n" + "="*60)
            
    except Exception as e:
        print(f"❌ Error accessing El Nuevo Día news: {str(e)}")
        print("This could be due to:")
        print("- Twitter API authentication issues")
        print("- Rate limiting")
        print("- Network connectivity problems")


async def test_elnuevodia_trending():
    """Test trending topics from El Nuevo Día."""
    print("\n🔥 Testing El Nuevo Día Trending Topics")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Get trending topics
    news_provider = container.get_news_provider()
    print("🔍 Getting trending topics from @ElNuevoDia...")
    
    try:
        trending_topics = await news_provider.get_trending_topics(max_topics=5)
        
        if not trending_topics:
            print("❌ No trending topics found!")
            return
        
        print(f"✅ Found {len(trending_topics)} trending topics")
        
        # Create Jovani agent
        ai_provider = container.get_ai_provider()
        jovani = create_agent("jovani_vazquez", ai_provider=ai_provider)
        if not jovani:
            print("❌ Failed to create Jovani agent!")
            return
        
        # Test reactions to trending topics
        for i, topic in enumerate(trending_topics, 1):
            print(f"\n🔥 Trending Topic {i}: {topic.term}")
            print("-" * 40)
            print(f"Count: {topic.count}")
            print(f"Relevance: {topic.relevance:.2f}")
            print(f"Category: {topic.category}")
            
            try:
                # Create a simple context from the trending topic
                context = f"Trending topic: {topic.term} is currently popular in Puerto Rico with {topic.count} mentions."
                
                result = await execute_character_workflow(
                    character_agent=jovani,
                    input_context=context,
                    news_item=None,
                    target_topic=topic.term,
                    is_new_thread=True,
                    thread_engagement_state=None
                )
                
                if result["success"]:
                    print(f"✅ Engagement Decision: {result.get('engagement_decision', 'unknown')}")
                    agent_state = result.get('agent_state')
                    if agent_state:
                        print(f"🎯 Confidence Score: {agent_state.decision_confidence:.2f}")
                    else:
                        print("🎯 Confidence Score: 0.00")
                    
                    if result.get("generated_response"):
                        print(f"\n💬 Jovani's Response:")
                        print(f"\"{result['generated_response']}\"")
                    else:
                        print("🤐 Jovani chose not to respond")
                else:
                    print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error processing trending topic: {str(e)}")
            
            print("\n" + "="*60)
            
    except Exception as e:
        print(f"❌ Error getting trending topics: {str(e)}")


async def test_health_check():
    """Test the health of the El Nuevo Día integration."""
    print("\n🏥 Testing El Nuevo Día Health Check")
    print("=" * 60)
    
    # Create container with El Nuevo Día news provider
    container = DependencyContainer({
        "news_provider": "elnuevodia"
    })
    
    # Test health check
    news_provider = container.get_news_provider()
    
    try:
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


async def main():
    """Run all El Nuevo Día integration tests."""
    print("📰 El Nuevo Día News Integration Test")
    print("=" * 60)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        # Test health check first
        await test_health_check()
        
        # Test news discovery and reactions
        await test_elnuevodia_news()
        
        # Test trending topics
        await test_elnuevodia_trending()
        
        print("\n🎉 All El Nuevo Día integration tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 