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
        from urllib.parse import urlparse
        settings = Settings()
        db_url = urlparse(settings.database_url)
        assert db_url.scheme == "postgresql"
        assert db_url.port == 5432
        assert db_url.hostname in ["localhost", "db"]
        assert db_url.path.endswith("cuentamelo")
    
    def test_redis_url_has_correct_format(self):
        """Should have properly formatted Redis URL"""
        from urllib.parse import urlparse
        settings = Settings()
        redis_url = urlparse(settings.redis_url)
        assert redis_url.scheme == "redis"
        assert redis_url.port == 6379
        assert redis_url.hostname in ["localhost", "redis"]
        assert redis_url.path == "/0"
    
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
        assert isinstance(settings.ANTHROPIC_API_KEY, str)
        assert settings.TWITTER_API_KEY is None or isinstance(settings.TWITTER_API_KEY, str) 