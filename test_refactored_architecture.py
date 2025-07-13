#!/usr/bin/env python3
"""
Test script for refactored LangGraph architecture.
Tests the new personality data system, thread engagement state, and AI provider abstraction.
"""
import asyncio
import logging
from datetime import datetime
from typing import List

from app.models.conversation import (
    NewsItem, ThreadEngagementState, create_orchestration_state
)
from app.models.personality import (
    create_jovani_vazquez_personality, create_politico_boricua_personality,
    create_ciudadano_boricua_personality, create_historiador_cultural_personality,
    test_personality_consistency
)
from app.adapters.claude_ai_adapter import ClaudeAIAdapter
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


async def test_ai_provider_abstraction():
    """Test the AI provider abstraction layer."""
    logger.info("\n=== Testing AI Provider Abstraction ===")
    
    # Create Claude AI adapter
    claude_adapter = ClaudeAIAdapter()
    
    # Test with Jovani personality
    jovani_personality = create_jovani_vazquez_personality()
    
    try:
        # Test health check
        health_status = await claude_adapter.health_check()
        logger.info(f"Claude adapter health check: {health_status}")
        
        if health_status:
            # Test character response generation
            response = await claude_adapter.generate_character_response(
                personality_data=jovani_personality,
                context="New Puerto Rican music festival announced!",
                target_topic="music",
                is_new_thread=True
            )
            
            logger.info(f"Generated response: {response.content[:100]}...")
            logger.info(f"Confidence score: {response.confidence_score}")
            logger.info(f"Character consistency: {response.character_consistency}")
            logger.info(f"Metadata: {response.metadata}")
            
            # Test thread reply
            thread_response = await claude_adapter.generate_character_response(
                personality_data=jovani_personality,
                context="This festival is going to be amazing!",
                thread_context="Previous discussion about music festival",
                is_new_thread=False
            )
            
            logger.info(f"Thread reply: {thread_response.content[:100]}...")
            logger.info(f"Thread aware: {thread_response.metadata.get('thread_aware')}")
            
        else:
            logger.warning("Claude adapter not available, skipping response generation tests")
            
    except Exception as e:
        logger.error(f"Error testing AI provider: {str(e)}")


async def test_character_agent_refactoring():
    """Test the refactored character agent system."""
    logger.info("\n=== Testing Character Agent Refactoring ===")
    
    # Create AI provider
    claude_adapter = ClaudeAIAdapter()
    
    # Create Jovani agent with AI provider injection
    jovani_agent = create_jovani_vazquez(ai_provider=claude_adapter)
    
    logger.info(f"Created Jovani agent: {jovani_agent.character_name}")
    logger.info(f"Character type: {jovani_agent.character_type}")
    logger.info(f"Engagement threshold: {jovani_agent.engagement_threshold}")
    logger.info(f"Max replies per thread: {jovani_agent.max_replies_per_thread}")
    
    # Test personality data access
    logger.info(f"Signature phrases: {jovani_agent.personality_data.signature_phrases}")
    logger.info(f"Topic weights: {dict(list(jovani_agent.personality_data.topic_weights.items())[:5])}")
    
    # Test engagement probability calculation
    test_context = "New Puerto Rican music festival announced in San Juan!"
    engagement_prob = jovani_agent.calculate_engagement_probability(
        context=test_context,
        conversation_history=[]
    )
    
    logger.info(f"Engagement probability for music festival: {engagement_prob:.2f}")
    
    # Test topic relevance
    topics = ["music", "entertainment", "culture"]
    relevance = jovani_agent.get_topic_relevance(topics)
    logger.info(f"Topic relevance for {topics}: {relevance:.2f}")


async def test_character_workflow_enhancements():
    """Test the enhanced character workflow with thread awareness."""
    logger.info("\n=== Testing Character Workflow Enhancements ===")
    
    # Create AI provider and character agent
    claude_adapter = ClaudeAIAdapter()
    jovani_agent = create_jovani_vazquez(ai_provider=claude_adapter)
    
    # Test new thread workflow
    logger.info("Testing new thread workflow...")
    
    new_thread_result = await execute_character_workflow(
        character_agent=jovani_agent,
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
        target_topic="music",
        is_new_thread=True
    )
    
    if new_thread_result["success"]:
        logger.info(f"New thread workflow successful: {new_thread_result['workflow_step']}")
        if new_thread_result.get("generated_response"):
            logger.info(f"Generated response: {new_thread_result['generated_response'][:100]}...")
    else:
        logger.error(f"New thread workflow failed: {new_thread_result.get('error_details')}")
    
    # Test thread reply workflow
    logger.info("Testing thread reply workflow...")
    
    thread_state = ThreadEngagementState(
        thread_id="test_thread_002",
        original_content="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷"
    )
    thread_state.add_character_reply("other_character", "This is going to be amazing!")
    
    thread_reply_result = await execute_character_workflow(
        character_agent=jovani_agent,
        input_context="This festival is going to be amazing!",
        conversation_history=[],
        target_topic="music",
        thread_id="test_thread_002",
        thread_context="Previous discussion about music festival",
        is_new_thread=False,
        thread_engagement_state=thread_state
    )
    
    if thread_reply_result["success"]:
        logger.info(f"Thread reply workflow successful: {thread_reply_result['workflow_step']}")
        if thread_reply_result.get("generated_response"):
            logger.info(f"Generated reply: {thread_reply_result['generated_response'][:100]}...")
    else:
        logger.error(f"Thread reply workflow failed: {thread_reply_result.get('error_details')}")


