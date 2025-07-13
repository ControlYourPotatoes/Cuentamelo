"""
Integration tests for the configuration-driven personality system.
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.services.personality_config_loader import PersonalityConfigLoader
from app.models.personality import PersonalityData
from app.models.ai_personality_data import AIPersonalityData
from app.models.agent_personality_data import AgentPersonalityData
from app.models.personalities.jovani_vazquez_personality import JovaniVazquezPersonality


class TestConfigDrivenPersonalityIntegration:
    """Integration tests for configuration-driven personality system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "personalities"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration
        self.test_config = {
            "character_id": "test_jovani",
            "character_name": "Test Jovani",
            "character_type": "influencer",
            "personality": {
                "traits": "Energetic, charismatic Puerto Rican social media influencer",
                "background": "Born and raised in San Juan, Puerto Rico. Content creator focusing on Puerto Rican culture",
                "language_style": "spanglish",
                "interaction_style": "High energy, quick to respond, loves to engage",
                "cultural_context": "Deeply connected to Puerto Rican culture and identity"
            },
            "engagement": {
                "threshold": 0.3,
                "cooldown_minutes": 2,
                "max_daily_interactions": 100,
                "max_replies_per_thread": 2
            },
            "topics": {
                "of_interest": ["entertainment", "music", "culture", "social media"],
                "weights": {
                    "entertainment": 0.9,
                    "music": 0.9,
                    "culture": 0.8
                },
                "preferred": ["entertainment", "music", "culture"],
                "avoided": ["heavy politics", "controversial religious topics"]
            },
            "language": {
                "signature_phrases": ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"],
                "common_expressions": ["que lo que", "pa", "tremendo"],
                "emoji_preferences": ["🔥", "💯", "😂", "🇵🇷"],
                "patterns": {
                    "excited": "High energy with lots of exclamations and emojis",
                    "casual": "Spanglish mix with local expressions"
                }
            },
            "responses": {
                "examples": {
                    "entertainment": ["¡Ay, pero esto está buenísimo! 🔥"],
                    "music": ["¡La música está en mi sangre! 🎵🇵🇷"]
                },
                "templates": {
                    "new_thread": "Hey fam! {content} What do you think? 👀",
                    "thread_reply": "¡Exacto! {content} 🔥"
                }
            },
            "energy": {
                "base_level": 0.9,
                "tone_preferences": {
                    "entertainment": "enthusiastic",
                    "culture": "passionate"
                },
                "emotional_triggers": {
                    "puerto_rico_related": 0.9,
                    "music": 0.8
                }
            },
            "cultural": {
                "puerto_rico_references": ["Borinquen", "Boricua", "PR"],
                "local_places": ["San Juan", "Viejo San Juan"],
                "cultural_events": ["Fiestas de la Calle San Sebastián"],
                "local_foods": ["mofongo", "pasteles"]
            },
            "behavior": {
                "hashtag_style": "natural",
                "mention_behavior": "selective",
                "retweet_preferences": ["Puerto Rican creators", "Local events"],
                "thread_behavior": "conversational"
            },
            "validation": {
                "personality_consistency_rules": ["Use Spanglish naturally", "Maintain high energy"],
                "content_guidelines": ["Never be offensive", "Show Puerto Rican pride"]
            }
        }
        
        # Save test configuration
        config_file = self.config_dir / "test_jovani.json"
        with open(config_file, 'w') as f:
            json.dump(self.test_config, f)
        
        self.loader = PersonalityConfigLoader(str(self.config_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_personality_data_from_config(self):
        """Test creating PersonalityData from configuration."""
        personality_data = PersonalityData.create_from_config(self.test_config)
        
        assert personality_data.character_id == "test_jovani"
        assert personality_data.character_name == "Test Jovani"
        assert personality_data.character_type == "influencer"
        assert personality_data.personality_traits == "Energetic, charismatic Puerto Rican social media influencer"
        assert personality_data.engagement_threshold == 0.3
        assert personality_data.cooldown_minutes == 2
        assert personality_data.max_daily_interactions == 100
        assert personality_data.max_replies_per_thread == 2
        assert personality_data.topics_of_interest == ["entertainment", "music", "culture", "social media"]
        assert personality_data.topic_weights == {"entertainment": 0.9, "music": 0.9, "culture": 0.8}
        assert personality_data.signature_phrases == ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"]
        assert personality_data.emoji_preferences == ["🔥", "💯", "😂", "🇵🇷"]
        assert personality_data.base_energy_level == 0.9
        assert personality_data.puerto_rico_references == ["Borinquen", "Boricua", "PR"]
    
    def test_ai_personality_data_from_config(self):
        """Test creating AIPersonalityData from configuration."""
        ai_data = AIPersonalityData.create_from_config(self.test_config)
        
        assert ai_data.character_id == "test_jovani"
        assert ai_data.character_name == "Test Jovani"
        assert ai_data.character_type == "influencer"
        assert ai_data.personality_traits == "Energetic, charismatic Puerto Rican social media influencer"
        assert ai_data.language_style == "spanglish"
        assert ai_data.signature_phrases == ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"]
        assert ai_data.topics_of_interest == ["entertainment", "music", "culture", "social media"]
        assert ai_data.example_responses == {
            "entertainment": ["¡Ay, pero esto está buenísimo! 🔥"],
            "music": ["¡La música está en mi sangre! 🎵🇵🇷"]
        }
        assert ai_data.base_energy_level == 0.9
        assert ai_data.puerto_rico_references == ["Borinquen", "Boricua", "PR"]
    
    def test_agent_personality_data_from_config(self):
        """Test creating AgentPersonalityData from configuration."""
        agent_data = AgentPersonalityData.create_from_config(self.test_config)
        
        assert agent_data.character_id == "test_jovani"
        assert agent_data.character_name == "Test Jovani"
        assert agent_data.character_type == "influencer"
        assert agent_data.engagement_threshold == 0.3
        assert agent_data.cooldown_minutes == 2
        assert agent_data.max_daily_interactions == 100
        assert agent_data.max_replies_per_thread == 2
        assert agent_data.topics_of_interest == ["entertainment", "music", "culture", "social media"]
        assert agent_data.topic_weights == {"entertainment": 0.9, "music": 0.9, "culture": 0.8}
        assert agent_data.preferred_topics == ["entertainment", "music", "culture"]
        assert agent_data.avoided_topics == ["heavy politics", "controversial religious topics"]
        assert agent_data.personality_traits == "Energetic, charismatic Puerto Rican social media influencer"
        assert agent_data.signature_phrases == ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"]
    
    def test_jovani_personality_with_config_loader(self):
        """Test JovaniVazquezPersonality with configuration loader."""
        # Create a mock config loader that returns our test config
        with patch.object(self.loader, 'load_personality', return_value=self.test_config):
            personality = JovaniVazquezPersonality(config_loader=self.loader)
            
            # Test basic properties
            assert personality.character_id == "test_jovani"
            assert personality.character_name == "Test Jovani"
            assert personality.character_type == "influencer"
            assert personality.engagement_threshold == 0.3
            assert personality.cooldown_minutes == 2
            assert personality.max_daily_interactions == 100
            assert personality.max_replies_per_thread == 2
            assert personality.topics_of_interest == ["entertainment", "music", "culture", "social media"]
            assert personality.signature_phrases == ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"]
            assert personality.emoji_preferences == ["🔥", "💯", "😂", "🇵🇷"]
            assert personality.base_energy_level == 0.9
    
    def test_jovani_personality_ai_data_integration(self):
        """Test that JovaniVazquezPersonality returns correct AI data."""
        with patch.object(self.loader, 'load_personality', return_value=self.test_config):
            personality = JovaniVazquezPersonality(config_loader=self.loader)
            ai_data = personality.get_ai_personality_data()
            
            assert isinstance(ai_data, AIPersonalityData)
            assert ai_data.character_id == "test_jovani"
            assert ai_data.character_name == "Test Jovani"
            assert ai_data.language_style == "spanglish"
            assert ai_data.signature_phrases == ["¡Ay, pero esto está buenísimo!", "Real talk", "Wepa!"]
            assert ai_data.example_responses == {
                "entertainment": ["¡Ay, pero esto está buenísimo! 🔥"],
                "music": ["¡La música está en mi sangre! 🎵🇵🇷"]
            }
    
    def test_jovani_personality_agent_data_integration(self):
        """Test that JovaniVazquezPersonality returns correct agent data."""
        with patch.object(self.loader, 'load_personality', return_value=self.test_config):
            personality = JovaniVazquezPersonality(config_loader=self.loader)
            agent_data = personality.get_agent_personality_data()
            
            assert isinstance(agent_data, AgentPersonalityData)
            assert agent_data.character_id == "test_jovani"
            assert agent_data.character_name == "Test Jovani"
            assert agent_data.engagement_threshold == 0.3
            assert agent_data.cooldown_minutes == 2
            assert agent_data.max_daily_interactions == 100
            assert agent_data.max_replies_per_thread == 2
            assert agent_data.topics_of_interest == ["entertainment", "music", "culture", "social media"]
            assert agent_data.topic_weights == {"entertainment": 0.9, "music": 0.9, "culture": 0.8}
    
    def test_jovani_personality_behavior_methods(self):
        """Test JovaniVazquezPersonality behavior methods with config data."""
        with patch.object(self.loader, 'load_personality', return_value=self.test_config):
            personality = JovaniVazquezPersonality(config_loader=self.loader)
            
            # Test topic relevance
            relevance = personality.get_topic_relevance(["entertainment", "politics"])
            assert relevance > 0.8  # Should be high for entertainment
            
            # Test emotional context
            context = personality.get_emotional_context("entertainment news")
            assert context == "excited"
            
            # Test controversy engagement
            should_engage = personality.should_engage_in_controversy("social justice issues")
            assert should_engage == True
            
            should_not_engage = personality.should_engage_in_controversy("heavy politics debate")
            assert should_not_engage == False
    
    def test_backward_compatibility(self):
        """Test that the system maintains backward compatibility."""
        # Test that the factory function still works
        from app.models.personality import create_jovani_vazquez_personality
        
        # This should work even if config loading fails (fallback to hardcoded)
        personality_data = create_jovani_vazquez_personality()
        assert isinstance(personality_data, PersonalityData)
        assert personality_data.character_id == "jovani_vazquez"
        assert personality_data.character_name == "Jovani Vázquez"
    
    def test_config_loader_integration(self):
        """Test full integration with config loader."""
        # Test loading all personalities
        all_personalities = self.loader.load_all_personalities()
        assert "test_jovani" in all_personalities
        assert all_personalities["test_jovani"] == self.test_config
        
        # Test available characters
        available = self.loader.get_available_characters()
        assert "test_jovani" in available
        
        # Test reloading
        reloaded = self.loader.reload_config("test_jovani")
        assert reloaded == self.test_config 