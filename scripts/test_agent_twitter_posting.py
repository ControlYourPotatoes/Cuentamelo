#!/usr/bin/env python3
"""
Test Agent Twitter Posting
Tests that agents can post tweets through the LangGraph workflow system.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.adapters.twitter_adapter import TwitterAdapter
from app.adapters.claude_ai_adapter import ClaudeAIAdapter
from app.adapters.langgraph_workflow_adapter import LangGraphWorkflowAdapter
from app.graphs.character_workflow import create_character_workflow
from app.models.conversation import NewsItem
from app.models.personality import create_jovani_vazquez_personality
from app.ports.twitter_provider import TwitterPostType


async def test_agent_workflow_posting():
    """Test that an agent can post through the LangGraph workflow."""
    print("🤖 TESTING AGENT WORKFLOW TWITTER POSTING")
    print("=" * 60)
    
    try:
        # Initialize components
        twitter_adapter = TwitterAdapter()
        ai_adapter = ClaudeAIAdapter()
        workflow_adapter = LangGraphWorkflowAdapter()
        
        print("✅ Components initialized")
        
        # Create a test news item
        test_news = NewsItem(
            id=str(uuid.uuid4()),
            headline="Test News: Puerto Rico's AI Innovation",
            content="Puerto Rico is making waves in AI technology with innovative startups and research initiatives.",
            source="Test Source",
            url="https://example.com/test-news",
            published_at=datetime.now(timezone.utc),
            relevance_score=0.9,
            puerto_rico_relevance=0.95
        )
        
        print(f"📰 Test news created: {test_news.title}")
        
        # Create Jovani personality
        jovani_personality = create_jovani_vazquez_personality()
        print("🎭 Jovani personality loaded")
        
        # Create character workflow
        workflow = create_character_workflow()
        print("🔄 Character workflow created")
        
        # Prepare workflow state
        initial_state = {
            "news_item": test_news,
            "character_id": "jovani_vazquez",
            "character_name": "Jovani Vázquez",
            "personality": jovani_personality,
            "ai_provider": ai_adapter,
            "twitter_provider": twitter_adapter,
            "thread_engagement_state": None,
            "execution_start_time": datetime.now(timezone.utc)
        }
        
        print("📋 Workflow state prepared")
        
        # Ask for confirmation
        print(f"\n🤔 Ready to run the agent workflow and post a tweet?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Workflow execution cancelled")
            return
        
        print("\n🚀 Executing character workflow...")
        
        # Execute workflow
        result = await workflow_adapter.execute_workflow(
            workflow=workflow,
            initial_state=initial_state
        )
        
        if result.success:
            print(f"✅ Workflow executed successfully!")
            print(f"   Execution time: {result.execution_time:.2f}s")
            
            # Check if a tweet was posted
            final_state = result.final_state
            if "tweet_posted" in final_state and final_state["tweet_posted"]:
                print(f"   Tweet posted: {final_state.get('twitter_tweet_id', 'Unknown ID')}")
                print(f"   Tweet URL: https://twitter.com/CuentameloAgent/status/{final_state.get('twitter_tweet_id', '')}")
            else:
                print("   ⚠️  No tweet was posted (agent decided not to engage)")
                
        else:
            print(f"❌ Workflow execution failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error in workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_direct_agent_posting():
    """Test direct agent posting without workflow."""
    print("\n🎭 TESTING DIRECT AGENT POSTING")
    print("=" * 60)
    
    try:
        twitter_adapter = TwitterAdapter()
        
        # Generate unique content
        timestamp = datetime.now().strftime("%H:%M:%S")
        unique_content = f"¡Wepa! Testing our AI agent system at {timestamp}! 🔥 The integration is working perfectly and I'm excited to share more Puerto Rican content! 💯 #AITest #PuertoRico"
        
        print(f"\n📝 Unique test content:")
        print(f"   {unique_content}")
        print(f"   Length: {len(unique_content)}/280")
        
        # Ask for confirmation
        print(f"\n🤔 Ready to post this unique tweet?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Posting cancelled")
            return
        
        print("\n🚀 Posting unique tweet...")
        
        # Post the tweet
        result = await twitter_adapter.post_tweet(
            content=unique_content,
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez"
        )
        
        if result.success:
            print(f"✅ Tweet posted successfully!")
            print(f"   Tweet ID: {result.twitter_tweet_id}")
            print(f"   Posted at: {result.post.posted_at}")
            print(f"   URL: https://twitter.com/CuentameloAgent/status/{result.twitter_tweet_id}")
            
            if result.rate_limit_info:
                print(f"   Rate limit: {result.rate_limit_info.remaining}/{result.rate_limit_info.limit} remaining")
        else:
            print(f"❌ Failed to post tweet: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_news_discovery_posting():
    """Test posting in response to discovered news."""
    print("\n📰 TESTING NEWS DISCOVERY POSTING")
    print("=" * 60)
    
    try:
        twitter_adapter = TwitterAdapter()
        
        # Create a realistic news item
        news_content = "Breaking: Puerto Rico's tech startup scene is booming! 🚀 Local entrepreneurs are creating innovative solutions for the island's challenges. #PuertoRico #TechStartups #Innovation"
        
        # Generate Jovani's response
        jovani_response = f"¡Brutal! This is exactly what PR needs! 🔥 Our tech scene is on fire and I'm here for it! 💯 Let's support our local entrepreneurs and show the world what Boricuas can do! 🇵🇷 #BoricuaTech #Innovation"
        
        print(f"\n📰 News content:")
        print(f"   {news_content}")
        
        print(f"\n🎭 Jovani's response:")
        print(f"   {jovani_response}")
        print(f"   Length: {len(jovani_response)}/280")
        
        # Ask for confirmation
        print(f"\n🤔 Ready to post Jovani's response to this news?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Posting cancelled")
            return
        
        print("\n🚀 Posting news response...")
        
        # Post the response
        result = await twitter_adapter.post_tweet(
            content=jovani_response,
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez"
        )
        
        if result.success:
            print(f"✅ News response posted successfully!")
            print(f"   Tweet ID: {result.twitter_tweet_id}")
            print(f"   URL: https://twitter.com/CuentameloAgent/status/{result.twitter_tweet_id}")
        else:
            print(f"❌ Failed to post news response: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error posting news response: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("🤖 AGENT TWITTER POSTING TEST SUITE")
    print("=" * 60)
    print("Testing agent tweet posting capabilities...")
    
    # Test direct agent posting first (simpler)
    await test_direct_agent_posting()
    
    # Test news discovery posting
    await test_news_discovery_posting()
    
    # Test full workflow integration (more complex)
    await test_agent_workflow_posting()
    
    print("\n🎉 Agent posting tests completed!")
    print("\nCheck your @CuentameloAgent account to see the results!")


if __name__ == "__main__":
    asyncio.run(main()) 