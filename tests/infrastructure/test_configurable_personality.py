"""
Tests for the configurable personality implementation.
"""
import pytest
from unittest.mock import Mock, patch

from app.models.personalities.configurable_personality import ConfigurablePersonality, create_configurable_personality
from app.ports.personality_port import PersonalityPort, LanguageStyle


class TestConfigurablePersonality:
    """Test the configurable personality implementation."""

    def test_create_configurable_personality(self):
        """Test creating configurable personality."""
        personality = create_configurable_personality("jovani_vazquez")

        assert isinstance(personality, PersonalityPort)
        assert personality.character_id == "jovani_vazquez"
        assert personality.character_name == "Jovani Vázquez"

    def test_personality_properties(self):
        """Test personality properties are correctly loaded."""
        personality = create_configurable_personality("jovani_vazquez")

        # Test basic properties
        assert personality.character_id == "jovani_vazquez"
        assert personality.character_name == "Jovani Vázquez"
        assert personality.character_type == "influencer"
        # With use_enum_values=True, language_style is a string, not an enum
        assert isinstance(personality.language_style, str)
        assert personality.language_style == LanguageStyle.PUERTO_RICAN_SLANG.value

        # Test engagement properties
        assert isinstance(personality.engagement_threshold, float)
        assert isinstance(personality.cooldown_minutes, int)
        assert isinstance(personality.max_daily_interactions, int)
        assert isinstance(personality.max_replies_per_thread, int)

        # Test topic properties
        assert isinstance(personality.topics_of_interest, list)
        assert isinstance(personality.topic_weights, dict)
        assert isinstance(personality.preferred_topics, list)
        assert isinstance(personality.avoided_topics, list)

    def test_get_topic_relevance(self):
        """Test topic relevance calculation."""
        personality = create_configurable_personality("jovani_vazquez")

        # Test with empty topics
        relevance = personality.get_topic_relevance([])
        assert relevance == 0.2

        # Test with relevant topics
        relevance = personality.get_topic_relevance(["entertainment"])
        assert relevance > 0.0

    def test_get_emotional_context(self):
        """Test emotional context determination."""
        personality = create_configurable_personality("jovani_vazquez")

        # Test with different energy levels
        context = personality.get_emotional_context("test content")
        assert context in ["excited", "calm", "neutral"]

    def test_should_engage_in_controversy(self):
        """Test controversy engagement logic."""
        personality = create_configurable_personality("jovani_vazquez")

        # Test with normal content
        should_engage = personality.should_engage_in_controversy("normal content")
        assert isinstance(should_engage, bool)

    def test_get_character_context(self):
        """Test character context enhancement and signature phrase frequency logic."""
        personality = create_configurable_personality("jovani_vazquez")

        base_context = "Test context"
        # Simulate multiple calls to check frequency distribution
        phrase_counts = {}
        for _ in range(100):
            enhanced_context = personality.get_character_context(base_context)
            # Extract the signature phrase used (after 'Start with your signature:')
            import re
            match = re.search(r"Start with your signature: '([^']+)'", enhanced_context)
            if match:
                phrase = match.group(1)
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        # Check that at least one 'common' and one 'rare' phrase appear
        config = personality.get_personality_data()
        common_phrases = [p.text for p in config.signature_phrases if getattr(p, 'frequency', 'rare') == 'common']
        rare_phrases = [p.text for p in config.signature_phrases if getattr(p, 'frequency', 'rare') == 'rare']
        assert any(phrase in phrase_counts for phrase in common_phrases)
        if rare_phrases:
            assert any(phrase in phrase_counts for phrase in rare_phrases)
            # Common phrases should appear more often than rare ones
            common_total = sum(phrase_counts.get(p, 0) for p in common_phrases)
            rare_total = sum(phrase_counts.get(p, 0) for p in rare_phrases)
            assert common_total > rare_total
        # Also check that the base context is present
        enhanced_context = personality.get_character_context(base_context)
        assert base_context in enhanced_context
        assert personality.character_name in enhanced_context
        assert personality.personality_traits in enhanced_context

    def test_get_fallback_responses(self):
        """Test fallback response generation."""
        personality = create_configurable_personality("jovani_vazquez")

        responses = personality.get_fallback_responses()
        assert isinstance(responses, list)
        assert len(responses) > 0

    def test_calculate_engagement_boost(self):
        """Test engagement boost calculation."""
        personality = create_configurable_personality("jovani_vazquez")

        content = "Puerto Rico is amazing!"
        boosts = personality.calculate_engagement_boost(content)

        assert isinstance(boosts, dict)
        assert "energy" in boosts
        assert "pr_relevance" in boosts
        assert "emotion" in boosts
        assert "trending" in boosts

        # Test Puerto Rico relevance
        assert boosts["pr_relevance"] > 0.0

    def test_get_personality_data(self):
        """Test getting personality data."""
        personality = create_configurable_personality("jovani_vazquez")

        personality_data = personality.get_personality_data()
        assert personality_data is not None
        assert personality_data.character_id == "jovani_vazquez"

    def test_get_ai_personality_data(self):
        """Test getting AI personality data."""
        personality = create_configurable_personality("jovani_vazquez")

        ai_data = personality.get_ai_personality_data()
        assert ai_data is not None

    def test_get_agent_personality_data(self):
        """Test getting agent personality data."""
        personality = create_configurable_personality("jovani_vazquez")

        agent_data = personality.get_agent_personality_data()
        assert agent_data is not None

    def test_invalid_character_id(self):
        """Test error handling for invalid character ID."""
        with pytest.raises(Exception):  # Should raise some exception for invalid ID
            create_configurable_personality("nonexistent_character") 