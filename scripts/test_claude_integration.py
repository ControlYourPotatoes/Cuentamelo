#!/usr/bin/env python3
"""
Test script for Claude API integration with character workflows.
This script tests the complete integration from AI provider to character response generation.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Add the app directory to the Python path
app_path = str(Path(__file__).parent.parent)
if app_path not in sys.path:
    sys.path.insert(0, app_path)

from app.services.dependency_container import get_container, configure_container_for_production
from app.agents.agent_factory import create_agent
from app.models.conversation import NewsItem
from app.graphs.character_workflow import execute_character_workflow
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_claude_health_check():
    """Test Claude API health check."""
    print("🔍 Testing Claude API health check...")
    
    try:
        container = get_container()
        configure_container_for_production()
        
        ai_provider = container.get_ai_provider()
        is_healthy = await ai_provider.health_check()
        
        if is_healthy:
            print("✅ Claude API health check passed!")
            return True
        else:
            print("❌ Claude API health check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during health check: {str(e)}")
        return False


async def test_character_response_generation():
    """Test character response generation with Claude API."""
    print("\n🤖 Testing character response generation...")
    
    try:
        # Create Jovani agent
        jovani_agent = create_agent("jovani_vazquez")
        
        if not jovani_agent:
            print("❌ Failed to create Jovani agent")
            return False
        
        print(f"✅ Created agent: {jovani_agent.character_name}")
        
        # Test context
        test_context = "Breaking news: Puerto Rican artist Bad Bunny just announced a surprise concert in San Juan next month!"
        
        # Create a news item
        news_item = NewsItem(
            id="test_news_001",
            headline="Bad Bunny Announces Surprise Concert in San Juan",
            content=test_context,
            source="Test News",
            published_at="2025-01-15T10:00:00Z",
            relevance_score=0.9
        )
        
        print(f"📰 Testing with news: {news_item.headline}")
        
        # Execute character workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context=test_context,
            news_item=news_item,
            target_topic="music_entertainment"
        )
        
        if result["success"]:
            print("✅ Character workflow executed successfully!")
            
            if result.get("engagement_decision"):
                print(f"📊 Engagement decision: {result['engagement_decision']}")
            
            if result.get("generated_response"):
                print(f"💬 Generated response: {result['generated_response']}")
                print(f"📏 Response length: {len(result['generated_response'])} characters")
            else:
                print("⚠️ No response generated (character chose not to engage)")
            
            return True
        else:
            print(f"❌ Character workflow failed: {result.get('error_details', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during character response test: {str(e)}")
        return False


async def test_multiple_characters():
    """Test multiple characters responding to the same news."""
    print("\n👥 Testing multiple character responses...")
    
    try:
        # Create multiple agents
        agents = []
        for character_id in ["jovani_vazquez", "politico_boricua", "abuela_carmen", "profesor_ramirez"]:
            agent = create_agent(character_id)
            if agent:
                agents.append(agent)
                print(f"✅ Created agent: {agent.character_name}")
        
        if not agents:
            print("❌ No agents created")
            return False
        
        # Test context
        test_context = "Puerto Rico's economy shows strong growth in tourism sector, with record visitor numbers this year."
        
        news_item = NewsItem(
            id="test_news_002",
            headline="Puerto Rico Tourism Booms with Record Visitor Numbers",
            content=test_context,
            source="Economic News",
            published_at="2025-01-15T11:00:00Z",
            relevance_score=0.8
        )
        
        print(f"📰 Testing with news: {news_item.headline}")
        
        # Test each character
        successful_responses = 0
        
        for agent in agents:
            print(f"\n🎭 Testing {agent.character_name}...")
            
            result = await execute_character_workflow(
                character_agent=agent,
                input_context=test_context,
                news_item=news_item,
                target_topic="economy_tourism"
            )
            
            if result["success"] and result.get("generated_response"):
                print(f"✅ {agent.character_name} responded: {result['generated_response'][:100]}...")
                successful_responses += 1
            else:
                print(f"⚠️ {agent.character_name} chose not to engage")
        
        print(f"\n📊 Results: {successful_responses}/{len(agents)} characters responded")
        return successful_responses > 0
        
    except Exception as e:
        print(f"❌ Error during multiple character test: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Claude API Integration Tests")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ Warning: ANTHROPIC_API_KEY not set in environment")
        print("   Please set your Anthropic API key to test Claude integration")
        print("   You can set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Run tests
    tests = [
        ("Claude Health Check", test_claude_health_check),
        ("Character Response Generation", test_character_response_generation),
        ("Multiple Character Responses", test_multiple_characters)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
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
        print("🎉 All tests passed! Claude API integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main()) 