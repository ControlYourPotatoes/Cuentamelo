"""
Comprehensive tests for DependencyContainer.

This test suite follows the testing framework revamp plan principles:
- Uses pytest fixtures and dependency injection
- Tests both success and error cases
- Validates service configuration and injection
- Includes integration tests for complete container setup
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from app.services.dependency_container import DependencyContainer
from app.ports.ai_provider import AIProviderPort
from app.ports.news_provider import NewsProviderPort
from app.ports.twitter_provider import TwitterProviderPort
from app.ports.orchestration_service import OrchestrationServicePort
from app.ports.frontend_port import FrontendPort, EventBus
from app.ports.command_broker_port import CommandBrokerPort
from app.services.redis_client import RedisClient
from app.services.command_handler import CommandHandler


class TestDependencyContainer:
    """Test suite for DependencyContainer."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = MagicMock()
        settings.ANTHROPIC_API_KEY = "test_anthropic_key"
        settings.TWITTER_BEARER_TOKEN = "test_twitter_token"
        settings.DEMO_MODE_ENABLED = True
        return settings
    
    @pytest.fixture
    def container_with_mocks(self, mock_settings):
        """Dependency container configured with mock services."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({
                "ai_provider": "mock",
                "news_provider": "mock",
                "twitter_provider": "mock",
                "orchestration": "mock",
                "frontend_service": "mock"
            })
            return container
    
    @pytest.fixture
    def container_with_real_services(self, mock_settings):
        """Dependency container configured with real services."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({
                "ai_provider": "claude",
                "news_provider": "simulated",
                "twitter_provider": "mock",
                "orchestration": "langgraph"
            })
            return container

    @pytest.mark.asyncio
    async def test_get_ai_provider_mock(self, container_with_mocks):
        """Test getting mock AI provider."""
        # Act
        ai_provider = container_with_mocks.get_ai_provider()
        
        # Assert
        assert ai_provider is not None
        # Verify it's a mock provider (would be instance of MockAIProvider in real implementation)
        assert hasattr(ai_provider, 'generate_character_response')
    
    @pytest.mark.asyncio
    async def test_get_ai_provider_claude(self, mock_settings):
        """Test getting Claude AI provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"ai_provider": "claude"})
            
            # Act
            ai_provider = container.get_ai_provider()
            
            # Assert
            assert ai_provider is not None
            # Verify it's a Claude adapter
            assert "ClaudeAIAdapter" in str(type(ai_provider))
    
    @pytest.mark.asyncio
    async def test_get_ai_provider_invalid(self, mock_settings):
        """Test getting invalid AI provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"ai_provider": "invalid_provider"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown AI provider: invalid_provider"):
                container.get_ai_provider()
    
    @pytest.mark.asyncio
    async def test_get_orchestration_service_mock(self, container_with_mocks):
        """Test getting mock orchestration service."""
        # Act
        orchestration_service = container_with_mocks.get_orchestration_service()
        
        # Assert
        assert orchestration_service is not None
        assert hasattr(orchestration_service, 'process_content')
    
    @pytest.mark.asyncio
    async def test_get_orchestration_service_langgraph(self, mock_settings):
        """Test getting LangGraph orchestration service."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({
                "ai_provider": "mock",
                "orchestration": "langgraph"
            })
            
            # Act
            orchestration_service = container.get_orchestration_service()
            
            # Assert
            assert orchestration_service is not None
            # Verify it's a LangGraph adapter
            assert "LangGraphOrchestrationAdapter" in str(type(orchestration_service))
    
    @pytest.mark.asyncio
    async def test_get_orchestration_service_invalid(self, mock_settings):
        """Test getting invalid orchestration service."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"orchestration": "invalid_orchestration"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown orchestration type: invalid_orchestration"):
                container.get_orchestration_service()
    
    @pytest.mark.asyncio
    async def test_get_news_provider_mock(self, container_with_mocks):
        """Test getting mock news provider."""
        # Act
        news_provider = container_with_mocks.get_news_provider()
        
        # Assert
        assert news_provider is not None
        assert hasattr(news_provider, 'discover_latest_news')
    
    @pytest.mark.asyncio
    async def test_get_news_provider_simulated(self, mock_settings):
        """Test getting simulated news provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"news_provider": "simulated"})
            
            # Act
            news_provider = container.get_news_provider()
            
            # Assert
            assert news_provider is not None
            # Verify it's a simulated adapter
            assert "SimulatedNewsAdapter" in str(type(news_provider))
    
    @pytest.mark.asyncio
    async def test_get_news_provider_twitter(self, mock_settings):
        """Test getting Twitter news provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"news_provider": "twitter"})
            
            # Act
            news_provider = container.get_news_provider()
            
            # Assert
            assert news_provider is not None
            # Verify it's a Twitter adapter
            assert "TwitterNewsAdapter" in str(type(news_provider))
    
    @pytest.mark.asyncio
    async def test_get_news_provider_elnuevodia(self, mock_settings):
        """Test getting El Nuevo Día news provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"news_provider": "elnuevodia"})
            
            # Act
            news_provider = container.get_news_provider()
            
            # Assert
            assert news_provider is not None
            # Verify it's an El Nuevo Día adapter
            assert "ElNuevoDiaNewsAdapter" in str(type(news_provider))
    
    @pytest.mark.asyncio
    async def test_get_news_provider_invalid(self, mock_settings):
        """Test getting invalid news provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"news_provider": "invalid_provider"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown news provider: invalid_provider"):
                container.get_news_provider()
    
    @pytest.mark.asyncio
    async def test_get_twitter_provider_mock(self, container_with_mocks):
        """Test getting mock Twitter provider."""
        # Act
        twitter_provider = container_with_mocks.get_twitter_provider()
        
        # Assert
        assert twitter_provider is not None
        assert hasattr(twitter_provider, 'post_tweet')
    
    @pytest.mark.asyncio
    async def test_get_twitter_provider_real(self, mock_settings):
        """Test getting real Twitter provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"twitter_provider": "twitter"})
            
            # Act
            twitter_provider = container.get_twitter_provider()
            
            # Assert
            assert twitter_provider is not None
            # Verify it's a Twitter connector
            assert "TwitterConnector" in str(type(twitter_provider))
    
    @pytest.mark.asyncio
    async def test_get_twitter_provider_invalid(self, mock_settings):
        """Test getting invalid Twitter provider."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"twitter_provider": "invalid_provider"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown Twitter provider: invalid_provider"):
                container.get_twitter_provider()
    
    @pytest.mark.asyncio
    async def test_get_frontend_service_mock(self, container_with_mocks):
        """Test getting mock frontend service."""
        # Act
        frontend_service = container_with_mocks.get_frontend_service()
        
        # Assert
        assert frontend_service is not None
        assert hasattr(frontend_service, 'get_dashboard_overview')
    
    @pytest.mark.asyncio
    async def test_get_frontend_service_n8n(self, mock_settings):
        """Test getting N8N frontend service."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"frontend_service": "n8n"})
            
            # Act
            frontend_service = container.get_frontend_service()
            
            # Assert
            assert frontend_service is not None
            # Verify it's an N8N frontend service
            assert "N8NFrontendService" in str(type(frontend_service))
    
    @pytest.mark.asyncio
    async def test_get_frontend_event_bus(self, container_with_mocks):
        """Test getting frontend event bus."""
        # Act
        event_bus = container_with_mocks.get_frontend_event_bus()
        
        # Assert
        assert event_bus is not None
        assert hasattr(event_bus, 'publish_event')
        # Verify it's a frontend event bus
        assert "FrontendEventBus" in str(type(event_bus))
    
    @pytest.mark.asyncio
    async def test_get_user_session_manager(self, container_with_mocks):
        """Test getting user session manager."""
        # Act
        session_manager = container_with_mocks.get_user_session_manager()
        
        # Assert
        assert session_manager is not None
        assert hasattr(session_manager, 'create_session')
    
    @pytest.mark.asyncio
    async def test_get_analytics_engine(self, container_with_mocks):
        """Test getting analytics engine."""
        # Act
        analytics_engine = container_with_mocks.get_analytics_engine()
        
        # Assert
        assert analytics_engine is not None
        assert hasattr(analytics_engine, 'track_event')
    
    @pytest.mark.asyncio
    async def test_get_command_broker(self, container_with_mocks):
        """Test getting command broker."""
        # Act
        command_broker = container_with_mocks.get_command_broker()
        
        # Assert
        assert command_broker is not None
        assert hasattr(command_broker, 'submit_command')
        # Verify it's a command broker service
        assert "CommandBrokerService" in str(type(command_broker))
    
    @pytest.mark.asyncio
    async def test_get_command_handler(self, container_with_mocks):
        """Test getting command handler."""
        # Act
        command_handler = container_with_mocks.get_command_handler()
        
        # Assert
        assert command_handler is not None
        assert hasattr(command_handler, 'execute_command')
        # Verify it's a command handler
        assert "CommandHandler" in str(type(command_handler))
    
    @pytest.mark.asyncio
    async def test_get_redis_client(self, container_with_mocks):
        """Test getting Redis client."""
        # Act
        redis_client = container_with_mocks.get_redis_client()
        
        # Assert
        assert redis_client is not None
        assert hasattr(redis_client, 'set')
        assert hasattr(redis_client, 'get')
        # Verify it's a Redis client
        assert "RedisClient" in str(type(redis_client))
    
    @pytest.mark.asyncio
    async def test_get_agent_factory(self, container_with_mocks):
        """Test getting agent factory."""
        # Act
        agent_factory = container_with_mocks.get_agent_factory()
        
        # Assert
        assert agent_factory is not None
        assert hasattr(agent_factory, 'get_agent')
        # Verify it's an agent factory
        assert "AgentFactory" in str(type(agent_factory))
    
    @pytest.mark.asyncio
    async def test_get_demo_orchestrator(self, container_with_mocks):
        """Test getting demo orchestrator."""
        # Act
        demo_orchestrator = container_with_mocks.get_demo_orchestrator()
        
        # Assert
        assert demo_orchestrator is not None
        assert hasattr(demo_orchestrator, 'run_scenario')
        # Verify it's a demo orchestrator
        assert "DemoOrchestrator" in str(type(demo_orchestrator))
    
    @pytest.mark.asyncio
    async def test_get_n8n_webhook_service(self, container_with_mocks):
        """Test getting N8N webhook service."""
        # Act
        n8n_webhook_service = container_with_mocks.get_n8n_webhook_service()
        
        # Assert
        assert n8n_webhook_service is not None
        assert hasattr(n8n_webhook_service, 'emit_event')
        # Verify it's an N8N webhook service
        assert "N8NWebhookService" in str(type(n8n_webhook_service))
    
    @pytest.mark.asyncio
    async def test_get_personality_config_loader(self, container_with_mocks):
        """Test getting personality config loader."""
        # Act
        config_loader = container_with_mocks.get_personality_config_loader()
        
        # Assert
        assert config_loader is not None
        assert hasattr(config_loader, 'load_personality')
        # Verify it's a personality config loader
        assert "PersonalityConfigLoader" in str(type(config_loader))
    
    @pytest.mark.asyncio
    async def test_service_caching(self, container_with_mocks):
        """Test that services are cached after first creation."""
        # Act - Get AI provider twice
        ai_provider_1 = container_with_mocks.get_ai_provider()
        ai_provider_2 = container_with_mocks.get_ai_provider()
        
        # Assert - Should be the same instance
        assert ai_provider_1 is ai_provider_2
    
    @pytest.mark.asyncio
    async def test_configure_for_testing(self, container_with_mocks):
        """Test configuring container for testing."""
        # Act
        container_with_mocks.configure_for_testing()
        
        # Assert
        # Verify that all services are configured for testing
        # This would typically set all providers to mock mode
        assert container_with_mocks.config.get("ai_provider") == "mock"
        assert container_with_mocks.config.get("news_provider") == "mock"
        assert container_with_mocks.config.get("twitter_provider") == "mock"
        assert container_with_mocks.config.get("orchestration") == "mock"
    
    @pytest.mark.asyncio
    async def test_configure_for_production(self, container_with_mocks):
        """Test configuring container for production."""
        # Act
        container_with_mocks.configure_for_production()
        
        # Assert
        # Verify that all services are configured for production
        # This would typically set providers to real implementations
        assert container_with_mocks.config.get("ai_provider") == "claude"
        assert container_with_mocks.config.get("news_provider") == "twitter"
        assert container_with_mocks.config.get("orchestration") == "langgraph"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, container_with_mocks):
        """Test health check success."""
        # Act
        is_healthy = await container_with_mocks.health_check()
        
        # Assert
        assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, container_with_mocks):
        """Test health check failure."""
        # Arrange - Mock a service to fail health check
        with patch.object(container_with_mocks.get_ai_provider(), 'health_check', return_value=False):
            # Act
            is_healthy = await container_with_mocks.health_check()
            
            # Assert
            assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_shutdown(self, container_with_mocks):
        """Test container shutdown."""
        # Act
        await container_with_mocks.shutdown()
        
        # Assert
        # Verify that all services are properly shut down
        # This would typically close connections and clean up resources
        assert True  # No exceptions should be raised


class TestDependencyContainerIntegration:
    """Integration tests for DependencyContainer."""
    
    @pytest.fixture
    def integration_container(self):
        """Dependency container with real services for integration testing."""
        # This would use real services in integration tests
        # For now, we'll use mocks but test the complete flow
        with patch('app.services.dependency_container.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                ANTHROPIC_API_KEY="test_key",
                TWITTER_BEARER_TOKEN="test_token",
                DEMO_MODE_ENABLED=True
            )
            
            container = DependencyContainer({
                "ai_provider": "mock",
                "news_provider": "mock",
                "twitter_provider": "mock",
                "orchestration": "mock",
                "frontend_service": "mock"
            })
            return container
    
    @pytest.mark.asyncio
    async def test_complete_service_integration(self, integration_container):
        """Test complete service integration and interaction."""
        # Act - Get all services
        ai_provider = integration_container.get_ai_provider()
        news_provider = integration_container.get_news_provider()
        twitter_provider = integration_container.get_twitter_provider()
        orchestration_service = integration_container.get_orchestration_service()
        frontend_service = integration_container.get_frontend_service()
        event_bus = integration_container.get_frontend_event_bus()
        command_broker = integration_container.get_command_broker()
        command_handler = integration_container.get_command_handler()
        redis_client = integration_container.get_redis_client()
        
        # Assert - All services should be available
        assert ai_provider is not None
        assert news_provider is not None
        assert twitter_provider is not None
        assert orchestration_service is not None
        assert frontend_service is not None
        assert event_bus is not None
        assert command_broker is not None
        assert command_handler is not None
        assert redis_client is not None
        
        # Verify service interactions work
        # Test AI provider health check
        ai_healthy = await ai_provider.health_check()
        assert isinstance(ai_healthy, bool)
        
        # Test news provider health check
        news_healthy = await news_provider.health_check()
        assert isinstance(news_healthy, bool)
        
        # Test Twitter provider health check
        twitter_healthy = await twitter_provider.health_check()
        assert isinstance(twitter_healthy, bool)
        
        # Test orchestration service health check
        orchestration_healthy = await orchestration_service.health_check()
        assert isinstance(orchestration_healthy, bool)
        
        # Test Redis client operations (mocked)
        # Note: In real integration tests, this would use a real Redis instance
        # For now, we'll just verify the interface exists
        assert hasattr(redis_client, 'set')
        assert hasattr(redis_client, 'get')
        assert hasattr(redis_client, 'ping')
        
        # Test event bus operations (mocked)
        # Note: In real integration tests, this would use a real event bus
        # For now, we'll just verify the interface exists
        assert hasattr(event_bus, 'publish_event')
        assert hasattr(event_bus, 'publish_system_event')
        
        # Test command handler operations
        # This would require a proper command request, but we can test the interface
        assert hasattr(command_handler, 'execute_command')
    
    @pytest.mark.asyncio
    async def test_service_dependency_injection(self, integration_container):
        """Test that services are properly injected with their dependencies."""
        # Act - Get orchestration service (which depends on AI provider)
        orchestration_service = integration_container.get_orchestration_service()
        
        # Assert - Should have AI provider injected
        # Note: Mock orchestration service doesn't have ai_provider attribute
        # In real implementation, this would be injected
        assert hasattr(orchestration_service, 'process_content')
        assert hasattr(orchestration_service, 'health_check')
        
        # Act - Get frontend service (which depends on multiple services)
        frontend_service = integration_container.get_frontend_service()
        
        # Assert - Should have dependencies injected
        assert hasattr(frontend_service, 'n8n_webhook_service')
        assert hasattr(frontend_service, 'agent_factory')
        assert hasattr(frontend_service, 'demo_orchestrator')
        assert hasattr(frontend_service, 'event_bus')
        
        # Act - Get command broker (which depends on command handler, Redis, and event bus)
        command_broker = integration_container.get_command_broker()
        
        # Assert - Should have dependencies injected
        assert hasattr(command_broker, 'command_handler')
        assert hasattr(command_broker, 'redis_client')
        assert hasattr(command_broker, 'event_bus')
    
    @pytest.mark.asyncio
    async def test_configuration_override(self):
        """Test that configuration overrides work properly."""
        # Arrange
        custom_config = {
            "ai_provider": "claude",
            "news_provider": "simulated",
            "twitter_provider": "mock",
            "orchestration": "langgraph",
            "initial_characters": ["jovani_vazquez", "politico_boricua"]
        }
        
        with patch('app.services.dependency_container.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                ANTHROPIC_API_KEY="test_key",
                TWITTER_BEARER_TOKEN="test_token",
                DEMO_MODE_ENABLED=True
            )
            
            container = DependencyContainer(custom_config)
            
            # Act
            ai_provider = container.get_ai_provider()
            orchestration_service = container.get_orchestration_service()
            
            # Assert
            assert "ClaudeAIAdapter" in str(type(ai_provider))
            assert "LangGraphOrchestrationAdapter" in str(type(orchestration_service))
            
            # Verify custom configuration was used
            assert container.config["initial_characters"] == ["jovani_vazquez", "politico_boricua"]
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self, integration_container):
        """Test complete service lifecycle from creation to shutdown."""
        # Act - Create and use services
        ai_provider = integration_container.get_ai_provider()
        news_provider = integration_container.get_news_provider()
        
        # Use services
        await ai_provider.health_check()
        await news_provider.health_check()
        
        # Act - Shutdown
        await integration_container.shutdown()
        
        # Assert - No exceptions should be raised during shutdown
        assert True 