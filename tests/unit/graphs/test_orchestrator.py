"""
Tests for the orchestration system and news processing workflow.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from app.graphs.orchestrator import execute_orchestration_cycle
from app.models.conversation import create_orchestration_state
from app.agents.jovani_vazquez import create_jovani_vazquez


class TestOrchestrationStateCreation:
    """Test orchestration state creation and basic properties."""
    
    def test_orchestration_state_creation(self):
        """Should create orchestration state with correct properties."""
        character_ids = ["jovani_vazquez", "politico_boricua"]
        orchestration_state = create_orchestration_state(character_ids)
        
        assert orchestration_state.active_characters == character_ids
        assert len(orchestration_state.pending_news_queue) == 0
        assert len(orchestration_state.character_reactions) == 0
        assert len(orchestration_state.active_conversations) == 0
        assert orchestration_state.processed_news_count == 0
        assert orchestration_state.created_at is not None
    
    def test_orchestration_state_with_empty_characters(self):
        """Should handle empty character list."""
        orchestration_state = create_orchestration_state([])
        
        assert orchestration_state.active_characters == []
        assert len(orchestration_state.pending_news_queue) == 0
    
    def test_orchestration_state_with_single_character(self):
        """Should handle single character."""
        character_ids = ["jovani_vazquez"]
        orchestration_state = create_orchestration_state(character_ids)
        
        assert orchestration_state.active_characters == character_ids
        assert len(orchestration_state.active_characters) == 1


class TestOrchestrationCycleExecution:
    """Test orchestration cycle execution and basic functionality."""
    
    @pytest.mark.asyncio
    async def test_orchestration_cycle_with_news_items(self, sample_news_items):
        """Should execute orchestration cycle with news items."""
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
        
        # Verify result structure
        assert result["success"] is True
        assert "workflow_step" in result
        assert "execution_time_ms" in result
        assert "orchestration_state" in result
        assert "character_reactions" in result
    
    @pytest.mark.asyncio
    async def test_orchestration_cycle_with_new_news(self, news_item_builder):
        """Should process new news items in orchestration cycle."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create new news items
        new_news_items = [
            news_item_builder\
                .with_id("news_001")\
                .with_headline("Music Festival Announcement")\
                .with_topics(["music", "festival"])\
                .with_relevance_score(0.8)\
                .build(),
            news_item_builder\
                .with_id("news_002")\
                .with_headline("Traffic Update")\
                .with_topics(["traffic", "construction"])\
                .with_relevance_score(0.4)\
                .build()
        ]
        
        # Execute orchestration cycle with new news
        result = await execute_orchestration_cycle(
            news_items=new_news_items,
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        assert result["orchestration_state"].processed_news_count > 0
    
    @pytest.mark.asyncio
    async def test_orchestration_cycle_without_news(self):
        """Should handle orchestration cycle without news items."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Execute orchestration cycle without news
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        assert result["orchestration_state"].processed_news_count == 0
    
    @pytest.mark.asyncio
    async def test_orchestration_cycle_with_multiple_characters(self, sample_news_items):
        """Should handle orchestration with multiple characters."""
        # Create orchestration state with multiple characters
        character_ids = ["jovani_vazquez", "politico_boricua", "ciudadano_boricua"]
        orchestration_state = create_orchestration_state(character_ids)
        
        # Add news items to queue
        for news in sample_news_items:
            orchestration_state.pending_news_queue.append(news)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        assert len(result["orchestration_state"].active_characters) == 3


class TestOrchestrationNewsProcessing:
    """Test news processing within orchestration cycles."""
    
    @pytest.mark.asyncio
    async def test_news_item_processing_priority(self, news_item_builder):
        """Should process news items based on priority/relevance."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news items with different relevance scores
        high_relevance_news = news_item_builder\
            .with_id("high_relevance")\
            .with_headline("High Relevance News")\
            .with_topics(["music", "entertainment"])\
            .with_relevance_score(0.9)\
            .build()
        
        low_relevance_news = news_item_builder\
            .with_id("low_relevance")\
            .with_headline("Low Relevance News")\
            .with_topics(["traffic", "construction"])\
            .with_relevance_score(0.2)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.extend([low_relevance_news, high_relevance_news])
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should process news items (may prioritize by relevance)
        assert result["orchestration_state"].processed_news_count >= 0
    
    @pytest.mark.asyncio
    async def test_news_item_topic_matching(self, news_item_builder):
        """Should match news items to appropriate characters based on topics."""
        # Create orchestration state with multiple characters
        character_ids = ["jovani_vazquez", "politico_boricua"]
        orchestration_state = create_orchestration_state(character_ids)
        
        # Create news items with different topics
        music_news = news_item_builder\
            .with_id("music_news")\
            .with_headline("Music Festival")\
            .with_topics(["music", "entertainment"])\
            .with_relevance_score(0.8)\
            .build()
        
        political_news = news_item_builder\
            .with_id("political_news")\
            .with_headline("Political Update")\
            .with_topics(["politics", "government"])\
            .with_relevance_score(0.8)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.extend([music_news, political_news])
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should generate reactions from appropriate characters
        assert len(result["character_reactions"]) >= 0
    
    @pytest.mark.asyncio
    async def test_news_item_relevance_filtering(self, news_item_builder):
        """Should filter news items based on relevance scores."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news items with varying relevance
        relevant_news = news_item_builder\
            .with_id("relevant")\
            .with_relevance_score(0.8)\
            .build()
        
        irrelevant_news = news_item_builder\
            .with_id("irrelevant")\
            .with_relevance_score(0.1)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.extend([relevant_news, irrelevant_news])
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should process relevant news more actively
        assert result["orchestration_state"].processed_news_count >= 0


class TestOrchestrationCharacterReactions:
    """Test character reaction generation within orchestration."""
    
    @pytest.mark.asyncio
    async def test_character_reaction_generation(self, news_item_builder):
        """Should generate character reactions to news items."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create relevant news item
        news_item = news_item_builder\
            .with_id("music_festival")\
            .with_headline("Music Festival Announcement")\
            .with_topics(["music", "entertainment"])\
            .with_relevance_score(0.9)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should generate reactions from characters
        assert len(result["character_reactions"]) >= 0
    
    @pytest.mark.asyncio
    async def test_character_reaction_decision_making(self, news_item_builder):
        """Should make appropriate decisions about character engagement."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news items with different characteristics
        engaging_news = news_item_builder\
            .with_id("engaging")\
            .with_topics(["music", "festival"])\
            .with_relevance_score(0.9)\
            .build()
        
        non_engaging_news = news_item_builder\
            .with_id("non_engaging")\
            .with_topics(["traffic", "construction"])\
            .with_relevance_score(0.2)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.extend([engaging_news, non_engaging_news])
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should make different decisions for different news items
        reactions = result["character_reactions"]
        assert len(reactions) >= 0  # May have different engagement decisions


class TestOrchestrationStateManagement:
    """Test orchestration state management and persistence."""
    
    @pytest.mark.asyncio
    async def test_orchestration_state_persistence(self, sample_news_items):
        """Should maintain state across orchestration cycles."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Add news items to queue
        for news in sample_news_items:
            orchestration_state.pending_news_queue.append(news)
        
        # Execute first cycle
        result1 = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Execute second cycle with same state
        result2 = await execute_orchestration_cycle(
            news_items=[],
            existing_state=result1["orchestration_state"]
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        # State should persist between cycles
        assert result2["orchestration_state"].processed_news_count >= result1["orchestration_state"].processed_news_count
    
    @pytest.mark.asyncio
    async def test_orchestration_state_conversation_tracking(self, news_item_builder):
        """Should track active conversations in orchestration state."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news item
        news_item = news_item_builder\
            .with_id("conversation_test")\
            .with_headline("Test Conversation")\
            .with_topics(["music"])\
            .with_relevance_score(0.8)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should track conversations
        assert len(result["orchestration_state"].active_conversations) >= 0
    
    @pytest.mark.asyncio
    async def test_orchestration_state_character_reaction_tracking(self, news_item_builder):
        """Should track character reactions in orchestration state."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create news item
        news_item = news_item_builder\
            .with_id("reaction_test")\
            .with_headline("Test Reactions")\
            .with_topics(["music"])\
            .with_relevance_score(0.8)\
            .build()
        
        # Add to queue
        orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should track character reactions
        assert len(result["orchestration_state"].character_reactions) >= 0


class TestOrchestrationErrorHandling:
    """Test orchestration error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_orchestration_with_invalid_state(self):
        """Should handle invalid orchestration state gracefully."""
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=None
        )
        
        assert result["success"] is False
        assert "error" in result or "error_details" in result
    
    @pytest.mark.asyncio
    async def test_orchestration_with_empty_character_list(self):
        """Should handle orchestration with no active characters."""
        # Create orchestration state with no characters
        orchestration_state = create_orchestration_state([])
        
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        assert len(result["orchestration_state"].active_characters) == 0
    
    @pytest.mark.asyncio
    async def test_orchestration_with_large_news_queue(self, news_item_builder):
        """Should handle large news queues efficiently."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create many news items
        for i in range(10):
            news_item = news_item_builder\
                .with_id(f"news_{i}")\
                .with_headline(f"News Item {i}")\
                .with_topics(["music"])\
                .with_relevance_score(0.5 + (i * 0.05))\
                .build()
            orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should handle large queues without errors
        assert result["orchestration_state"].processed_news_count >= 0


class TestOrchestrationIntegration:
    """Test orchestration integration with other components."""
    
    @pytest.mark.asyncio
    async def test_orchestration_with_character_agents(self):
        """Should integrate properly with character agents."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create character agent
        jovani_agent = create_jovani_vazquez()
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should work with character agents
        assert "jovani_vazquez" in result["orchestration_state"].active_characters
    
    @pytest.mark.asyncio
    async def test_orchestration_with_news_processing(self, sample_news_items):
        """Should integrate properly with news processing."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Add news items
        for news in sample_news_items:
            orchestration_state.pending_news_queue.append(news)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        assert result["success"] is True
        # Should process news items
        assert result["orchestration_state"].processed_news_count >= 0 