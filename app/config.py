from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import uuid

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")  # Ignore extra environment variables
    
    app_name: str = "Cuentamelo"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/cuentamelo"
    redis_url: str = "redis://:cuentamelo_redis@localhost:6379/0"

    # APIs
    ANTHROPIC_API_KEY: str = ""
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # Character settings
    default_language: str = "es-pr"
    posting_rate_limit: int = 10
    interaction_cooldown: int = 900
    max_conversation_turns: int = 6

    # N8N Integration Settings
    N8N_WEBHOOK_URL: str = "http://localhost:5678"
    DEMO_MODE_ENABLED: bool = False
    DEMO_SESSION_ID: str = str(uuid.uuid4())
    N8N_WEBHOOK_TIMEOUT: int = 5
    DEMO_SPEED_MULTIPLIER: float = 1.0


def get_settings():
    """Get the global settings instance."""
    return Settings()

settings = Settings() 