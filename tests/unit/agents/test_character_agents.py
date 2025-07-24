"""
Tests for the character agent system and AI provider abstraction.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.models.personality import create_jovani_vazquez_personality


class TestCharacterAgentCreation:
    """Test character agent creation and basic properties."""
    
    def test_jovani_agent_creation_without_ai_provider(self):
        """Should create Jovani agent without AI provider."""
        jovani_agent = create_jovani_vazquez()
        
        assert jovani_agent.character_name == "Jovani Vázquez"
        assert jovani_agent.character_type == "music_enthusiast"
        assert jovani_agent.engagement_threshold > 0
        assert jovani_agent.max_replies_per_thread > 0
        assert jovani_agent.personality_data is not None
    
    def test_jovani_agent_creation_with_ai_provider(self):
        """Should create Jovani agent with AI provider injection."""
        mock_ai_provider = Mock()
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        assert jovani_agent.character_name == "Jovani Vázquez"
        assert jovani_agent.ai_provider == mock_ai_provider
    
    def test_jovani_agent_personality_data_access(self):
        """Should provide access to personality data."""
        jovani_agent = create_jovani_vazquez()
        
        assert jovani_agent.personality_data is not None
        assert jovani_agent.personality_data.character_name == "Jovani Vázquez"
        assert len(jovani_agent.personality_data.signature_phrases) > 0
        assert len(jovani_agent.personality_data.topic_weights) > 0


class TestCharacterAgentEngagement:
    """Test character agent engagement probability calculations."""
    
    def test_engagement_probability_calculation(self):
        """Should calculate engagement probability for relevant topics."""
        jovani_agent = create_jovani_vazquez()
        
        # Test with music-related context (high relevance)
        music_context = "New Puerto Rican music festival announced in San Juan!"
        music_prob = jovani_agent.calculate_engagement_probability(
            context=music_context,
            conversation_history=[]
        )
        
        assert 0 <= music_prob <= 1
        assert music_prob > 0.5  # Should be high for music topics
    
    def test_engagement_probability_with_irrelevant_topic(self):
        """Should calculate low engagement probability for irrelevant topics."""
        jovani_agent = create_jovani_vazquez()
        
        # Test with traffic-related context (low relevance for Jovani)
        traffic_context = "Traffic delays on Highway 22 in Bayamón"
        traffic_prob = jovani_agent.calculate_engagement_probability(
            context=traffic_context,
            conversation_history=[]
        )
        
        assert 0 <= traffic_prob <= 1
        assert traffic_prob < 0.5  # Should be lower for non-music topics
    
    def test_engagement_probability_with_conversation_history(self):
        """Should consider conversation history in engagement calculation."""
        jovani_agent = create_jovani_vazquez()
        
        # Test with empty history
        empty_history_prob = jovani_agent.calculate_engagement_probability(
            context="Music festival announcement",
            conversation_history=[]
        )
        
        # Test with existing conversation
        existing_history = ["Previous music discussion", "Concert announcement"]
        history_prob = jovani_agent.calculate_engagement_probability(
            context="Music festival announcement",
            conversation_history=existing_history
        )
        
        assert 0 <= empty_history_prob <= 1
        assert 0 <= history_prob <= 1
    
    def test_engagement_probability_edge_cases(self):
        """Should handle edge cases in engagement probability calculation."""
        jovani_agent = create_jovani_vazquez()
        
        # Test with empty context
        empty_prob = jovani_agent.calculate_engagement_probability(
            context="",
            conversation_history=[]
        )
        assert 0 <= empty_prob <= 1
        
        # Test with very long context
        long_context = "A" * 1000
        long_prob = jovani_agent.calculate_engagement_probability(
            context=long_context,
            conversation_history=[]
        )
        assert 0 <= long_prob <= 1


class TestCharacterAgentTopicRelevance:
    """Test character agent topic relevance calculations."""
    
    def test_topic_relevance_for_music_topics(self):
        """Should calculate high relevance for music-related topics."""
        jovani_agent = create_jovani_vazquez()
        
        music_topics = ["music", "entertainment", "festival", "concert"]
        music_relevance = jovani_agent.get_topic_relevance(music_topics)
        
        assert 0 <= music_relevance <= 1
        assert music_relevance > 0.5  # Should be high for music topics
    
    def test_topic_relevance_for_non_music_topics(self):
        """Should calculate lower relevance for non-music topics."""
        jovani_agent = create_jovani_vazquez()
        
        non_music_topics = ["traffic", "construction", "politics", "weather"]
        non_music_relevance = jovani_agent.get_topic_relevance(non_music_topics)
        
        assert 0 <= non_music_relevance <= 1
        assert non_music_relevance < 0.5  # Should be lower for non-music topics
    
    def test_topic_relevance_with_empty_topics(self):
        """Should handle empty topics list."""
        jovani_agent = create_jovani_vazquez()
        
        empty_relevance = jovani_agent.get_topic_relevance([])
        assert 0 <= empty_relevance <= 1
    
    def test_topic_relevance_with_mixed_topics(self):
        """Should calculate relevance for mixed topic lists."""
        jovani_agent = create_jovani_vazquez()
        
        mixed_topics = ["music", "traffic", "festival", "construction"]
        mixed_relevance = jovani_agent.get_topic_relevance(mixed_topics)
        
        assert 0 <= mixed_relevance <= 1
        # Should be moderate (some music, some non-music)
        assert 0.2 <= mixed_relevance <= 0.8


class TestCharacterAgentDecisionMaking:
    """Test character agent decision-making logic."""
    
    def test_should_engage_with_high_relevance_news(self):
        """Should decide to engage with high-relevance news."""
        jovani_agent = create_jovani_vazquez()
        
        # High-relevance music news
        music_news = Mock()
        music_news.topics = ["music", "entertainment", "festival"]
        music_news.relevance_score = 0.9
        
        decision = jovani_agent.should_engage_with_news(music_news)
        assert decision is True
    
    def test_should_not_engage_with_low_relevance_news(self):
        """Should decide not to engage with low-relevance news."""
        jovani_agent = create_jovani_vazquez()
        
        # Low-relevance traffic news
        traffic_news = Mock()
        traffic_news.topics = ["traffic", "construction"]
        traffic_news.relevance_score = 0.3
        
        decision = jovani_agent.should_engage_with_news(traffic_news)
        assert decision is False
    
    def test_should_engage_with_medium_relevance_news(self):
        """Should make appropriate decision for medium-relevance news."""
        jovani_agent = create_jovani_vazquez()
        
        # Medium-relevance cultural news
        cultural_news = Mock()
        cultural_news.topics = ["culture", "heritage"]
        cultural_news.relevance_score = 0.6
        
        decision = jovani_agent.should_engage_with_news(cultural_news)
        # Decision should be boolean (True or False)
        assert isinstance(decision, bool)


class TestCharacterAgentResponseGeneration:
    """Test character agent response generation with AI provider."""
    
    @pytest.mark.asyncio
    async def test_generate_response_with_ai_provider(self):
        """Should generate response using AI provider when available."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "¡Qué noticia increíble! 🎵"
        mock_response.confidence_score = 0.8
        mock_response.character_consistency = 0.9
        mock_response.metadata = {"tone": "passionate"}
        
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        response = await jovani_agent.generate_response(
            context="New music festival announced",
            target_topic="music",
            is_new_thread=True
        )
        
        assert response is not None
        assert response.content == "¡Qué noticia increíble! 🎵"
        assert response.confidence_score == 0.8
        assert response.character_consistency == 0.9
    
    @pytest.mark.asyncio
    async def test_generate_response_without_ai_provider(self):
        """Should handle response generation without AI provider."""
        jovani_agent = create_jovani_vazquez()  # No AI provider
        
        response = await jovani_agent.generate_response(
            context="New music festival announced",
            target_topic="music",
            is_new_thread=True
        )
        
        # Should return None or handle gracefully
        assert response is None or isinstance(response, Mock)
    
    @pytest.mark.asyncio
    async def test_generate_response_with_thread_context(self):
        """Should generate response with thread context."""
        mock_ai_provider = Mock()
        mock_response = Mock()
        mock_response.content = "¡Exacto! Este festival va a ser épico 🎵"
        mock_response.metadata = {"thread_aware": True}
        
        mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
        
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        response = await jovani_agent.generate_response(
            context="This festival is going to be amazing!",
            target_topic="music",
            is_new_thread=False,
            thread_context="Previous discussion about music festival"
        )
        
        assert response is not None
        assert response.content == "¡Exacto! Este festival va a ser épico 🎵"
        assert response.metadata.get("thread_aware") is True