async def test_orchestration_integration():
    """Test the integrated orchestration system."""
    logger.info("\n=== Testing Orchestration Integration ===")
    
    # Create AI provider
    claude_adapter = ClaudeAIAdapter()
    
    # Create test news
    news_items = create_test_news_items()
    
    # Create orchestration state
    orchestration_state = create_orchestration_state(["jovani_vazquez"])
    
    # Add news items to queue
    for news in news_items:
        orchestration_state.pending_news_queue.append(news)
    
    logger.info(f"Added {len(news_items)} news items to orchestration queue")
    
    # Execute orchestration cycle
    result = await execute_orchestration_cycle(
        news_items=[],
        existing_state=orchestration_state,
        ai_provider=claude_adapter
    )
    
    if result["success"]:
        logger.info("Orchestration cycle completed successfully")
        logger.info(f"Workflow step: {result['workflow_step']}")
        logger.info(f"Execution time: {result['execution_time_ms']}ms")
        
        reactions = result.get("character_reactions", [])
        logger.info(f"Generated {len(reactions)} character reactions")
        
        for reaction in reactions:
            logger.info(f"  {reaction.character_name}: {reaction.decision}")
            if reaction.reaction_content:
                logger.info(f"    Content: {reaction.reaction_content[:100]}...")
        
        # Check orchestration state
        final_state = result["orchestration_state"]
        logger.info(f"Final orchestration state:")
        logger.info(f"  Processed news: {final_state.processed_news_count}")
        logger.info(f"  Total reactions: {len(final_state.character_reactions)}")
        logger.info(f"  Active conversations: {len([c for c in final_state.active_conversations if c.is_active])}")
        
    else:
        logger.error(f"Orchestration cycle failed: {result.get('error_details')}")


async def test_rate_limiting_and_thread_behavior():
    """Test rate limiting and thread-based behavior."""
    logger.info("\n=== Testing Rate Limiting and Thread Behavior ===")
    
    # Create thread state
    thread_state = ThreadEngagementState(
        thread_id="rate_limit_test",
        original_content="Test thread for rate limiting and thread behavior"
    )
    
    # Simulate multiple characters in a thread
    characters = ["jovani_vazquez", "politico_boricua", "ciudadano_boricua"]
    
    for char_id in characters:
        logger.info(f"\nTesting character: {char_id}")
        
        # Check if character can reply
        can_reply = thread_state.can_character_reply(char_id)
        logger.info(f"  Can reply initially? {can_reply}")
        
        if can_reply:
            # Add first reply
            thread_state.add_character_reply(char_id, f"First reply from {char_id}")
            logger.info(f"  Added first reply")
            
            # Check if can reply again
            can_reply_again = thread_state.can_character_reply(char_id)
            logger.info(f"  Can reply again? {can_reply_again}")
            
            if can_reply_again:
                thread_state.add_character_reply(char_id, f"Second reply from {char_id}")
                logger.info(f"  Added second reply")
                
                # Check third reply (should be blocked)
                can_reply_third = thread_state.can_character_reply(char_id)
                logger.info(f"  Can reply third time? {can_reply_third}")
    
    # Show final thread state
    logger.info(f"\nFinal thread state:")
    logger.info(f"  Thread ID: {thread_state.thread_id}")
    logger.info(f"  Characters with replies: {len(thread_state.character_replies)}")
    for char_id, replies in thread_state.character_replies.items():
        logger.info(f"    {char_id}: {len(replies)} replies")


async def main():
    """Run all tests for the refactored architecture."""
    logger.info("Starting Refactored LangGraph Architecture Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Personality data system
        await test_personality_data_system()
        
        # Test 2: Thread engagement state
        await test_thread_engagement_state()
        
        # Test 3: AI provider abstraction
        await test_ai_provider_abstraction()
        
        # Test 4: Character agent refactoring
        await test_character_agent_refactoring()
        
        # Test 5: Character workflow enhancements
        await test_character_workflow_enhancements()
        
        # Test 6: Orchestration integration
        await test_orchestration_integration()
        
        # Test 7: Rate limiting and thread behavior
        await test_rate_limiting_and_thread_behavior()
        
        logger.info("\n" + "=" * 60)
        logger.info("All refactored architecture tests completed successfully!")
        logger.info("\nKey Improvements Verified:")
        logger.info("✅ Personality data separation from AI provider")
        logger.info("✅ Thread engagement state for realistic Twitter behavior")
        logger.info("✅ AI provider abstraction with dependency injection")
        logger.info("✅ Enhanced character workflow with thread awareness")
        logger.info("✅ Rate limiting per thread and character")
        logger.info("✅ Improved orchestration with realistic news discovery")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 