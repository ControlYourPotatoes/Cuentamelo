#!/usr/bin/env python3
"""
Test script for Jovani's reaction to news scenarios.
This script tests how Jovani responds to the demo news items.
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


async def test_jovani_news_reaction():
    """Test Jovani's reaction to demo news scenarios."""
    print("🎭 Testing Jovani's News Reactions")
    print("=" * 60)
    
    # Create container with simulated news provider
    container = DependencyContainer({
        "news_provider": "simulated"
    })
    
    # Get news provider and discover news
    news_provider = container.get_news_provider()
    news_items = await news_provider.discover_latest_news(max_results=3)
    
    if not news_items:
        print("❌ No news items found!")
        return
    
    # Create Jovani agent
    print("1. Creating Jovani agent...")
    
    # Get AI provider from dependency container
    ai_provider = container.get_ai_provider()
    jovani = create_agent("jovani_vazquez", ai_provider=ai_provider)
    
    if not jovani:
        print("❌ Failed to create Jovani agent!")
        return
    
    print(f"   ✅ Jovani created: {jovani.character_name}")
    if jovani.personality_data:
        print(f"   📝 Personality: {jovani.personality_data.personality_traits}")
    else:
        print("   📝 Personality: Not loaded")
    
    # Test reactions to each news item
    for i, news_item in enumerate(news_items, 1):
        print(f"\n📰 News Item {i}: {news_item.headline}")
        print("-" * 50)
        print(f"Content: {news_item.content[:150]}...")
        print(f"Source: {news_item.source}")
        print(f"Topics: {', '.join(news_item.topics) if news_item.topics else 'None'}")
        print(f"Relevance Score: {news_item.relevance_score:.2f}")
        
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


async def test_jovani_trending_reaction():
    """Test Jovani's reaction to trending topics."""
    print("\n🔥 Testing Jovani's Reaction to Trending Topics")
    print("=" * 60)
    
    # Create container with simulated news provider
    container = DependencyContainer({
        "news_provider": "simulated"
    })
    
    # Get trending topics
    news_provider = container.get_news_provider()
    trending_topics = await news_provider.get_trending_topics(max_topics=3)
    
    if not trending_topics:
        print("❌ No trending topics found!")
        return
    
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
                is_new_thread=True,  # Force new thread for each trending topic
                thread_engagement_state=None  # Reset thread state
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


async def test_jovani_custom_news():
    """Test Jovani's reaction to a custom news item."""
    print("\n📝 Testing Jovani's Reaction to Custom News")
    print("=" * 60)
    
    # Create container with simulated news provider
    container = DependencyContainer({
        "news_provider": "simulated"
    })
    
    # Create Jovani agent
    ai_provider = container.get_ai_provider()
    jovani = create_agent("jovani_vazquez", ai_provider=ai_provider)
    if not jovani:
        print("❌ Failed to create Jovani agent!")
        return
    
    # Create a custom news item
    custom_news = {
        "headline": "Puerto Rican Coffee Wins International Award",
        "content": "Puerto Rican coffee from the central mountains has won the prestigious International Coffee Excellence Award. This recognition highlights the island's rich coffee heritage and the dedication of local farmers. The winning coffee comes from a small family farm in Adjuntas.",
        "source": "Coffee News",
        "topics": ["coffee", "culture", "awards"],
        "relevance_score": 0.9
    }
    
    print(f"📰 Custom News: {custom_news['headline']}")
    print("-" * 50)
    print(f"Content: {custom_news['content']}")
    print(f"Source: {custom_news['source']}")
    print(f"Topics: {', '.join(custom_news['topics'])}")
    print(f"Relevance Score: {custom_news['relevance_score']:.2f}")
    
    try:
        # Ingest the custom news
        news_provider = container.get_news_provider()
        news_item = await news_provider.ingest_news_item(
            headline=custom_news["headline"],
            content=custom_news["content"],
            source=custom_news["source"],
            tags=custom_news["topics"],
            relevance_score=custom_news["relevance_score"]
        )
        
        print(f"\n🤖 Jovani's Reaction:")
        print("-" * 30)
        
        result = await execute_character_workflow(
            character_agent=jovani,
            input_context=news_item.content,
            news_item=news_item,
            target_topic="coffee"
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
        print(f"❌ Error processing custom news: {str(e)}")
    
    print("\n" + "="*60)


async def main():
    """Run all Jovani news reaction tests."""
    print("🎭 Jovani News Reaction Test")
    print("=" * 60)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        # Test reactions to demo news scenarios
        await test_jovani_news_reaction()
        
        # Test reactions to trending topics
        await test_jovani_trending_reaction()
        
        # Test reaction to custom news
        await test_jovani_custom_news()
        
        print("\n🎉 All Jovani news reaction tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 