#!/usr/bin/env python3
"""
Simplified test script for personality system only.
Tests the new personality data system without requiring AI provider setup.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from app.models.conversation import (
    NewsItem, ThreadEngagementState, create_orchestration_state
)
from app.models.personality import (
    create_jovani_vazquez_personality, create_politico_boricua_personality,
    create_ciudadano_boricua_personality, create_historiador_cultural_personality,
    test_personality_consistency, PersonalityTone
)

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
            published_at=datetime.now(timezone.utc),
            relevance_score=0.8
        ),
        NewsItem(
            id="news_002", 
            headline="Traffic Chaos in Bayamón: Major Construction Project Delays Commuters",
            content="Ongoing construction on Highway 22 in Bayamón is causing significant delays for morning commuters. The project is expected to continue for another 3 months.",
            topics=["traffic", "construction", "bayamón", "transportation", "daily life"],
            source="El Nuevo Día",
            published_at=datetime.now(timezone.utc),
            relevance_score=0.6
        ),
        NewsItem(
            id="news_003",
            headline="Cultural Heritage: Restoration of Historic Buildings in Old San Juan",
            content="The government has announced funding for the restoration of several historic buildings in Old San Juan, preserving Puerto Rico's rich cultural heritage for future generations.",
            topics=["culture", "history", "old san juan", "heritage", "restoration"],
            source="Caribbean Business",
            published_at=datetime.now(timezone.utc),
            relevance_score=0.7
        )
    ]


async def test_personality_data_system():
    """Test the new personality data system."""
    logger.info("=== Testing Personality Data System ===")
    
    # Test Jovani Vázquez personality
    jovani_personality = create_jovani_vazquez_personality()
    logger.info(f"Created Jovani personality: {jovani_personality.character_name}")
    logger.info(f"Signature phrases: {jovani_personality.signature_phrases}")
    logger.info(f"Engagement threshold: {jovani_personality.engagement_threshold}")
    
    # Test personality consistency
    consistency_result = test_personality_consistency(jovani_personality)
    logger.info(f"Personality consistency test: {consistency_result}")
    
    # Test other personalities
    politico_personality = create_politico_boricua_personality()
    ciudadano_personality = create_ciudadano_boricua_personality()
    historiador_personality = create_historiador_cultural_personality()
    
    logger.info(f"Created {politico_personality.character_name}: {politico_personality.character_type}")
    logger.info(f"Created {ciudadano_personality.character_name}: {ciudadano_personality.character_type}")
    logger.info(f"Created {historiador_personality.character_name}: {historiador_personality.character_type}")
    
    # Test personality differences
    logger.info(f"Jovani energy level: {jovani_personality.base_energy_level}")
    logger.info(f"Político energy level: {politico_personality.base_energy_level}")
    logger.info(f"Ciudadano energy level: {ciudadano_personality.base_energy_level}")
    logger.info(f"Historiador energy level: {historiador_personality.base_energy_level}")
    
    # Test tone preferences
    logger.info(f"Jovani tone preferences: {jovani_personality.tone_preferences}")
    logger.info(f"Historiador tone preferences: {historiador_personality.tone_preferences}")
    
    # Test that PASSIONATE tone exists
    logger.info(f"Available PersonalityTone values: {[tone.value for tone in PersonalityTone]}")
    logger.info(f"PASSIONATE tone exists: {PersonalityTone.PASSIONATE}")


async def test_thread_engagement_state():
    """Test the thread engagement state system."""
    logger.info("\n=== Testing Thread Engagement State ===")
    
    # Create a thread engagement state
    thread_state = ThreadEngagementState(
        thread_id="test_thread_001",
        original_content="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷"
    )
    
    logger.info(f"Created thread: {thread_state.thread_id}")
    logger.info(f"Original content: {thread_state.original_content}")
    
    # Test character reply limits
    character_id = "jovani_vazquez"
    
    for i in range(4):
        can_reply = thread_state.can_character_reply(character_id)
        logger.info(f"Reply attempt {i+1}: Can reply? {can_reply}")
        
        if can_reply:
            reply_content = f"Reply {i+1} from {character_id}"
            thread_state.add_character_reply(character_id, reply_content)
            logger.info(f"  Added reply: {reply_content}")
        else:
            logger.info(f"  Rate limited - cannot reply")
            break
    
    # Test thread context
    thread_context = thread_state.get_thread_context(character_id)
    logger.info(f"Thread context for {character_id}: {thread_context}")
    
    # Test multiple characters
    other_character = "politico_boricua"
    thread_state.add_character_reply(other_character, "Response from político")
    logger.info(f"Added reply from {other_character}")
    
    logger.info(f"Total characters with replies: {len(thread_state.character_replies)}")


async def test_news_processing():
    """Test news item processing."""
    logger.info("\n=== Testing News Processing ===")
    
    news_items = create_test_news_items()
    
    for i, news in enumerate(news_items, 1):
        logger.info(f"News {i}: {news.headline}")
        logger.info(f"  Topics: {news.topics}")
        logger.info(f"  Relevance score: {news.relevance_score}")
        logger.info(f"  Source: {news.source}")


async def main():
    """Run all tests."""
    logger.info("Starting Personality System Tests")
    logger.info("=" * 60)
    
    try:
        await test_personality_data_system()
        await test_thread_engagement_state()
        await test_news_processing()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main()) 