class TestCharacterAgentValidation:
    """Test character agent validation and edge cases."""
    
    def test_character_agent_has_required_attributes(self):
        """Should have all required character agent attributes."""
        jovani_agent = create_jovani_vazquez()
        
        required_attributes = [
            'character_name', 'character_type', 'engagement_threshold',
            'max_replies_per_thread', 'personality_data'
        ]
        
        for attr in required_attributes:
            assert hasattr(jovani_agent, attr)
            assert getattr(jovani_agent, attr) is not None
    
    def test_character_agent_engagement_threshold_bounds(self):
        """Should have engagement threshold within valid bounds."""
        jovani_agent = create_jovani_vazquez()
        
        assert 0 < jovani_agent.engagement_threshold <= 1.0
    
    def test_character_agent_max_replies_bounds(self):
        """Should have reasonable max replies per thread."""
        jovani_agent = create_jovani_vazquez()
        
        assert jovani_agent.max_replies_per_thread > 0
        assert jovani_agent.max_replies_per_thread <= 10  # Reasonable upper bound
    
    def test_character_agent_personality_data_consistency(self):
        """Should have consistent personality data."""
        jovani_agent = create_jovani_vazquez()
        
        personality = jovani_agent.personality_data
        
        assert personality.character_name == jovani_agent.character_name
        assert personality.character_type == jovani_agent.character_type
        assert personality.engagement_threshold == jovani_agent.engagement_threshold


class TestCharacterAgentIntegration:
    """Test character agent integration with other components."""
    
    def test_character_agent_with_personality_data(self, jovani_personality):
        """Should integrate properly with personality data."""
        mock_ai_provider = Mock()
        jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
        
        # Verify personality data integration
        assert jovani_agent.personality_data.character_name == jovani_personality.character_name
        assert jovani_agent.personality_data.signature_phrases == jovani_personality.signature_phrases
        assert jovani_agent.personality_data.topic_weights == jovani_personality.topic_weights
    
    def test_character_agent_topic_weights_integration(self):
        """Should use personality topic weights for relevance calculations."""
        jovani_agent = create_jovani_vazquez()
        
        # Get topic weights from personality
        topic_weights = jovani_agent.personality_data.topic_weights
        
        # Test that music has high weight
        assert topic_weights.get("music", 0) > 0.5
        
        # Test relevance calculation uses these weights
        music_relevance = jovani_agent.get_topic_relevance(["music"])
        assert music_relevance > 0.5 