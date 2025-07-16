"""
Tests for Dependency Container.

This module tests the dependency injection container which wires together
all ports and adapters, making the system flexible and testable.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.services.dependency_container import DependencyContainer, get_container
from app.ports.ai_provider import AIProviderPort
from app.ports.news_provider import NewsProviderPort
from app.ports.twitter_provider import TwitterProviderPort
from app.ports.orchestration_service import OrchestrationServicePort
from app.ports.frontend_port import FrontendPort, EventBus, UserSessionManager, AnalyticsEngine
from app.ports.command_broker_port import CommandBrokerPort


class TestDependencyContainer:
    """Test suite for DependencyContainer."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = MagicMock()
        settings.ANTHROPIC_API_KEY = "test_api_key"
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
                "orchestration": "mock"
            })
            return container
    
    @pytest.fixture
    def container_with_real_services(self, mock_settings):
        """Dependency container configured with real services."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({
                "ai_provider": "claude",
                "news_provider": "simulated",
                "twitter_provider": "mock"
            })
            return container
    
    def test_container_initialization(self, mock_settings):
        """Test container initialization."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Act
            container = DependencyContainer()
            
            # Assert
            assert container.settings == mock_settings
            assert container.config == {}
            assert hasattr(container, '_services')
            assert hasattr(container, 'personality_config_loader')
    
    def test_container_initialization_with_config(self, mock_settings):
        """Test container initialization with custom configuration."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Arrange
            config = {
                "ai_provider": "mock",
                "news_provider": "simulated",
                "custom_setting": "test_value"
            }
            
            # Act
            container = DependencyContainer(config)
            
            # Assert
            assert container.config == config
            assert container.config["custom_setting"] == "test_value"
    
    def test_get_ai_provider_mock(self, container_with_mocks):
        """Test getting mock AI provider."""
        # Act
        ai_provider = container_with_mocks.get_ai_provider()
        
        # Assert
        assert isinstance(ai_provider, AIProviderPort)
        assert hasattr(ai_provider, 'generate_response')
    
    def test_get_ai_provider_claude(self, container_with_real_services):
        """Test getting Claude AI provider."""
        # Act
        ai_provider = container_with_real_services.get_ai_provider()
        
        # Assert
        assert isinstance(ai_provider, AIProviderPort)
        assert hasattr(ai_provider, 'generate_response')
    
    def test_get_ai_provider_invalid_type(self, mock_settings):
        """Test getting AI provider with invalid type."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"ai_provider": "invalid_type"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown AI provider: invalid_type"):
                container.get_ai_provider()
    
    def test_get_news_provider_mock(self, container_with_mocks):
        """Test getting mock news provider."""
        # Act
        news_provider = container_with_mocks.get_news_provider()
        
        # Assert
        assert isinstance(news_provider, NewsProviderPort)
        assert hasattr(news_provider, 'get_latest_news')
    
    def test_get_news_provider_simulated(self, container_with_real_services):
        """Test getting simulated news provider."""
        # Act
        news_provider = container_with_real_services.get_news_provider()
        
        # Assert
        assert isinstance(news_provider, NewsProviderPort)
        assert hasattr(news_provider, 'discover_latest_news')
    
    def test_get_news_provider_invalid_type(self, mock_settings):
        """Test getting news provider with invalid type."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"news_provider": "invalid_type"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown news provider: invalid_type"):
                container.get_news_provider()
    
    def test_get_twitter_provider_mock(self, container_with_mocks):
        """Test getting mock Twitter provider."""
        # Act
        twitter_provider = container_with_mocks.get_twitter_provider()
        
        # Assert
        assert isinstance(twitter_provider, TwitterProviderPort)
        assert hasattr(twitter_provider, 'post_tweet')
    
    def test_get_orchestration_service_mock(self, container_with_mocks):
        """Test getting mock orchestration service."""
        # Act
        orchestration_service = container_with_mocks.get_orchestration_service()
        
        # Assert
        assert isinstance(orchestration_service, OrchestrationServicePort)
        assert hasattr(orchestration_service, 'execute_orchestration_cycle')
    
    def test_get_orchestration_service_langgraph(self, container_with_real_services):
        """Test getting LangGraph orchestration service."""
        # Act
        orchestration_service = container_with_real_services.get_orchestration_service()
        
        # Assert
        assert isinstance(orchestration_service, OrchestrationServicePort)
        assert hasattr(orchestration_service, 'execute_orchestration_cycle')
    
    def test_get_orchestration_service_invalid_type(self, mock_settings):
        """Test getting orchestration service with invalid type."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({"orchestration": "invalid_type"})
            
            # Act & Assert
            with pytest.raises(ValueError, match="Unknown orchestration type: invalid_type"):
                container.get_orchestration_service()
    
    def test_get_frontend_service(self, container_with_mocks):
        """Test getting frontend service."""
        # Act
        frontend_service = container_with_mocks.get_frontend_service()
        
        # Assert
        assert isinstance(frontend_service, FrontendPort)
        assert hasattr(frontend_service, 'get_dashboard_overview')
    
    def test_get_frontend_event_bus(self, container_with_mocks):
        """Test getting frontend event bus."""
        # Act
        event_bus = container_with_mocks.get_frontend_event_bus()
        
        # Assert
        assert isinstance(event_bus, EventBus)
        assert hasattr(event_bus, 'publish_event')
    
    def test_get_user_session_manager(self, container_with_mocks):
        """Test getting user session manager."""
        # Act
        session_manager = container_with_mocks.get_user_session_manager()
        
        # Assert
        assert isinstance(session_manager, UserSessionManager)
        assert hasattr(session_manager, 'create_session')
    
    def test_get_analytics_engine(self, container_with_mocks):
        """Test getting analytics engine."""
        # Act
        analytics_engine = container_with_mocks.get_analytics_engine()
        
        # Assert
        assert isinstance(analytics_engine, AnalyticsEngine)
        assert hasattr(analytics_engine, 'track_event')
    
    def test_get_command_broker(self, container_with_mocks):
        """Test getting command broker."""
        # Act
        command_broker = container_with_mocks.get_command_broker()
        
        # Assert
        assert isinstance(command_broker, CommandBrokerPort)
        assert hasattr(command_broker, 'submit_command')
    
    def test_get_command_handler(self, container_with_mocks):
        """Test getting command handler."""
        # Act
        command_handler = container_with_mocks.get_command_handler()
        
        # Assert
        assert hasattr(command_handler, 'execute_command')
    
    def test_get_redis_client(self, container_with_mocks):
        """Test getting Redis client."""
        # Act
        redis_client = container_with_mocks.get_redis_client()
        
        # Assert
        assert hasattr(redis_client, 'set')
        assert hasattr(redis_client, 'get')
        assert hasattr(redis_client, 'publish')
    
    def test_get_agent_factory(self, container_with_mocks):
        """Test getting agent factory."""
        # Act
        agent_factory = container_with_mocks.get_agent_factory()
        
        # Assert
        assert hasattr(agent_factory, 'create_agent')
        assert hasattr(agent_factory, 'get_available_agents')
    
    def test_get_demo_orchestrator(self, container_with_mocks):
        """Test getting demo orchestrator."""
        # Act
        demo_orchestrator = container_with_mocks.get_demo_orchestrator()
        
        # Assert
        assert hasattr(demo_orchestrator, 'get_available_scenarios')
        assert hasattr(demo_orchestrator, 'get_demo_status')
    
    def test_get_n8n_webhook_service(self, container_with_mocks):
        """Test getting N8N webhook service."""
        # Act
        n8n_service = container_with_mocks.get_n8n_webhook_service()
        
        # Assert
        assert hasattr(n8n_service, 'emit_event')
        assert hasattr(n8n_service, 'test_connection')
    
    def test_get_personality_config_loader(self, container_with_mocks):
        """Test getting personality config loader."""
        # Act
        config_loader = container_with_mocks.get_personality_config_loader()
        
        # Assert
        assert hasattr(config_loader, 'load_personality_config')
        assert hasattr(config_loader, 'get_available_personalities')
    
    def test_service_caching(self, container_with_mocks):
        """Test that services are cached after first creation."""
        # Act
        service1 = container_with_mocks.get_ai_provider()
        service2 = container_with_mocks.get_ai_provider()
        
        # Assert
        assert service1 is service2  # Same instance due to caching
    
    def test_configure_for_testing(self, container_with_mocks):
        """Test configuring container for testing."""
        # Act
        container_with_mocks.configure_for_testing()
        
        # Assert
        # Verify that all services are configured for testing
        ai_provider = container_with_mocks.get_ai_provider()
        news_provider = container_with_mocks.get_news_provider()
        twitter_provider = container_with_mocks.get_twitter_provider()
        
        assert isinstance(ai_provider, AIProviderPort)
        assert isinstance(news_provider, NewsProviderPort)
        assert isinstance(twitter_provider, TwitterProviderPort)
    
    def test_configure_for_production(self, container_with_real_services):
        """Test configuring container for production."""
        # Act
        container_with_real_services.configure_for_production()
        
        # Assert
        # Verify that services are configured for production
        ai_provider = container_with_real_services.get_ai_provider()
        news_provider = container_with_real_services.get_news_provider()
        
        assert isinstance(ai_provider, AIProviderPort)
        assert isinstance(news_provider, NewsProviderPort)
    
    @pytest.mark.asyncio
    async def test_health_check(self, container_with_mocks):
        """Test container health check."""
        # Act
        is_healthy = await container_with_mocks.health_check()
        
        # Assert
        assert isinstance(is_healthy, bool)
    
    @pytest.mark.asyncio
    async def test_shutdown(self, container_with_mocks):
        """Test container shutdown."""
        # Act
        await container_with_mocks.shutdown()
        
        # Assert
        # Verify no exceptions are raised during shutdown
        assert True
    
    def test_get_container_singleton(self, mock_settings):
        """Test get_container returns singleton instance."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Act
            container1 = get_container()
            container2 = get_container()
            
            # Assert
            assert container1 is container2  # Same instance
    
    def test_configure_container_for_testing(self, mock_settings):
        """Test configure_container_for_testing function."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Act
            container = get_container()
            container.configure_for_testing()
            
            # Assert
            # Verify container is configured for testing
            ai_provider = container.get_ai_provider()
            assert isinstance(ai_provider, AIProviderPort)
    
    def test_configure_container_for_production(self, mock_settings):
        """Test configure_container_for_production function."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Act
            container = get_container()
            container.configure_for_production()
            
            # Assert
            # Verify container is configured for production
            ai_provider = container.get_ai_provider()
            assert isinstance(ai_provider, AIProviderPort)
    
    def test_dependency_injection_benefits(self, container_with_mocks):
        """Test that dependency injection provides expected benefits."""
        # Test 1: Easy testing (inject mocks)
        ai_provider = container_with_mocks.get_ai_provider()
        assert isinstance(ai_provider, AIProviderPort)
        
        # Test 2: Configuration flexibility (swap implementations)
        container_simulated = DependencyContainer({"news_provider": "simulated"})
        news_provider = container_simulated.get_news_provider()
        assert isinstance(news_provider, NewsProviderPort)
        
        # Test 3: Loose coupling (depend on interfaces, not concrete classes)
        orchestration_service = container_with_mocks.get_orchestration_service()
        assert isinstance(orchestration_service, OrchestrationServicePort)
    
    def test_service_dependencies(self, container_with_mocks):
        """Test that services can depend on other services."""
        # Act
        orchestration_service = container_with_mocks.get_orchestration_service()
        
        # Assert
        # The orchestration service should have access to the AI provider
        assert hasattr(orchestration_service, 'ai_provider')
        assert isinstance(orchestration_service.ai_provider, AIProviderPort)
    
    def test_error_handling_in_service_creation(self, mock_settings):
        """Test error handling when creating services fails."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            # Test with invalid configuration
            container = DependencyContainer({"ai_provider": "invalid"})
            
            # Act & Assert
            with pytest.raises(ValueError):
                container.get_ai_provider()
    
    def test_mock_service_creation(self, mock_settings):
        """Test creation of mock services."""
        with patch('app.services.dependency_container.get_settings', return_value=mock_settings):
            container = DependencyContainer({
                "ai_provider": "mock",
                "news_provider": "mock",
                "twitter_provider": "mock",
                "orchestration": "mock"
            })
            
            # Act
            ai_provider = container._create_mock_ai_provider()
            news_provider = container._create_mock_news_provider()
            twitter_provider = container._create_mock_twitter_provider()
            orchestration_service = container._create_mock_orchestration_service()
            
            # Assert
            assert isinstance(ai_provider, AIProviderPort)
            assert isinstance(news_provider, NewsProviderPort)
            assert isinstance(twitter_provider, TwitterProviderPort)
            assert isinstance(orchestration_service, OrchestrationServicePort) 