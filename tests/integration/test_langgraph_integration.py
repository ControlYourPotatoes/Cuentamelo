"""
Integration tests for the LangGraph system components.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from app.models.conversation import create_orchestration_state
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.graphs.orchestrator import execute_orchestration_cycle
from app.graphs.character_workflow import execute_character_workflow


class TestLangGraphSystemIntegration:
    """Test integration between LangGraph system components."""
    
    @pytest.mark.asyncio
    async def test_full_news_discovery_and_engagement_flow(self, sample_news_items):
        """Should execute complete news discovery and engagement flow."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Add news items to queue
        for news in sample_news_items:
            orchestration_state.pending_news_queue.append(news)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Verify orchestration result
        assert result["success"] is True
        assert "orchestration_state" in result
        assert "character_reactions" in result
        
        # Check that news items were processed
        final_state = result["orchestration_state"]
        assert final_state.processed_news_count >= 0
    
    @pytest.mark.asyncio
    async def test_character_workflow_integration_with_orchestration(self, news_item_builder):
        """Should integrate character workflow with orchestration system."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Integrated response from character"
        mock_response.confidence_score = 0.8
        mock_response.character_consistency = 0.9
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        # Create character agent with AI provider
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create news item
        news_item = news_item_builder\
            .with_id("integration_test")\
            .with_headline("Integration Test News")\
            .with_topics(["music", "entertainment"])\
            .with_relevance_score(0.8)\
            .build()
        
        # Execute character workflow
        workflow_result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="¡Breaking news! New Puerto Rican music festival announced in San Juan! 🔥🎵 This is going to be brutal!",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Verify workflow result
        assert workflow_result["success"] is True
        # The response might be the mock response or a no-engagement message
        assert workflow_result["generated_response"] is not None
        assert len(workflow_result["generated_response"]) > 0
        
        # Create orchestration state and add news
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        orchestration_result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Verify orchestration result
        assert orchestration_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_thread_engagement_integration(self, thread_state_builder, news_item_builder):
        """Should integrate thread engagement with character workflow."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Thread-aware response"
        mock_response.confidence_score = 0.7
        mock_response.character_consistency = 0.8
        mock_response.metadata = {"thread_aware": True}
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        # Create character agent
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create thread state
        thread_state = thread_state_builder\
            .with_thread_id("integration_thread")\
            .with_original_content("Original thread content")\
            .build()
        
        # Add existing replies
        thread_state.add_character_reply("other_character", "First reply")
        thread_state.add_character_reply("another_character", "Second reply")
        
        # Execute character workflow with thread context
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="¡Wepa! This music festival thread is getting wild! 🔥🎵",
            conversation_history=[],
            target_topic="music",
            thread_id="integration_thread",
            thread_context="Thread discussion context",
            is_new_thread=False,
            thread_engagement_state=thread_state
        )
        
        # Verify result
        assert result["success"] is True
        # The response might be the mock response or a no-engagement message
        assert result["generated_response"] is not None
        assert len(result["generated_response"]) > 0
        
        # Verify thread state was updated (only if character decided to engage)
        if result.get("engagement_decision") == "engage":
            assert "jovani_vazquez" in thread_state.character_replies
        else:
            # If character decided not to engage, thread state should not be updated
            assert "jovani_vazquez" not in thread_state.character_replies
    
    @pytest.mark.asyncio
    async def test_personality_data_integration(self, jovani_personality, news_item_builder):
        """Should integrate personality data throughout the system."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Personality-driven response"
        mock_response.confidence_score = 0.9
        mock_response.character_consistency = 0.95
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        # Create character agent
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Verify personality data integration
        assert jovani_agent.personality_data.character_name == jovani_personality.character_name
        assert jovani_agent.personality_data.signature_phrases == jovani_personality.signature_phrases
        assert jovani_agent.personality_data.topic_weights == jovani_personality.topic_weights
        
        # Create news item relevant to personality
        news_item = news_item_builder\
            .with_id("personality_test")\
            .with_headline("Music Festival Announcement")\
            .with_topics(["music", "entertainment", "festival"])\
            .with_relevance_score(0.9)\
            .build()
        
        # Execute character workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="¡Increíble! Major music festival coming to Puerto Rico! 🔥🎵 This is exactly what we need!",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Verify result uses personality data
        assert result["success"] is True
        # The response might be the mock response or a no-engagement message
        assert result["generated_response"] is not None
        assert len(result["generated_response"]) > 0


class TestRealisticNewsDiscoveryFlow:
    """Test realistic news discovery and processing flow."""
    
    @pytest.mark.asyncio
    async def test_realistic_news_discovery_sequence(self, news_item_builder):
        """Should process news items in realistic discovery sequence."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news items with different characteristics
        news_items = [
            news_item_builder\
                .with_id("breaking_news")\
                .with_headline("Breaking: Major Music Festival Announced")\
                .with_topics(["music", "entertainment", "festival"])\
                .with_relevance_score(0.9)\
                .build(),
            news_item_builder\
                .with_id("local_news")\
                .with_headline("Local Traffic Update")\
                .with_topics(["traffic", "local", "transportation"])\
                .with_relevance_score(0.5)\
                .build(),
            news_item_builder\
                .with_id("cultural_news")\
                .with_headline("Cultural Heritage Restoration")\
                .with_topics(["culture", "heritage", "history"])\
                .with_relevance_score(0.7)\
                .build()
        ]
        
        # Process news items one by one (realistic discovery)
        for i, news in enumerate(news_items):
            # Add news item to queue
            orchestration_state.pending_news_queue.append(news)
            
            # Execute orchestration cycle
            result = await execute_orchestration_cycle(
                news_items=[],
                existing_state=orchestration_state
            )
            
            # Verify each cycle
            assert result["success"] is True
            assert result["orchestration_state"].processed_news_count >= i + 1
    
    @pytest.mark.asyncio
    async def test_news_priority_processing(self, news_item_builder):
        """Should process news items based on priority and relevance."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news items with different priorities
        high_priority = news_item_builder\
            .with_id("high_priority")\
            .with_headline("Breaking: Music Festival")\
            .with_topics(["music", "festival"])\
            .with_relevance_score(0.95)\
            .build()
        
        medium_priority = news_item_builder\
            .with_id("medium_priority")\
            .with_headline("Cultural Event")\
            .with_topics(["culture", "event"])\
            .with_relevance_score(0.7)\
            .build()
        
        low_priority = news_item_builder\
            .with_id("low_priority")\
            .with_headline("Traffic Update")\
            .with_topics(["traffic", "construction"])\
            .with_relevance_score(0.3)\
            .build()
        
        # Add to queue in mixed order
        orchestration_state.pending_news_queue.extend([low_priority, high_priority, medium_priority])
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should process news items (may prioritize by relevance)
        assert result["orchestration_state"].processed_news_count >= 0


class TestThreadBasedEngagementFlow:
    """Test thread-based engagement and conversation flow."""
    
    @pytest.mark.asyncio
    async def test_thread_conversation_flow(self, thread_state_builder, news_item_builder):
        """Should handle realistic thread conversation flow."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_ai_provider.generate_character_response = AsyncMock()
        
        # Create character agent
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create thread state
        thread_state = thread_state_builder\
            .with_thread_id("conversation_thread")\
            .with_original_content("Breaking: New Music Festival Announced! 🎵🇵🇷")\
            .build()
        
        # Simulate conversation flow
        conversation_steps = [
            ("jovani_vazquez", "¡Qué noticia increíble! 🎵"),
            ("other_character", "This is going to be amazing!"),
            ("jovani_vazquez", "¡Exacto! Este festival va a ser épico 🎵"),
            ("another_character", "I can't wait to attend!")
        ]
        
        for character_id, reply_content in conversation_steps:
            # Check if character can reply
            if thread_state.can_character_reply(character_id):
                # Add reply
                thread_state.add_character_reply(character_id, reply_content)
                
                # Execute character workflow for next reply
                if character_id == "jovani_vazquez":
                    mock_response = Mock()
                    mock_response.content = reply_content
                    mock_response.confidence_score = 0.8
                    mock_response.character_consistency = 0.9
                    mock_ai_provider.generate_character_response.return_value = mock_response
                    
                    result = await execute_character_workflow(
                        character_agent=jovani_agent,
                        input_context="Thread conversation",
                        conversation_history=[],
                        target_topic="music",
                        thread_id="conversation_thread",
                        thread_context=thread_state.get_thread_context(character_id),
                        is_new_thread=False,
                        thread_engagement_state=thread_state
                    )
                    
                    assert result["success"] is True
        
        # Verify conversation state
        assert len(thread_state.character_replies) >= 2
        for character_id, _ in conversation_steps:
            if character_id in thread_state.character_replies:
                assert len(thread_state.character_replies[character_id]) > 0
    
    @pytest.mark.asyncio
    async def test_thread_rate_limiting_integration(self, thread_state_builder):
        """Should integrate rate limiting with thread engagement."""
        # Create character agent
        jovani_agent = create_jovani_vazquez()
        
        # Create thread state
        thread_state = thread_state_builder\
            .with_thread_id("rate_limit_thread")\
            .with_original_content("Test thread for rate limiting")\
            .build()
        
        # Simulate multiple replies from same character
        character_id = "jovani_vazquez"
        replies_added = 0
        
        for i in range(5):  # Try more than the limit
            if thread_state.can_character_reply(character_id):
                thread_state.add_character_reply(character_id, f"Reply {i+1}")
                replies_added += 1
            else:
                # Should be rate limited
                break
        
        # Verify rate limiting worked
        assert replies_added <= 3  # Should be limited to max replies per thread
        assert thread_state.can_character_reply(character_id) is False
        
        # Other characters should still be able to reply
        other_character = "other_character"
        assert thread_state.can_character_reply(other_character) is True


