#!/usr/bin/env python3
"""
Test script for improved LangGraph architecture.
Demonstrates realistic news discovery and thread-based engagement.
"""
import asyncio
import logging
from datetime import datetime
from typing import List

from app.models.conversation import (
    NewsItem, ThreadEngagementState, create_orchestration_state
)
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.graphs.orchestrator import execute_orchestration_cycle
from app.graphs.character_workflow import execute_character_workflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_news_items() -> List[NewsItem]:
    """Create test news items for demonstration."""
    return [
        NewsItem(
            id="news_001",
            headline="Breaking: New Puerto Rican Music Festival Announced in San Juan",
            content="A major music festival featuring local and international artists will take place in San Juan next month. The event promises to showcase Puerto Rican culture and boost tourism.",
            topics=["music", "entertainment", "culture", "tourism", "san juan"],
            source="Puerto Rico Daily News",
            published_at=datetime.utcnow(),
            relevance_score=0.8
        ),
        NewsItem(
            id="news_002", 
            headline="Traffic Chaos in Bayamón: Major Construction Project Delays Commuters",
            content="Ongoing construction on Highway 22 in Bayamón is causing significant delays for morning commuters. The project is expected to continue for another 3 months.",
            topics=["traffic", "construction", "bayamón", "transportation", "daily life"],
            source="El Nuevo Día",
            published_at=datetime.utcnow(),
            relevance_score=0.6
        ),
        NewsItem(
            id="news_003",
            headline="Cultural Heritage: Restoration of Historic Buildings in Old San Juan",
            content="The government has announced funding for the restoration of several historic buildings in Old San Juan, preserving Puerto Rico's rich cultural heritage for future generations.",
            topics=["culture", "history", "old san juan", "heritage", "restoration"],
            source="Caribbean Business",
            published_at=datetime.utcnow(),
            relevance_score=0.7
        )
    ]


async def test_realistic_news_discovery():
    """Test the realistic news discovery flow."""
    logger.info("=== Testing Realistic News Discovery ===")
    
    # Create test news
    news_items = create_test_news_items()
    
    # Create orchestration state
    orchestration_state = create_orchestration_state(["jovani_vazquez"])
    
    # Add news items to queue
    for news in news_items:
        orchestration_state.pending_news_queue.append(news)
    
    logger.info(f"Added {len(news_items)} news items to queue")
    
    # Process news items one by one (realistic discovery)
    for i, news in enumerate(news_items):
        logger.info(f"\n--- Processing News {i+1}: {news.headline} ---")
        
        # Execute orchestration cycle for this news item
        result = await execute_orchestration_cycle(
            news_items=[news],
            existing_state=orchestration_state
        )
        
        # Check results
        if result["success"]:
            reactions = result.get("character_reactions", [])
            logger.info(f"Generated {len(reactions)} character reactions")
            
            for reaction in reactions:
                logger.info(f"  {reaction.character_name}: {reaction.content[:100]}...")
        else:
            logger.error(f"Orchestration failed: {result.get('error_details')}")
        
        # Small delay to simulate realistic timing
        await asyncio.sleep(1)


async def test_thread_based_engagement():
    """Test thread-based engagement with multiple characters."""
    logger.info("\n=== Testing Thread-Based Engagement ===")
    
    # Create a thread engagement state
    thread_state = ThreadEngagementState(
        thread_id="thread_001",
        original_content="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷"
    )
    
    # Create Jovani character
    jovani = create_jovani_vazquez()
    
    # Simulate Jovani discovering the news first
    logger.info("Jovani discovers the news and creates a new thread...")
    
    result1 = await execute_character_workflow(
        character_agent=jovani,
        input_context="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷",
        news_item=NewsItem(
            id="music_festival",
            headline="New Puerto Rican Music Festival Announced",
            content="A major music festival featuring local and international artists will take place in San Juan next month.",
            topics=["music", "entertainment", "culture"],
            source="Test",
            published_at=datetime.utcnow(),
            relevance_score=0.9
        ),
        conversation_history=[],
        target_topic="music"
    )
    
    if result1["success"] and result1.get("generated_response"):
        jovani_response = result1["generated_response"]
        logger.info(f"Jovani's response: {jovani_response}")
        
        # Add to thread state
        thread_state.add_character_reply("jovani_vazquez", jovani_response)
        
        # Now simulate another character seeing Jovani's reply and responding
        logger.info("\nAnother character sees Jovani's reply and responds...")
        
        # Create a simulated "other character" context
        thread_context = thread_state.get_thread_context("other_character")
        logger.info(f"Thread context: {thread_context}")
        
        # Simulate character workflow with thread context
        result2 = await execute_character_workflow(
            character_agent=jovani,  # Using Jovani again for demo
            input_context="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷",
            news_item=None,  # This is now a thread reply, not new news
            conversation_history=[],
            target_topic="music"
        )
        
        if result2["success"] and result2.get("generated_response"):
            thread_reply = result2["generated_response"]
            logger.info(f"Thread reply: {thread_reply}")
            
            # Check if character can still reply
            can_reply = thread_state.can_character_reply("jovani_vazquez")
            logger.info(f"Can Jovani reply again? {can_reply}")
            
            # Show thread state
            logger.info(f"Thread has {len(thread_state.character_replies)} characters with replies")
            for char_id, replies in thread_state.character_replies.items():
                logger.info(f"  {char_id}: {len(replies)} replies")


async def test_rate_limiting():
    """Test rate limiting per thread."""
    logger.info("\n=== Testing Rate Limiting ===")
    
    # Create thread state
    thread_state = ThreadEngagementState(
        thread_id="rate_limit_test",
        original_content="Test thread for rate limiting"
    )
    
    # Simulate multiple replies from same character
    for i in range(4):
        can_reply = thread_state.can_character_reply("test_character")
        logger.info(f"Reply attempt {i+1}: Can reply? {can_reply}")
        
        if can_reply:
            thread_state.add_character_reply("test_character", f"Reply {i+1}")
            logger.info(f"  Added reply {i+1}")
        else:
            logger.info(f"  Rate limited - cannot reply")
            break


async def main():
    """Run all tests."""
    logger.info("Starting LangGraph Architecture Tests")
    logger.info("=" * 50)
    
    try:
        # Test 1: Realistic news discovery
        await test_realistic_news_discovery()
        
        # Test 2: Thread-based engagement
        await test_thread_based_engagement()
        
        # Test 3: Rate limiting
        await test_rate_limiting()
        
        logger.info("\n" + "=" * 50)
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 