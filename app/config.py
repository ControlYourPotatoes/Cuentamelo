from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Cuentamelo"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/cuentamelo"
    redis_url: str = "redis://:cuentamelo_redis@localhost:6379/0"

    # APIs
    anthropic_api_key: str = ""
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # Character settings
    default_language: str = "es-pr"
    posting_rate_limit: int = 10
    interaction_cooldown: int = 900
    max_conversation_turns: int = 6

    class Config:
        env_file = ".env"

settings = Settings() 