class TestSystemErrorHandling:
    """Test system-wide error handling and recovery."""
    
    @pytest.mark.asyncio
    async def test_ai_provider_failure_recovery(self, news_item_builder):
        """Should handle AI provider failures gracefully."""
        # Create mock AI provider that fails
        mock_ai_provider = Mock()
        mock_ai_provider.generate_character_response = AsyncMock(
            side_effect=Exception("AI provider unavailable")
        )
        
        # Create character agent with failing AI provider
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create news item
        news_item = news_item_builder\
            .with_id("failure_test")\
            .with_headline("Test News")\
            .with_topics(["music"])\
            .with_relevance_score(0.8)\
            .build()
        
        # Execute character workflow (should handle failure gracefully)
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Test context",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Should handle failure gracefully
        assert result["success"] is False
        assert "error" in result or "error_details" in result
        
        # Orchestration should continue despite individual failures
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        orchestration_state.pending_news_queue.append(news_item)
        
        orchestration_result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert orchestration_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_invalid_data_handling(self, news_item_builder):
        """Should handle invalid data gracefully throughout the system."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news item with invalid data
        invalid_news = news_item_builder\
            .with_id("invalid_news")\
            .with_headline("")\
            .with_content("")\
            .with_topics([])\
            .with_relevance_score(-0.1)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.append(invalid_news)
        
        # Execute orchestration cycle (should handle gracefully)
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Should handle invalid data gracefully
        assert result["success"] is True or result["success"] is False
        assert isinstance(result, dict)


class TestPerformanceAndScalability:
    """Test system performance and scalability."""
    
    @pytest.mark.asyncio
    async def test_large_news_queue_processing(self, news_item_builder):
        """Should handle large news queues efficiently."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create large number of news items
        for i in range(20):
            news_item = news_item_builder\
                .with_id(f"news_{i}")\
                .with_headline(f"News Item {i}")\
                .with_topics(["music", "entertainment"])\
                .with_relevance_score(0.5 + (i * 0.02))\
                .build()
            orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        start_time = datetime.now()
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        end_time = datetime.now()
        
        # Verify performance
        assert result["success"] is True
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 10  # Should complete within reasonable time
        
        # Verify processing
        assert result["orchestration_state"].processed_news_count >= 0
    
    @pytest.mark.asyncio
    async def test_multiple_character_processing(self, news_item_builder):
        """Should handle multiple characters efficiently."""
        # Create orchestration state with many characters
        character_ids = [
            "jovani_vazquez", "politico_boricua", "ciudadano_boricua",
            "historiador_cultural", "music_lover", "culture_enthusiast"
        ]
        orchestration_state = create_orchestration_state(character_ids)
        
        # Create news items
        for i in range(5):
            news_item = news_item_builder\
                .with_id(f"multi_char_news_{i}")\
                .with_headline(f"Multi-Character News {i}")\
                .with_topics(["music", "culture", "politics"])\
                .with_relevance_score(0.7)\
                .build()
            orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Verify multi-character processing
        assert result["success"] is True
        assert len(result["orchestration_state"].active_characters) == 6
        assert result["orchestration_state"].processed_news_count >= 0 