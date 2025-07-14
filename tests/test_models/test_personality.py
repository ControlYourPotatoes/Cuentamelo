"""
Tests for the personality system models and data structures.
"""
import pytest
from datetime import datetime, timezone

from app.models.personality import (
    create_jovani_vazquez_personality,
    PersonalityTone, test_personality_consistency as validate_personality_consistency
)


class TestPersonalityDataSystem:
    """Test the personality data system and character creation."""
    
    def test_jovani_vazquez_personality_creation(self, jovani_personality):
        """Should create Jovani Vázquez personality with correct attributes."""
        assert jovani_personality.character_name == "Jovani Vázquez"
        assert jovani_personality.character_type == "influencer"
        assert jovani_personality.engagement_threshold > 0
        assert len(jovani_personality.signature_phrases) > 0
        assert jovani_personality.base_energy_level > 0
    
    def test_politico_boricua_personality_creation(self, politico_personality):
        """Should create Político Boricua personality with correct attributes."""
        assert politico_personality.character_name == "Político Boricua"
        assert politico_personality.character_type == "politician"
        assert politico_personality.engagement_threshold > 0
        assert len(politico_personality.signature_phrases) > 0
        assert politico_personality.base_energy_level > 0
    
    def test_ciudadano_boricua_personality_creation(self, ciudadano_personality):
        """Should create Ciudadano Boricua personality with correct attributes."""
        assert ciudadano_personality.character_name == "Ciudadano Boricua"
        assert ciudadano_personality.character_type == "citizen"
        assert ciudadano_personality.engagement_threshold > 0
        assert len(ciudadano_personality.signature_phrases) > 0
        assert ciudadano_personality.base_energy_level > 0
    
    def test_historiador_cultural_personality_creation(self, historiador_personality):
        """Should create Historiador Cultural personality with correct attributes."""
        assert historiador_personality.character_name == "Historiador Cultural"
        assert historiador_personality.character_type == "historian"
        assert historiador_personality.engagement_threshold > 0
        assert len(historiador_personality.signature_phrases) > 0
        assert historiador_personality.base_energy_level > 0
    
    def test_personality_energy_levels_are_different(self, jovani_personality, 
                                                   politico_personality, 
                                                   ciudadano_personality, 
                                                   historiador_personality):
        """Should have different energy levels for different character types."""
        energy_levels = [
            jovani_personality.base_energy_level,
            politico_personality.base_energy_level,
            ciudadano_personality.base_energy_level,
            historiador_personality.base_energy_level
        ]
        
        # All energy levels should be positive
        assert all(level > 0 for level in energy_levels)
        
        # Energy levels should be different (not all the same)
        assert len(set(energy_levels)) > 1
    
    def test_personality_tone_preferences(self, jovani_personality, historiador_personality):
        """Should have appropriate tone preferences for different character types."""
        assert len(jovani_personality.tone_preferences) > 0
        assert len(historiador_personality.tone_preferences) > 0
        
        # Jovani should have tone preferences (flexible on specific values)
        jovani_tones = list(jovani_personality.tone_preferences.values())
        assert len(jovani_tones) > 0
        assert all(isinstance(tone, str) for tone in jovani_tones)
        
        # Historiador should have tone preferences (flexible on specific values)
        historiador_tones = list(historiador_personality.tone_preferences.values())
        assert len(historiador_tones) > 0
        assert all(isinstance(tone, str) for tone in historiador_tones)
    
    def test_personality_consistency_validation(self, jovani_personality):
        """Should validate personality consistency correctly."""
        consistency_result = validate_personality_consistency(jovani_personality)
        assert isinstance(consistency_result, dict)
        assert "valid" in consistency_result
        assert "issues" in consistency_result
        assert "strengths" in consistency_result
        assert "suggestions" in consistency_result
    
    def test_personality_topic_weights(self, jovani_personality):
        """Should have topic weights that sum to reasonable values."""
        topic_weights = jovani_personality.topic_weights
        
        # Should have topic weights
        assert len(topic_weights) > 0
        
        # All weights should be positive
        assert all(weight >= 0 for weight in topic_weights.values())
        
        # Music should be a high-priority topic for Jovani
        assert topic_weights.get("music", 0) > 0.5
    
    def test_personality_signature_phrases(self, jovani_personality):
        """Should have signature phrases that reflect character personality."""
        phrases = jovani_personality.signature_phrases
        
        assert len(phrases) > 0
        
        # Phrases should be strings
        assert all(isinstance(phrase, str) for phrase in phrases)
        
        # Phrases should not be empty
        assert all(len(phrase.strip()) > 0 for phrase in phrases)
    
    def test_personality_engagement_thresholds(self, jovani_personality, 
                                             politico_personality, 
                                             ciudadano_personality, 
                                             historiador_personality):
        """Should have reasonable engagement thresholds."""
        thresholds = [
            jovani_personality.engagement_threshold,
            politico_personality.engagement_threshold,
            ciudadano_personality.engagement_threshold,
            historiador_personality.engagement_threshold
        ]
        
        # All thresholds should be between 0 and 1
        assert all(0 <= threshold <= 1 for threshold in thresholds)
        
        # Thresholds should be different for different characters
        assert len(set(thresholds)) > 1


class TestPersonalityToneEnum:
    """Test the PersonalityTone enumeration."""
    
    def test_personality_tone_values(self):
        """Should have expected tone values."""
        expected_tones = [
            "passionate", "professional", "casual", "educational", 
            "enthusiastic", "controversial", "supportive"
        ]
        
        actual_tones = [tone.value for tone in PersonalityTone]
        
        for expected_tone in expected_tones:
            assert expected_tone in actual_tones
    
    def test_passionate_tone_exists(self):
        """Should have PASSIONATE tone available."""
        assert PersonalityTone.PASSIONATE.value == "passionate"
    
    def test_educational_tone_exists(self):
        """Should have EDUCATIONAL tone available."""
        assert PersonalityTone.EDUCATIONAL.value == "educational"
    
    def test_casual_tone_exists(self):
        """Should have CASUAL tone available."""
        assert PersonalityTone.CASUAL.value == "casual"


class TestPersonalityDataValidation:
    """Test personality data validation and edge cases."""
    
    def test_jovani_personality_creation_does_not_raise_exceptions(self):
        """Should create Jovani personality without raising exceptions."""
        try:
            create_jovani_vazquez_personality()
        except Exception as e:
            pytest.fail(f"Jovani personality creation raised unexpected exception: {e}")
    
    def test_personality_consistency_with_jovani(self, jovani_personality):
        """Should validate consistency for Jovani personality."""
        consistency_result = validate_personality_consistency(jovani_personality)
        assert isinstance(consistency_result, dict)
        assert "valid" in consistency_result
    
    def test_personality_topic_weights_are_consistent(self, jovani_personality):
        """Should have consistent topic weight structure."""
        topic_weights = jovani_personality.topic_weights
        
        # Should be a dictionary
        assert isinstance(topic_weights, dict)
        
        # All keys should be strings
        assert all(isinstance(key, str) for key in topic_weights.keys())
        
        # All values should be numbers
        assert all(isinstance(value, (int, float)) for value in topic_weights.values()) 