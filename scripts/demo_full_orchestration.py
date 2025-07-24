#!/usr/bin/env python3
"""
Full Orchestration Demo Script
==============================

This script demonstrates the complete Cuentamelo system:
1. News Discovery (simulated)
2. Jovani's AI reaction and decision making
3. Twitter posting (simulated for demo)

Perfect for video demonstrations and hackathon presentations.
"""
import asyncio
import sys
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.dependency_container import DependencyContainer
from app.agents.agent_factory import create_agent
from app.graphs.character_workflow import execute_character_workflow
from app.ports.twitter_provider import TwitterPostResult, TwitterPostStatus, TwitterPost


class DemoOrchestrator:
    """Demo orchestrator for showcasing the full system flow."""
    
    def __init__(self):
        self.container = DependencyContainer({
            "news_provider": "simulated",  # Mock news for demo
            "twitter_provider": "twitter"  # Real Twitter posting
        })
        self.jovani = None
        self.news_provider = None
        self.twitter_provider = None
        
    async def setup(self):
        """Initialize all components."""
        print("🔧 Setting up Cuentamelo Demo System...")
        print("=" * 60)
        
        # Initialize news provider
        self.news_provider = self.container.get_news_provider()
        print(f"📰 News Provider: {self.news_provider.__class__.__name__}")
        
        # Initialize Twitter provider (real for demo)
        self.twitter_provider = self.container.get_twitter_provider()
        print(f"🐦 Twitter Provider: {self.twitter_provider.__class__.__name__}")
        
        # Create Jovani agent
        ai_provider = self.container.get_ai_provider()
        self.jovani = create_agent("jovani_vazquez", ai_provider=ai_provider)
        print(f"🤖 Jovani Agent: {self.jovani.character_name}")
        
        print("✅ System setup complete!")
        print()
        
    async def discover_news(self) -> List[Any]:
        """Discover latest news items."""
        print("📰 STEP 1: Discovering Latest News")
        print("-" * 40)
        
        if not self.news_provider:
            print("❌ News provider not initialized!")
            return []
        
        news_items = await self.news_provider.discover_latest_news(max_results=3)
        
        if not news_items:
            print("❌ No news items found!")
            return []
        
        print(f"✅ Found {len(news_items)} news items:")
        for i, item in enumerate(news_items, 1):
            print(f"   {i}. {item.headline}")
            print(f"      Source: {item.source}")
            print(f"      Relevance: {item.relevance_score:.2f}")
            print(f"      Topics: {', '.join(item.topics) if item.topics else 'None'}")
            print()
        
        return news_items
    
    async def process_news_with_jovani(self, news_item: Any) -> Dict[str, Any]:
        """Process a news item with Jovani's AI workflow."""
        print(f"🤖 STEP 2: Jovani's AI Analysis")
        print("-" * 40)
        print(f"📰 Processing: {news_item.headline}")
        print(f"📝 Content: {news_item.content[:100]}...")
        print()
        
        if not self.jovani:
            print("❌ Jovani agent not initialized!")
            return {"success": False, "error": "Agent not initialized"}
        
        # Execute character workflow
        result = await execute_character_workflow(
            character_agent=self.jovani,
            input_context=news_item.content,
            news_item=news_item,
            target_topic=None,
            is_new_thread=True,
            thread_engagement_state=None
        )
        
        # Convert result to dict for type safety
        result_dict = {
            "success": result["success"],
            "engagement_decision": result.get("engagement_decision"),
            "generated_response": result.get("generated_response"),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "error": result.get("error"),
            "agent_state": result.get("agent_state")
        }
        
        if result_dict["success"]:
            print(f"✅ Decision: {result_dict.get('engagement_decision', 'unknown')}")
            agent_state = result_dict.get('agent_state')
            if agent_state:
                print(f"🎯 Confidence: {agent_state.decision_confidence:.2f}")
            print(f"⏱️  Processing Time: {result_dict.get('execution_time_ms', 0)}ms")
            
            if result_dict.get("generated_response"):
                print(f"💬 Jovani's Response:")
                print(f"   \"{result_dict['generated_response']}\"")
                return result_dict
            else:
                print("🤐 Jovani chose not to respond")
                return result_dict
        else:
            print(f"❌ Workflow failed: {result_dict.get('error', 'Unknown error')}")
            return result_dict
    
    async def post_to_twitter(self, response: str, news_item: Any) -> TwitterPostResult:
        """Post Jovani's response to Twitter (simulated for demo)."""
        print(f"🐦 STEP 3: Twitter Posting")
        print("-" * 40)
        
        # Create a formatted tweet with context
        tweet_content = self._format_tweet(response, news_item)
        print(f"📝 Tweet Content:")
        print(f"   \"{tweet_content}\"")
        print()
        
        # Post to Twitter (real posting)
        if not self.twitter_provider:
            print("❌ Twitter provider not initialized!")
            return TwitterPostResult(
                success=False,
                post=TwitterPost(
                    content=tweet_content,
                    character_id="jovani_vazquez",
                    character_name="Jovani Vázquez",
                    status=TwitterPostStatus.FAILED
                ),
                error_message="Twitter provider not initialized"
            )
        
        result = await self.twitter_provider.post_tweet(
            content=tweet_content,
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez",
            reply_to_tweet_id=None,
            quote_tweet_id=None,
            thread_id=None
        )
        
        if result.success:
            print(f"✅ Tweet posted successfully!")
            print(f"   Tweet ID: {result.twitter_tweet_id}")
            print(f"   Status: {result.post.status}")
            if result.rate_limit_info:
                print(f"   Rate Limit: {result.rate_limit_info.remaining}/{result.rate_limit_info.limit}")
        else:
            print(f"❌ Tweet posting failed: {result.error_message}")
        
        return result
    
    def _format_tweet(self, response: str, news_item: Any) -> str:
        """Format the tweet content with news context."""
        # Truncate response if too long
        max_length = 200  # Leave room for context
        if len(response) > max_length:
            response = response[:max_length] + "..."
        
        # Add news context
        context = f"📰 {news_item.headline[:50]}..."
        tweet = f"{response}\n\n{context}"
        
        # Ensure we don't exceed Twitter's limit
        if len(tweet) > 280:
            # Truncate more aggressively
            available_space = 280 - len(context) - 10  # Leave space for "..."
            response = response[:available_space] + "..."
            tweet = f"{response}\n\n{context}"
        
        return tweet
    
    async def run_full_demo(self):
        """Run the complete demo orchestration."""
        print("🎭 CUENTAMELO - Full System Demo")
        print("=" * 60)
        print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
        print()
        
        try:
            # Setup system
            await self.setup()
            
            # Discover news
            news_items = await self.discover_news()
            if not news_items:
                print("❌ No news to process. Demo ending.")
                return
            
            # Process each news item
            successful_posts = 0
            total_items = len(news_items)
            
            for i, news_item in enumerate(news_items, 1):
                print(f"\n🔄 Processing News Item {i}/{total_items}")
                print("=" * 60)
                
                # Step 1: Process with Jovani
                result = await self.process_news_with_jovani(news_item)
                
                if result.get("success") and result.get("generated_response"):
                    # Step 2: Post to Twitter
                    twitter_result = await self.post_to_twitter(
                        result["generated_response"], 
                        news_item
                    )
                    
                    if twitter_result.success:
                        successful_posts += 1
                    
                    # Add delay between posts for demo effect
                    if i < total_items:
                        print(f"\n⏳ Waiting 3 seconds before next item...")
                        await asyncio.sleep(3)
                else:
                    print("⏭️  Skipping Twitter post (no response generated)")
                
                print()
            
            # Demo summary
            print("🎉 DEMO COMPLETED!")
            print("=" * 60)
            print(f"📊 Summary:")
            print(f"   Total News Items: {total_items}")
            print(f"   Successful Posts: {successful_posts}")
            print(f"   Success Rate: {(successful_posts/total_items)*100:.1f}%")
            print()
            print("🎯 Demo Highlights:")
            print("   ✅ News discovery from simulated sources")
            print("   ✅ AI-powered character decision making")
            print("   ✅ Contextual response generation")
            print("   ✅ Real Twitter posting integration")
            print("   ✅ Full orchestration workflow")
            print()
            print("🚀 Ready for production deployment!")
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


