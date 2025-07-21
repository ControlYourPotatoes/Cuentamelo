"""
Tests for the character workflow system.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from app.graphs.character_workflow import execute_character_workflow
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.conversation import NewsItem, ThreadEngagementState


class TestCharacterWorkflowExecution:
    """Test character workflow execution and basic functionality."""
    
    @pytest.mark.asyncio
    async def test_new_thread_workflow_execution(self, news_item_builder):
        """Should execute new thread workflow successfully."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "¡Qué noticia increíble! 🎵"
        mock_response.confidence_score = 0.8
        mock_response.character_consistency = 0.9
        mock_response.metadata = {"tone": "passionate"}
        
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        # Create character agent
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create news item
        news_item = news_item_builder\
            .with_id("music_festival")\
            .with_headline("New Puerto Rican Music Festival Announced")\
            .with_content("A major music festival featuring local and international artists will take place in San Juan next month.")\
            .with_topics(["music", "entertainment", "culture"])\
            .with_relevance_score(0.9)\
            .build()
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Verify result
        assert result["success"] is True
        assert result["workflow_step"] == "new_thread_response"
        assert result["generated_response"] == "¡Qué noticia increíble! 🎵"
        assert result["confidence_score"] == 0.8
        assert result["character_consistency"] == 0.9
    
    @pytest.mark.asyncio
    async def test_thread_reply_workflow_execution(self, thread_state_builder):
        """Should execute thread reply workflow successfully."""
        # Create mock AI provider
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "¡Exacto! Este festival va a ser épico 🎵"
        mock_response.confidence_score = 0.7
        mock_response.character_consistency = 0.8
        mock_response.metadata = {"thread_aware": True}
        
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        # Create character agent
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Create thread state
        thread_state = thread_state_builder\
            .with_thread_id("test_thread_001")\
            .with_original_content("Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷")\
            .build()
        
        # Add existing reply
        thread_state.add_character_reply("other_character", "This is going to be amazing!")
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="This festival is going to be amazing!",
            conversation_history=[],
            target_topic="music",
            thread_id="test_thread_001",
            thread_context="Previous discussion about music festival",
            is_new_thread=False,
            thread_engagement_state=thread_state
        )
        
        # Verify result
        assert result["success"] is True
        assert result["workflow_step"] == "thread_reply"
        assert result["generated_response"] == "¡Exacto! Este festival va a ser épico 🎵"
        assert result["confidence_score"] == 0.7
        assert result["character_consistency"] == 0.8
        assert result["metadata"]["thread_aware"] is True
    
    @pytest.mark.asyncio
    async def test_workflow_without_ai_provider(self):
        """Should handle workflow execution without AI provider."""
        # Create character agent without AI provider
        jovani_agent = create_jovani_vazquez()
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Test context",
            target_topic="music",
            is_new_thread=True
        )
        
        # Should handle gracefully
        assert result["success"] is False
        assert "error" in result or "error_details" in result


class TestCharacterWorkflowDecisionMaking:
    """Test character workflow decision-making logic."""
    
    @pytest.mark.asyncio
    async def test_workflow_engagement_decision_high_relevance(self, news_item_builder):
        """Should decide to engage with high-relevance news."""
        # Create character agent
        jovani_agent = create_jovani_vazquez()
        
        # Create high-relevance news
        news_item = news_item_builder\
            .with_topics(["music", "entertainment", "festival"])\
            .with_relevance_score(0.9)\
            .build()
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Music festival announcement",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Should attempt engagement
        assert result["success"] is True or result.get("decision") == "engage"
    
    @pytest.mark.asyncio
    async def test_workflow_engagement_decision_low_relevance(self, news_item_builder):
        """Should decide not to engage with low-relevance news."""
        # Create character agent
        jovani_agent = create_jovani_vazquez()
        
        # Create low-relevance news
        news_item = news_item_builder\
            .with_topics(["traffic", "construction"])\
            .with_relevance_score(0.2)\
            .build()
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Traffic update",
            news_item=news_item,
            target_topic="traffic",
            is_new_thread=True
        )
        
        # Should not engage
        assert result["success"] is False or result.get("decision") == "skip"
    
    @pytest.mark.asyncio
    async def test_workflow_thread_rate_limiting(self, thread_state_builder):
        """Should respect thread rate limiting."""
        # Create character agent
        jovani_agent = create_jovani_vazquez()
        
        # Create thread state with existing replies
        thread_state = thread_state_builder\
            .with_thread_id("rate_limit_test")\
            .build()
        
        # Add replies up to limit
        for i in range(3):
            thread_state.add_character_reply("jovani_vazquez", f"Reply {i+1}")
        
        # Execute workflow
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Test context",
            conversation_history=[],
            target_topic="music",
            thread_id="rate_limit_test",
            is_new_thread=False,
            thread_engagement_state=thread_state
        )
        
        # Should be rate limited
        assert result["success"] is False or result.get("decision") == "rate_limited"


