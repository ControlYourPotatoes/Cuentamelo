#!/usr/bin/env python3
"""
Test Workflow Only - Enhanced Comparison Test
Tests both direct workflow execution and adapter approach to identify differences.
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
from app.graphs.character_workflow import create_character_workflow, execute_character_workflow
from app.models.conversation import NewsItem
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.personalities.jovani_vazquez_personality import create_jovani_personality


async def test_workflow_comparison():
    """Test both workflow execution approaches side by side."""
    print("🤖 WORKFLOW COMPARISON TEST")
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
            headline="¡Wepa! Puerto Rico's Tech Scene is Exploding! 🚀",
            content="Puerto Rico's tech scene is absolutely on fire! From San Juan to Ponce, young entrepreneurs are building the next big thing. The energy is incredible - it's like we're having our own Silicon Valley moment right here in the Caribbean! #PuertoRicoTech #Innovation #CaribbeanStartups",
            source="Test Source",
            url="https://example.com/test-news",
            published_at=datetime.now(timezone.utc),
            relevance_score=0.95,
            puerto_rico_relevance=0.98,
            topics=["technology", "entrepreneurship", "innovation", "puerto_rico", "startups"]
        )
        
        print(f"📰 Test news created: {test_news.headline}")
        
        # Create Jovani personality and agent
        jovani_personality = create_jovani_personality()
        jovani_agent = create_jovani_vazquez(
            ai_provider=ai_adapter, 
            personality=jovani_personality,
            twitter_provider=twitter_adapter
        )
        print("🤖 Jovani agent created with Twitter provider")
        
        # Test 1: Direct workflow execution (like the successful test)
        print("\n" + "="*60)
        print("🧪 TEST 1: Direct Workflow Execution")
        print("="*60)
        
        result1 = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context=f"News: {test_news.headline}\n\n{test_news.content}",
            news_item=test_news,
            is_new_thread=True,
            thread_engagement_state=None
        )
        
        print(f"✅ Direct execution result:")
        print(f"   Success: {result1.get('success', False)}")
        print(f"   Engagement Decision: {result1.get('engagement_decision', 'Unknown')}")
        print(f"   Generated Response: {result1.get('generated_response', 'None')[:50]}..." if result1.get('generated_response') else "   Generated Response: None")
        print(f"   Tweet Posted: {result1.get('tweet_posted', 'Not set')}")
        print(f"   Twitter Error: {result1.get('twitter_error', 'None')}")
        print(f"   Final Step: {result1.get('workflow_step', 'Unknown')}")
        
        # Test 2: Adapter workflow execution (like your current test)
        print("\n" + "="*60)
        print("🧪 TEST 2: Adapter Workflow Execution")
        print("="*60)
        
        # Create character workflow
        workflow = create_character_workflow()
        
        # Prepare workflow state
        initial_state = {
            "character_agent": jovani_agent,
            "input_context": f"News: {test_news.headline}\n\n{test_news.content}",
            "news_item": test_news,
            "conversation_history": None,
            "target_topic": None,
            "thread_id": None,
            "thread_context": None,
            "is_new_thread": True,
            "thread_engagement_state": None,
            "agent_state": None,
            "engagement_decision": None,
            "generated_response": None,
            "character_reaction": None,
            "final_message": None,
            "workflow_step": "start",
            "execution_time_ms": 0,
            "error_details": None,
            "success": False
        }
        
        # Execute workflow
        result2 = await workflow_adapter.execute_workflow(
            workflow_definition=workflow,
            initial_state=initial_state
        )
        
        if result2.success:
            final_state = result2.final_state
            print(f"✅ Adapter execution result:")
            print(f"   Success: {result2.success}")
            print(f"   Engagement Decision: {final_state.get('engagement_decision', 'Unknown')}")
            print(f"   Generated Response: {final_state.get('generated_response', 'None')[:50]}..." if final_state.get('generated_response') else "   Generated Response: None")
            print(f"   Tweet Posted: {final_state.get('tweet_posted', 'Not set')}")
            print(f"   Twitter Error: {final_state.get('twitter_error', 'None')}")
            print(f"   Final Step: {final_state.get('workflow_step', 'Unknown')}")
            
            # Check agent state
            agent_state = final_state.get('agent_state')
            if agent_state:
                print(f"   Agent State Step: {agent_state.current_step}")
                print(f"   Agent State Complete: {agent_state.workflow_complete}")
        else:
            print(f"❌ Adapter execution failed: {result2.error_details}")
        
        # Comparison
        print("\n" + "="*60)
        print("📊 COMPARISON RESULTS")
        print("="*60)
        
        direct_tweet_posted = result1.get('tweet_posted', False)
        adapter_tweet_posted = False
        if result2.success and result2.final_state:
            adapter_tweet_posted = result2.final_state.get('tweet_posted', False)
        
        print(f"Direct execution tweet posted: {direct_tweet_posted}")
        print(f"Adapter execution tweet posted: {adapter_tweet_posted}")
        
        if direct_tweet_posted != adapter_tweet_posted:
            print("❌ DIFFERENCE DETECTED: The two approaches produce different results!")
            print("   This suggests there's a difference in how the workflow state is handled.")
        else:
            print("✅ Both approaches produce the same result")
            
    except Exception as e:
        print(f"❌ Error in workflow comparison: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_comparison()) 