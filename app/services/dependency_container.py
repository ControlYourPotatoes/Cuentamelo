"""
Dependency Injection Container - Wires together all our ports and adapters.
This demonstrates how dependency injection makes the system flexible and testable.
"""
from typing import Dict, Any, Optional
import logging
from functools import lru_cache
import json
import os

from app.ports.ai_provider import AIProviderPort
from app.ports.orchestration_service import OrchestrationServicePort
from app.ports.news_provider import NewsProviderPort
from app.adapters.claude_ai_adapter import ClaudeAIAdapter
from app.adapters.langgraph_orchestration_adapter import LangGraphOrchestrationAdapter
from app.adapters.twitter_news_adapter import TwitterNewsAdapter
from app.adapters.simulated_news_adapter import SimulatedNewsAdapter
from app.tools.claude_client import ClaudeClient
from app.tools.twitter_connector import TwitterConnector
from app.services.personality_config_loader import PersonalityConfigLoader
from app.services.redis_client import RedisClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class DependencyContainer:
    """
    Dependency Injection Container that wires together our ports and adapters.
    
    This demonstrates the key benefits of dependency injection:
    - Easy testing (inject mocks)
    - Configuration flexibility (swap implementations)
    - Loose coupling (depend on interfaces, not concrete classes)
    - Single responsibility (each class has one job)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the container with optional configuration.
        
        Args:
            config: Override configuration for testing/customization
        """
        self.config = config or {}
        self.settings = get_settings()
        self._services: Dict[str, Any] = {}
        
        # Register configuration loader
        self.personality_config_loader = PersonalityConfigLoader()
        
        logger.info("Dependency container initialized")
    
    @lru_cache(maxsize=1)
    def get_ai_provider(self) -> AIProviderPort:
        """
        Get the AI provider service.
        
        This demonstrates dependency injection - we return an interface,
        not a concrete implementation. This makes testing and swapping easier.
        """
        if "ai_provider" not in self._services:
            
            # Check configuration for which AI provider to use
            provider_type = self.config.get("ai_provider", "claude")
            
            if provider_type == "claude":
                # Create Claude client with dependency injection
                claude_client = ClaudeClient(
                    api_key=self.settings.ANTHROPIC_API_KEY
                )
                self._services["ai_provider"] = ClaudeAIAdapter(claude_client)
                
            elif provider_type == "mock":
                # For testing - inject a mock provider
                self._services["ai_provider"] = self._create_mock_ai_provider()
                
            else:
                raise ValueError(f"Unknown AI provider: {provider_type}")
            
            logger.info(f"Created AI provider: {provider_type}")
        
        return self._services["ai_provider"]
    
    @lru_cache(maxsize=1)
    def get_orchestration_service(self) -> OrchestrationServicePort:
        """
        Get the orchestration service.
        
        This is THE KEY SERVICE that provides clean access to LangGraph!
        Notice how it depends on the AI provider interface, not concrete implementation.
        """
        if "orchestration_service" not in self._services:
            
            # Inject the AI provider dependency
            ai_provider = self.get_ai_provider()
            
            # Check configuration for orchestration type
            orchestration_type = self.config.get("orchestration", "langgraph")
            
            if orchestration_type == "langgraph":
                self._services["orchestration_service"] = LangGraphOrchestrationAdapter(
                    ai_provider=ai_provider,
                    initial_characters=self.config.get("initial_characters", ["jovani_vazquez"])
                )
                
            elif orchestration_type == "mock":
                # For testing - inject a mock orchestration service
                self._services["orchestration_service"] = self._create_mock_orchestration_service()
                
            else:
                raise ValueError(f"Unknown orchestration type: {orchestration_type}")
            
            logger.info(f"Created orchestration service: {orchestration_type}")
        
        return self._services["orchestration_service"]
    
    @lru_cache(maxsize=1)
    def get_news_provider(self) -> NewsProviderPort:
        """
        Get the news provider service.
        
        This demonstrates dependency injection - we return an interface,
        not a concrete implementation. This makes testing and swapping easier.
        """
        if "news_provider" not in self._services:
            
            # Check configuration for which news provider to use
            provider_type = self.config.get("news_provider", "simulated")
            
            if provider_type == "twitter":
                # Create Twitter news adapter with dependency injection
                twitter_connector = TwitterConnector()
                redis_client = RedisClient()
                
                # Load news sources configuration
                news_sources_config = self._load_news_sources_config()
                
                self._services["news_provider"] = TwitterNewsAdapter(
                    twitter_connector=twitter_connector,
                    redis_client=redis_client,
                    news_sources_config=news_sources_config
                )
                
            elif provider_type == "simulated":
                # Create simulated news adapter for demos and testing
                demo_scenarios_config = self._load_demo_scenarios_config()
                
                self._services["news_provider"] = SimulatedNewsAdapter(
                    demo_scenarios_config=demo_scenarios_config
                )
                
            elif provider_type == "mock":
                # For testing - inject a mock provider
                self._services["news_provider"] = self._create_mock_news_provider()
                
            else:
                raise ValueError(f"Unknown news provider: {provider_type}")
            
            logger.info(f"Created news provider: {provider_type}")
        
        return self._services["news_provider"]

    @lru_cache(maxsize=1)
    def get_personality_config_loader(self) -> PersonalityConfigLoader:
        """
        Get the personality configuration loader service.
        
        This service provides access to personality configurations from JSON files.
        """
        return self.personality_config_loader
    
    def _load_news_sources_config(self) -> Dict[str, Any]:
        """Load news sources configuration from JSON file."""
        try:
            config_path = os.path.join("configs", "news_sources.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load news sources config: {str(e)}")
            return {"sources": [], "keywords": {}, "hashtags": {}}

    def _load_demo_scenarios_config(self) -> Dict[str, Any]:
        """Load demo scenarios configuration from JSON file."""
        try:
            config_path = os.path.join("configs", "demo_news.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load demo scenarios config: {str(e)}")
            return {"scenarios": []}
    
    def _create_mock_ai_provider(self) -> AIProviderPort:
        """Create a mock AI provider for testing."""
        from app.tests.mocks.mock_ai_provider import MockAIProvider
        return MockAIProvider()
    
    def _create_mock_orchestration_service(self) -> OrchestrationServicePort:
        """Create a mock orchestration service for testing."""
        from app.tests.mocks.mock_orchestration_service import MockOrchestrationService
        return MockOrchestrationService()

    def _create_mock_news_provider(self) -> NewsProviderPort:
        """Create a mock news provider for testing."""
        from app.tests.mocks.mock_news_provider import MockNewsProvider
        return MockNewsProvider()
    
    def configure_for_testing(self):
        """Configure the container for testing with mocks."""
        self.config.update({
            "ai_provider": "mock",
            "orchestration": "mock",
            "news_provider": "mock"
        })
        self._services.clear()  # Clear cached services
        logger.info("Container configured for testing")
    
    def configure_for_production(self):
        """Configure the container for production."""
        self.config.update({
            "ai_provider": "claude",
            "orchestration": "langgraph",
            "news_provider": "twitter"
        })
        self._services.clear()  # Clear cached services
        logger.info("Container configured for production")
    
    async def health_check(self) -> bool:
        """Check health of all services."""
        try:
            ai_provider = self.get_ai_provider()
            orchestration_service = self.get_orchestration_service()
            news_provider = self.get_news_provider()
            
            ai_healthy = await ai_provider.health_check()
            orchestration_healthy = await orchestration_service.health_check()
            news_healthy = await news_provider.health_check()
            
            return ai_healthy and orchestration_healthy and news_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown all services."""
        try:
            if "orchestration_service" in self._services:
                orchestration_service = self._services["orchestration_service"]
                await orchestration_service.shutdown_gracefully()
            
            logger.info("All services shutdown gracefully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def configure_container_for_testing():
    """Configure the global container for testing."""
    container = get_container()
    container.configure_for_testing()


def configure_container_for_production():
    """Configure the global container for production."""
    container = get_container()
    container.configure_for_production() 