async def run_interactive_demo():
    """Run an interactive demo with user input."""
    print("🎭 CUENTAMELO - Interactive Demo")
    print("=" * 60)
    print("This demo allows you to inject custom news and see Jovani's reactions.")
    print()
    
    orchestrator = DemoOrchestrator()
    await orchestrator.setup()
    
    while True:
        print("\n📝 Enter custom news (or 'quit' to exit):")
        print("-" * 40)
        
        headline = input("Headline: ").strip()
        if headline.lower() == 'quit':
            break
        
        content = input("Content: ").strip()
        if not content:
            print("❌ Content is required!")
            continue
        
        source = input("Source (optional): ").strip() or "Demo News"
        topics = input("Topics (comma-separated, optional): ").strip()
        topics_list = [t.strip() for t in topics.split(",")] if topics else []
        
        # Create custom news item
        if not orchestrator.news_provider:
            print("❌ News provider not initialized!")
            continue
        
        news_item = await orchestrator.news_provider.ingest_news_item(
            headline=headline,
            content=content,
            source=source,
            tags=topics_list,
            relevance_score=0.8
        )
        
        print(f"\n🔄 Processing custom news...")
        print("=" * 60)
        
        # Process with Jovani
        result = await orchestrator.process_news_with_jovani(news_item)
        
        if result.get("success") and result.get("generated_response"):
            # Ask if user wants to post to Twitter
            post_choice = input("\n🐦 Post to Twitter? (y/n): ").strip().lower()
            if post_choice == 'y':
                await orchestrator.post_to_twitter(result["generated_response"], news_item)
        
        print("\n" + "="*60)
    
    print("👋 Demo ended. Thanks for trying Cuentamelo!")


async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await run_interactive_demo()
    else:
        # Use real Twitter posting (this is the main demo)
        orchestrator = DemoOrchestrator()
        await orchestrator.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main()) 