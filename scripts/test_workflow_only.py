#!/usr/bin/env python3
"""
Test Workflow Only
Tests the LangGraph workflow integration with Twitter posting.
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
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.personalities.jovani_vazquez_personality import create_jovani_personality


async def test_workflow_only():
    """Test the workflow integration."""
    print("🤖 TESTING WORKFLOW INTEGRATION")
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
        
        # Ask for confirmation
        print(f"\n🤔 Ready to run the workflow and post a tweet?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Workflow execution cancelled")
            return
        
        print("\n🚀 Executing character workflow...")
        
        # Execute workflow
        result = await workflow_adapter.execute_workflow(
            workflow_definition=workflow,
            initial_state=initial_state
        )
        
        if result.success:
            print(f"✅ Workflow executed successfully!")
            print(f"   Execution time: {result.execution_time_ms} ms")
            
            # Print results
            final_state = result.final_state
            print(f"\n📊 WORKFLOW RESULTS:")
            print(f"   Engagement Decision: {final_state.get('engagement_decision', 'Unknown')}")
            print(f"   Generated Response: {final_state.get('generated_response', 'None')[:100]}..." if final_state.get('generated_response') else "   Generated Response: None")
            
            # Check agent state
            agent_state = final_state.get('agent_state')
            if agent_state:
                print(f"   Decision Confidence: {agent_state.decision_confidence:.3f}")
                print(f"   Content Approved: {agent_state.content_approved}")
            
            # Check if a tweet was posted
            if final_state.get("tweet_posted"):
                print(f"   ✅ Tweet posted: {final_state.get('twitter_tweet_id', 'Unknown ID')}")
                print(f"   Tweet URL: https://twitter.com/CuentameloAgent/status/{final_state.get('twitter_tweet_id', '')}")
            else:
                print("   ⚠️  No tweet was posted")
                if final_state.get("twitter_error"):
                    print(f"   Twitter Error: {final_state['twitter_error']}")
                
        else:
            print(f"❌ Workflow execution failed: {result.error_details}")
            
    except Exception as e:
        print(f"❌ Error in workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_only()) 