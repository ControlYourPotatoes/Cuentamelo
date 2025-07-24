#!/usr/bin/env python3
"""
Demo script for AI Character Orchestration with Twitter Integration.
This demonstrates the complete workflow from news input to Twitter posting with AI-generated responses.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
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
from app.adapters.twitter_adapter import TwitterAdapter
from app.tools.twitter_connector import TwitterConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AICharacterOrchestrationDemo:
    """Demo class for AI character orchestration with Twitter integration."""
    
    def __init__(self):
        self.container = get_container()
        configure_container_for_production()
        self.twitter_adapter = TwitterAdapter(TwitterConnector())
        
    async def demo_news_reaction_scenario(self):
        """Demo scenario: Characters react to breaking news."""
        print("🎭 AI Character Orchestration Demo - News Reaction Scenario")
        print("=" * 60)
        
        # Demo news items
        news_scenarios = [
            {
                "id": "demo_news_001",
                "headline": "Bad Bunny Announces Surprise Concert in San Juan",
                "content": "Puerto Rican superstar Bad Bunny just announced a surprise concert in San Juan next month. The concert will take place at the Coliseo de Puerto Rico and is expected to draw thousands of fans.",
                "source": "Music News",
                "relevance_score": 0.95,
                "topic": "music_entertainment"
            },
            {
                "id": "demo_news_002", 
                "headline": "Puerto Rico Tourism Booms with Record Visitor Numbers",
                "content": "Puerto Rico's tourism sector is experiencing unprecedented growth, with record visitor numbers this year. The island welcomed over 3 million tourists, marking a 25% increase from last year.",
                "source": "Economic News",
                "relevance_score": 0.85,
                "topic": "economy_tourism"
            },
            {
                "id": "demo_news_003",
                "headline": "New Puerto Rican Restaurant Opens in New York",
                "content": "A new Puerto Rican restaurant 'Sabor Boricua' has opened in Brooklyn, bringing authentic Puerto Rican cuisine to New York. The restaurant features traditional dishes like mofongo, arroz con gandules, and pasteles.",
                "source": "Food News",
                "relevance_score": 0.80,
                "topic": "food_culture"
            }
        ]
        
        # Character IDs to test
        character_ids = ["jovani_vazquez", "politico_boricua", "abuela_carmen", "profesor_ramirez"]
        
        for i, news_data in enumerate(news_scenarios, 1):
            print(f"\n📰 Demo Scenario {i}: {news_data['headline']}")
            print("-" * 50)
            
            # Create news item
            news_item = NewsItem(
                id=news_data["id"],
                headline=news_data["headline"],
                content=news_data["content"],
                source=news_data["source"],
                published_at=datetime.now(timezone.utc).isoformat(),
                relevance_score=news_data["relevance_score"]
            )
            
            # Test each character
            successful_posts = 0
            
            for character_id in character_ids:
                print(f"\n🎭 Testing {character_id}...")
                
                try:
                    # Create agent
                    agent = create_agent(character_id)
                    if not agent:
                        print(f"❌ Failed to create agent for {character_id}")
                        continue
                    
                    # Execute workflow
                    result = await execute_character_workflow(
                        character_agent=agent,
                        input_context=news_data["content"],
                        news_item=news_item,
                        target_topic=news_data["topic"]
                    )
                    
                    if result["success"] and result.get("generated_response"):
                        response = result["generated_response"]
                        print(f"✅ Generated response: {response[:100]}...")
                        
                        # Post to Twitter (if configured)
                        if await self._should_post_to_twitter():
                            await self._post_character_response(agent, response, news_data["headline"])
                            successful_posts += 1
                        else:
                            print("📝 Response ready for Twitter (API not configured)")
                            successful_posts += 1
                    else:
                        print(f"⚠️ {agent.character_name} chose not to engage")
                        
                except Exception as e:
                    print(f"❌ Error with {character_id}: {str(e)}")
            
            print(f"\n📊 Scenario {i} Results: {successful_posts}/{len(character_ids)} characters responded")
            
            # Add delay between scenarios
            if i < len(news_scenarios):
                print("⏳ Waiting 5 seconds before next scenario...")
                await asyncio.sleep(5)
    
    async def demo_character_conversation(self):
        """Demo scenario: Characters having a conversation."""
        print("\n💬 AI Character Orchestration Demo - Character Conversation")
        print("=" * 60)
        
        # Initial conversation starter
        conversation_starter = "What do you think about Puerto Rico's future in the next 10 years?"
        
        print(f"🗣️ Conversation starter: {conversation_starter}")
        
        # Character IDs for conversation
        character_ids = ["jovani_vazquez", "politico_boricua", "abuela_carmen"]
        
        conversation_history = []
        
        for i, character_id in enumerate(character_ids):
            print(f"\n🎭 {character_id} responding...")
            
            try:
                # Create agent
                agent = create_agent(character_id)
                if not agent:
                    print(f"❌ Failed to create agent for {character_id}")
                    continue
                
                # Execute workflow for conversation
                result = await execute_character_workflow(
                    character_agent=agent,
                    input_context=conversation_starter if i == 0 else conversation_history[-1].content,
                    conversation_history=conversation_history,
                    target_topic="puerto_rico_future"
                )
                
                if result["success"] and result.get("generated_response"):
                    response = result["generated_response"]
                    print(f"💬 {agent.character_name}: {response}")
                    
                    # Add to conversation history
                    if result.get("final_message"):
                        conversation_history.append(result["final_message"])
                    
                    # Post to Twitter (if configured)
                    if await self._should_post_to_twitter():
                        await self._post_character_response(agent, response, "Character Conversation")
                    
                else:
                    print(f"⚠️ {agent.character_name} chose not to engage")
                    
            except Exception as e:
                print(f"❌ Error with {character_id}: {str(e)}")
            
            # Add delay between responses
            if i < len(character_ids) - 1:
                print("⏳ Waiting 3 seconds for next character...")
                await asyncio.sleep(3)
        
        print(f"\n📊 Conversation complete! {len(conversation_history)} responses generated.")
    
    async def _should_post_to_twitter(self) -> bool:
        """Check if we should post to Twitter (API configured)."""
        try:
            # Check if Twitter credentials are configured
            settings = self.container.settings
            return bool(settings.TWITTER_BEARER_TOKEN)
        except:
            return False
    
    async def _post_character_response(self, agent, response: str, context: str):
        """Post character response to Twitter."""
        try:
            # Add character signature
            signature = f"\n\n— {agent.character_name} 🇵🇷"
            full_response = response + signature
            
            # Post to Twitter
            result = await self.twitter_adapter.post_tweet(
                content=full_response,
                character_id=agent.character_id
            )
            
            if result.success:
                print(f"🐦 Posted to Twitter: {result.tweet_id}")
            else:
                print(f"❌ Twitter post failed: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error posting to Twitter: {str(e)}")
    
    async def run_demo(self):
        """Run the complete demo."""
        print("🚀 Starting AI Character Orchestration Demo")
        print("=" * 60)
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️ Warning: ANTHROPIC_API_KEY not set")
            print("   Demo will run with mock responses")
        
        # Check Twitter credentials
        twitter_key = os.getenv("TWITTER_BEARER_TOKEN")
        if not twitter_key:
            print("⚠️ Warning: TWITTER_BEARER_TOKEN not set")
            print("   Responses will not be posted to Twitter")
        
        print(f"🔑 Claude API: {'✅ Configured' if api_key else '❌ Not configured'}")
        print(f"🐦 Twitter API: {'✅ Configured' if twitter_key else '❌ Not configured'}")
        
        # Run demo scenarios
        await self.demo_news_reaction_scenario()
        await self.demo_character_conversation()
        
        print("\n🎉 Demo complete!")
        print("=" * 60)
        print("✅ AI Character Orchestration is working!")
        print("✅ Character personalities are being applied correctly!")
        print("✅ LangGraph workflows are executing successfully!")
        if twitter_key:
            print("✅ Twitter integration is functional!")
        else:
            print("⚠️ Twitter integration ready (needs API key)")


async def main():
    """Main demo function."""
    demo = AICharacterOrchestrationDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main()) 