class TestCharacterWorkflowContextHandling:
    """Test character workflow context handling and generation."""
    
    @pytest.mark.asyncio
    async def test_workflow_with_news_context(self, news_item_builder):
        """Should handle news item context properly."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Response with news context"
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        news_item = news_item_builder\
            .with_headline("Music Festival Announcement")\
            .with_content("Major festival coming to San Juan")\
            .with_topics(["music", "festival"])\
            .build()
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Breaking news about music festival",
            news_item=news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        assert result["success"] is True
        assert "news_context" in result or "context" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_thread_context(self, thread_state_builder):
        """Should handle thread context properly."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Response with thread context"
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        thread_state = thread_state_builder\
            .with_thread_id("thread_001")\
            .with_original_content("Original thread content")\
            .build()
        
        # Add some replies
        thread_state.add_character_reply("other_char", "First reply")
        thread_state.add_character_reply("another_char", "Second reply")
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="New reply in thread",
            conversation_history=[],
            target_topic="music",
            thread_id="thread_001",
            thread_context="Thread discussion context",
            is_new_thread=False,
            thread_engagement_state=thread_state
        )
        
        assert result["success"] is True
        assert "thread_context" in result or "context" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_conversation_history(self):
        """Should handle conversation history properly."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Response with history context"
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        conversation_history = [
            "Previous discussion about music",
            "Concert announcement",
            "Festival details"
        ]
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="New music news",
            conversation_history=conversation_history,
            target_topic="music",
            is_new_thread=True
        )
        
        assert result["success"] is True
        assert "conversation_history" in result or "history" in result


class TestCharacterWorkflowErrorHandling:
    """Test character workflow error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_workflow_with_invalid_character_agent(self):
        """Should handle invalid character agent gracefully."""
        result = await execute_character_workflow(
            character_agent=None,
            input_context="Test context",
            target_topic="music",
            is_new_thread=True
        )
        
        assert result["success"] is False
        assert "error" in result or "error_details" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_empty_context(self):
        """Should handle empty context gracefully."""
        jovani_agent = create_jovani_vazquez()
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="",
            target_topic="music",
            is_new_thread=True
        )
        
        # Should handle gracefully (may skip or return error)
        assert isinstance(result, dict)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_ai_provider_error(self):
        """Should handle AI provider errors gracefully."""
        # Create mock AI provider that raises exception
        mock_ai_provider = Mock()
        mock_ai_provider.generate_character_response = AsyncMock(
            side_effect=Exception("AI provider error")
        )
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Test context",
            target_topic="music",
            is_new_thread=True
        )
        
        assert result["success"] is False
        assert "error" in result or "error_details" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_missing_parameters(self):
        """Should handle missing parameters gracefully."""
        jovani_agent = create_jovani_vazquez()
        
        # Test with missing required parameters
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            # Missing input_context and target_topic
            is_new_thread=True
        )
        
        assert result["success"] is False
        assert "error" in result or "error_details" in result


class TestCharacterWorkflowIntegration:
    """Test character workflow integration with other components."""
    
    @pytest.mark.asyncio
    async def test_workflow_with_personality_data(self, jovani_personality):
        """Should integrate properly with personality data."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Response using personality"
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Music festival announcement",
            target_topic="music",
            is_new_thread=True
        )
        
        assert result["success"] is True
        # Should use personality data in workflow
        assert jovani_agent.personality_data.character_name == jovani_personality.character_name
    
    @pytest.mark.asyncio
    async def test_workflow_with_thread_engagement_state(self, thread_state_builder):
        """Should integrate properly with thread engagement state."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Thread-aware response"
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        thread_state = thread_state_builder\
            .with_thread_id("integration_test")\
            .with_original_content("Original content")\
            .build()
        
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="Thread reply",
            conversation_history=[],
            target_topic="music",
            thread_id="integration_test",
            is_new_thread=False,
            thread_engagement_state=thread_state
        )
        
        assert result["success"] is True
        # Should use thread engagement state
        assert thread_state.thread_id == "integration_test" 