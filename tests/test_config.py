import pytest
from app.config import Settings


class TestConfiguration:
    """Test configuration loading and validation"""
    
    def test_default_settings_load_successfully(self):
        """Should load configuration with default values"""
        settings = Settings()
        
        assert settings.app_name == "Cuentamelo"
        assert settings.debug is True
        assert settings.log_level == "INFO"
        assert settings.default_language == "es-pr"
        assert settings.posting_rate_limit == 10
        assert settings.max_conversation_turns == 6
    
    def test_database_url_has_correct_format(self):
        """Should have properly formatted database URL"""
        settings = Settings()
        
        assert "postgresql://" in settings.database_url
        assert "localhost:5432" in settings.database_url
        assert "cuentamelo" in settings.database_url
    
    def test_redis_url_has_correct_format(self):
        """Should have properly formatted Redis URL"""
        settings = Settings()
        
        assert "redis://" in settings.redis_url
        assert "localhost:6379" in settings.redis_url
    
    def test_character_settings_have_reasonable_defaults(self):
        """Should have sensible defaults for character behavior"""
        settings = Settings()
        
        assert settings.posting_rate_limit > 0
        assert settings.interaction_cooldown > 0
        assert settings.max_conversation_turns > 0
        assert settings.default_language == "es-pr"
    
    def test_api_keys_can_be_empty_strings(self):
        """Should handle missing API keys gracefully"""
        settings = Settings()
        
        # Should not raise errors even with empty keys
        assert isinstance(settings.anthropic_api_key, str)
        assert settings.twitter_api_key is None or isinstance(settings.twitter_api_key, str) 