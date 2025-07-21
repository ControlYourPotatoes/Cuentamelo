"""
Tests for the personality configuration loader service.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.personality_config_loader import PersonalityConfigLoader


class TestPersonalityConfigLoader:
    """Test cases for PersonalityConfigLoader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "personalities"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.loader = PersonalityConfigLoader(str(self.config_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directory(self):
        """Test that initialization creates the config directory."""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "nonexistent" / "personalities"
        
        try:
            loader = PersonalityConfigLoader(str(config_dir))
            assert config_dir.exists()
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config_data = {
            "character_id": "test_character",
            "character_name": "Test Character",
            "character_type": "influencer",
            "personality": {
                "traits": "Test personality traits",
                "background": "Test background",
                "language_style": "spanglish",
                "interaction_style": "Test interaction style",
                "cultural_context": "Test cultural context"
            },
            "engagement": {
                "threshold": 0.5,
                "cooldown_minutes": 15,
                "max_daily_interactions": 50,
                "max_replies_per_thread": 2
            },
            "topics": {
                "of_interest": ["test"],
                "weights": {},
                "preferred": [],
                "avoided": []
            },
            "language": {
                "signature_phrases": [],
                "common_expressions": [],
                "emoji_preferences": [],
                "patterns": {}
            },
            "responses": {
                "examples": {},
                "templates": {}
            },
            "energy": {
                "base_level": 0.5,
                "tone_preferences": {},
                "emotional_triggers": {}
            },
            "cultural": {
                "puerto_rico_references": [],
                "local_places": [],
                "cultural_events": [],
                "local_foods": []
            },
            "behavior": {
                "hashtag_style": "natural",
                "mention_behavior": "selective",
                "retweet_preferences": [],
                "thread_behavior": "conversational"
            },
            "validation": {
                "personality_consistency_rules": [],
                "content_guidelines": []
            }
        }
        
        config_file = self.config_dir / "test_character.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        loaded_config = self.loader.load_personality("test_character")
        assert loaded_config == config_data
    
    def test_load_nonexistent_config(self):
        """Test loading a configuration that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_personality("nonexistent")
    
    def test_load_invalid_json(self):
        """Test loading a configuration with invalid JSON."""
        config_file = self.config_dir / "invalid.json"
        with open(config_file, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(ValueError):
            self.loader.load_personality("invalid")
    
    def test_caching(self):
        """Test that configurations are cached."""
        config_data = {
            "character_id": "cached_character",
            "character_name": "Cached Character",
            "character_type": "influencer",
            "personality": {
                "traits": "Test traits",
                "background": "Test background",
                "language_style": "spanglish",
                "interaction_style": "Test style",
                "cultural_context": "Test context"
            },
            "engagement": {"threshold": 0.5, "cooldown_minutes": 15, "max_daily_interactions": 50, "max_replies_per_thread": 2},
            "topics": {"of_interest": [], "weights": {}, "preferred": [], "avoided": []},
            "language": {"signature_phrases": [], "common_expressions": [], "emoji_preferences": [], "patterns": {}},
            "responses": {"examples": {}, "templates": {}},
            "energy": {"base_level": 0.5, "tone_preferences": {}, "emotional_triggers": {}},
            "cultural": {"puerto_rico_references": [], "local_places": [], "cultural_events": [], "local_foods": []},
            "behavior": {"hashtag_style": "natural", "mention_behavior": "selective", "retweet_preferences": [], "thread_behavior": "conversational"},
            "validation": {"personality_consistency_rules": [], "content_guidelines": []}
        }
        
        config_file = self.config_dir / "cached_character.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # First load should cache
        config1 = self.loader.load_personality("cached_character")
        
        # Remove file to test caching
        config_file.unlink()
        
        # Second load should use cache
        config2 = self.loader.load_personality("cached_character")
        
        assert config1 == config2
    
    def test_clear_cache(self):
        """Test clearing the configuration cache."""
        config_data = {
            "character_id": "cache_test",
            "character_name": "Cache Test",
            "character_type": "influencer",
            "personality": {
                "traits": "Test traits",
                "background": "Test background",
                "language_style": "spanglish",
                "interaction_style": "Test style",
                "cultural_context": "Test context"
            },
            "engagement": {"threshold": 0.5, "cooldown_minutes": 15, "max_daily_interactions": 50, "max_replies_per_thread": 2},
            "topics": {"of_interest": [], "weights": {}, "preferred": [], "avoided": []},
            "language": {"signature_phrases": [], "common_expressions": [], "emoji_preferences": [], "patterns": {}},
            "responses": {"examples": {}, "templates": {}},
            "energy": {"base_level": 0.5, "tone_preferences": {}, "emotional_triggers": {}},
            "cultural": {"puerto_rico_references": [], "local_places": [], "cultural_events": [], "local_foods": []},
            "behavior": {"hashtag_style": "natural", "mention_behavior": "selective", "retweet_preferences": [], "thread_behavior": "conversational"},
            "validation": {"personality_consistency_rules": [], "content_guidelines": []}
        }
        
        config_file = self.config_dir / "cache_test.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Load to populate cache
        self.loader.load_personality("cache_test")
        assert "cache_test" in self.loader._cache
        
        # Clear cache
        self.loader.clear_cache()
        assert len(self.loader._cache) == 0
    
    def test_get_available_characters(self):
        """Test getting list of available characters."""
        # Create some test config files
        characters = ["char1", "char2", "char3"]
        for char in characters:
            config_data = {
                "character_id": char,
                "character_name": f"Character {char}",
                "character_type": "influencer",
                "personality": {
                    "traits": "Test traits",
                    "background": "Test background",
                    "language_style": "spanglish",
                    "interaction_style": "Test style",
                    "cultural_context": "Test context"
                },
                "engagement": {"threshold": 0.5, "cooldown_minutes": 15, "max_daily_interactions": 50, "max_replies_per_thread": 2},
                "topics": {"of_interest": [], "weights": {}, "preferred": [], "avoided": []},
                "language": {"signature_phrases": [], "common_expressions": [], "emoji_preferences": [], "patterns": {}},
                "responses": {"examples": {}, "templates": {}},
                "energy": {"base_level": 0.5, "tone_preferences": {}, "emotional_triggers": {}},
                "cultural": {"puerto_rico_references": [], "local_places": [], "cultural_events": [], "local_foods": []},
                "behavior": {"hashtag_style": "natural", "mention_behavior": "selective", "retweet_preferences": [], "thread_behavior": "conversational"},
                "validation": {"personality_consistency_rules": [], "content_guidelines": []}
            }
            
            config_file = self.config_dir / f"{char}.json"
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
        
        # Also create schema file (should be ignored)
        schema_file = self.config_dir / "schema.json"
        with open(schema_file, 'w') as f:
            json.dump({}, f)
        
        available = self.loader.get_available_characters()
        assert set(available) == set(characters)
    
    def test_create_default_config(self):
        """Test creating a default configuration template."""
        default_config = self.loader.create_default_config(
            "test_id", "Test Name", "influencer"
        )
        
        assert default_config["character_id"] == "test_id"
        assert default_config["character_name"] == "Test Name"
        assert default_config["character_type"] == "influencer"
        assert "personality" in default_config
        assert "engagement" in default_config
        assert "topics" in default_config
    
    def test_save_config(self):
        """Test saving a configuration to file."""
        config_data = {
            "character_id": "save_test",
            "character_name": "Save Test",
            "character_type": "influencer",
            "personality": {
                "traits": "Test traits",
                "background": "Test background",
                "language_style": "spanglish",
                "interaction_style": "Test style",
                "cultural_context": "Test context"
            },
            "engagement": {"threshold": 0.5, "cooldown_minutes": 15, "max_daily_interactions": 50, "max_replies_per_thread": 2},
            "topics": {"of_interest": [], "weights": {}, "preferred": [], "avoided": []},
            "language": {"signature_phrases": [], "common_expressions": [], "emoji_preferences": [], "patterns": {}},
            "responses": {"examples": {}, "templates": {}},
            "energy": {"base_level": 0.5, "tone_preferences": {}, "emotional_triggers": {}},
            "cultural": {"puerto_rico_references": [], "local_places": [], "cultural_events": [], "local_foods": []},
            "behavior": {"hashtag_style": "natural", "mention_behavior": "selective", "retweet_preferences": [], "thread_behavior": "conversational"},
            "validation": {"personality_consistency_rules": [], "content_guidelines": []}
        }
        
        # Save config
        success = self.loader.save_config("save_test", config_data)
        assert success
        
        # Verify file was created
        config_file = self.config_dir / "save_test.json"
        assert config_file.exists()
        
        # Verify cache was updated
        assert "save_test" in self.loader._cache
        
        # Verify content
        with open(config_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == config_data 
    
    def test_signature_phrases_structure_and_validation(self):
        """Test loading and validating signature_phrases with new structure and invalid frequency."""
        import shutil
        schema_path = self.config_dir / "schema.json"
        shutil.copyfile("configs/personalities/schema.json", schema_path)

        # Now re-initialize the loader so it picks up the schema
        self.loader = PersonalityConfigLoader(str(self.config_dir))

        # Valid config
        config_data = {
            "character_id": "sigtest",
            "character_name": "Sig Test",
            "character_type": "influencer",
            "personality": {
                "traits": "Test traits",
                "background": "Test background",
                "language_style": "spanglish",
                "interaction_style": "Test style",
                "cultural_context": "Test context"
            },
            "engagement": {"threshold": 0.5, "cooldown_minutes": 15, "max_daily_interactions": 50, "max_replies_per_thread": 2},
            "topics": {"of_interest": [], "weights": {}, "preferred": [], "avoided": []},
            "language": {
                "signature_phrases": [
                    {"text": "Test phrase 1", "frequency": "common"},
                    {"text": "Test phrase 2", "frequency": "rare"},
                    {"text": "Test phrase 3"}
                ],
                "common_expressions": [], "emoji_preferences": [], "patterns": {}
            },
            "responses": {"examples": {}, "templates": {}},
            "energy": {"base_level": 0.5, "tone_preferences": {}, "emotional_triggers": {}},
            "cultural": {"puerto_rico_references": [], "local_places": [], "cultural_events": [], "local_foods": []},
            "behavior": {"hashtag_style": "natural", "mention_behavior": "selective", "retweet_preferences": [], "thread_behavior": "conversational"},
            "validation": {"personality_consistency_rules": [], "content_guidelines": []}
        }
        config_file = self.config_dir / "sigtest.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        loaded_config = self.loader.load_personality("sigtest")
        assert loaded_config["language"]["signature_phrases"][0]["text"] == "Test phrase 1"
        # Invalid frequency
        config_data["language"]["signature_phrases"][0]["frequency"] = "invalid_freq"
        config_file = self.config_dir / "sigtest_invalid.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        with pytest.raises(ValueError):
            self.loader.load_personality("sigtest_invalid") 