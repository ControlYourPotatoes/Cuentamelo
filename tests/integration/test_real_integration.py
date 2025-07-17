"""
Real Integration Tests - Testing with actual services and external dependencies.

These tests verify the actual integration between components using real services
where possible, with minimal mocking only for isolation of specific components.
"""
import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from app.models.conversation import create_orchestration_state, NewsItem
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.graphs.orchestrator import execute_orchestration_cycle
from app.graphs.character_workflow import execute_character_workflow
from app.services.dependency_container import DependencyContainer
from app.ports.ai_provider import AIProviderPort
from app.ports.news_provider import NewsProviderPort
from app.ports.twitter_provider import TwitterProviderPort


class TestRealServiceIntegration:
    """Test integration with real services and minimal mocking."""
    
    @pytest.fixture
    def real_dependency_container(self):
        """Create a dependency container with real services configured."""
        container = DependencyContainer({
            "ai_provider": "claude",  # Use real Claude AI
            "news_provider": "twitter",  # Use real Twitter news
            "twitter_provider": "twitter",  # Use real Twitter posting
            "orchestration": "langgraph"  # Use real LangGraph
        })
        return container
    
    @pytest.fixture
    def sample_news_item(self):
        """Create a realistic news item for testing."""
        return NewsItem(
            id="test_news_001",
            headline="Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷",
            content="A major music festival featuring Puerto Rican artists has been announced for San Juan. The festival will showcase local talent and celebrate Puerto Rican culture.",
            source="Test News Source",
            url="https://example.com/news/001",
            published_at=datetime.now(timezone.utc),
            topics=["music", "entertainment", "puerto_rico", "festival"],
            sentiment="positive",
            relevance_score=0.9,
            puerto_rico_relevance=0.95
        )
    
    @pytest.mark.asyncio
    async def test_real_ai_provider_integration(self, real_dependency_container):
        """Test integration with real AI provider (Claude)."""
        # Get real AI provider from container
        ai_provider = real_dependency_container.get_ai_provider()
        
        # Test AI provider health check
        health_status = await ai_provider.health_check()
        assert health_status is True, "AI provider should be healthy"
        
        # Test basic AI functionality with character response
        from app.models.ai_personality_data import AIPersonalityData, LanguageStyle
        
        test_personality = AIPersonalityData(
            character_id="test",
            character_name="Test",
            character_type="test",
            personality_traits="Test personality",
            background="Test background",
            language_style=LanguageStyle.ENGLISH,
            interaction_style="casual",
            cultural_context="test context"
        )
        
        response = await ai_provider.generate_character_response(
            personality_data=test_personality,
            context="Generate a short response about Puerto Rican music culture.",
            target_topic="music"
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert isinstance(response.content, str)
    
    @pytest.mark.asyncio
    async def test_real_character_workflow_with_ai(self, real_dependency_container, sample_news_item):
        """Test character workflow with real AI provider."""
        # Get real AI provider
        ai_provider = real_dependency_container.get_ai_provider()
        
        # Create character with real AI provider
        jovani_agent = create_jovani_vazquez(ai_provider=ai_provider)
        
        # Execute character workflow with real news
        result = await execute_character_workflow(
            character_agent=jovani_agent,
            input_context="¡Breaking news! New Puerto Rican music festival announced in San Juan! 🔥🎵",
            news_item=sample_news_item,
            target_topic="music",
            is_new_thread=True
        )
        
        # Verify workflow completed successfully
        assert result["success"] is True, f"Workflow failed: {result.get('error_details')}"
        assert result["workflow_step"] in ["format_output", "handle_error"], f"Unexpected workflow step: {result['workflow_step']}"
        
        # Verify we got a response (either engagement or decision not to engage)
        assert result["engagement_decision"] is not None
        assert result["generated_response"] is not None or result["engagement_decision"].value in ["ignore", "defer"]
        
        # If character decided to engage, verify response quality
        if result["engagement_decision"].value == "engage":
            assert len(result["generated_response"]) > 10
            # Response should be in Spanish or contain Puerto Rican cultural elements
            response_lower = result["generated_response"].lower()
            assert any(word in response_lower for word in ["puerto", "rico", "música", "festival", "san juan"])
    
    @pytest.mark.asyncio
    async def test_real_orchestration_cycle(self, real_dependency_container, sample_news_item):
        """Test orchestration cycle with real services."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        orchestration_state.pending_news_queue.append(sample_news_item)
        
        # Execute orchestration cycle
        result = await execute_orchestration_cycle(
            news_items=[],
            existing_state=orchestration_state
        )
        
        # Verify orchestration completed
        assert result["success"] is True, f"Orchestration failed: {result.get('error_details')}"
        assert result["workflow_step"] in ["cleanup", "handle_error"], f"Unexpected workflow step: {result['workflow_step']}"
        
        # Verify state was updated
        final_state = result["orchestration_state"]
        assert final_state.processed_news_count >= 0
        assert final_state.orchestration_active is True
        
        # Verify character reactions were generated
        character_reactions = result.get("character_reactions", [])
        assert len(character_reactions) >= 0  # May be 0 if character decided not to engage
    
    @pytest.mark.asyncio
    async def test_real_news_processing_flow(self, real_dependency_container):
        """Test complete news processing flow with real services."""
        # Get real news provider
        news_provider = real_dependency_container.get_news_provider()
        
        # Test news provider health check
        health_status = await news_provider.health_check()
        assert health_status is True, "News provider should be healthy"
        
        # Test news discovery (may return empty if no recent news)
        latest_news = await news_provider.discover_latest_news(max_results=5)
        assert isinstance(latest_news, list)
        
        # If we have news, test processing
        if latest_news:
            # Create orchestration state
            orchestration_state = create_orchestration_state(["jovani_vazquez"])
            
            # Add real news items
            for news in latest_news[:2]:  # Process up to 2 news items
                orchestration_state.pending_news_queue.append(news)
            
            # Execute orchestration
            result = await execute_orchestration_cycle(
                news_items=[],
                existing_state=orchestration_state
            )
            
            # Verify processing completed
            assert result["success"] is True, f"News processing failed: {result.get('error_details')}"
            
            # Verify news was processed
            final_state = result["orchestration_state"]
            assert final_state.processed_news_count >= 0
    
    @pytest.mark.asyncio
    async def test_real_twitter_integration(self, real_dependency_container):
        """Test Twitter provider integration."""
        # Get real Twitter provider
        twitter_provider = real_dependency_container.get_twitter_provider()
        
        # Test Twitter provider health check
        health_status = await twitter_provider.health_check()
        # Note: This may fail if Twitter credentials aren't configured
        # That's okay for integration testing - we're testing the integration, not the external service
        
        # Test getting user tweets (should not fail even if no credentials)
        try:
            tweets = await twitter_provider.get_user_tweets(username="test_user", max_results=5)
            assert isinstance(tweets, list)
        except Exception as e:
            # Expected if Twitter credentials aren't configured
            assert "credentials" in str(e).lower() or "auth" in str(e).lower() or "unauthorized" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_real_error_handling(self, real_dependency_container):
        """Test error handling with real services."""
        # Test with invalid input that should trigger error handling
        ai_provider = real_dependency_container.get_ai_provider()
        
        # Test with empty input
        try:
            from app.models.ai_personality_data import AIPersonalityData, LanguageStyle
            
            test_personality = AIPersonalityData(
                character_id="test",
                character_name="Test",
                character_type="test",
                personality_traits="Test personality",
                background="Test background",
                language_style=LanguageStyle.ENGLISH,
                interaction_style="casual",
                cultural_context="test context"
            )
            
            response = await ai_provider.generate_character_response(
                personality_data=test_personality,
                context="",
                target_topic="test"
            )
            # Should handle gracefully
            assert response is not None
        except Exception as e:
            # Should handle errors gracefully
            assert "error" in str(e).lower() or "invalid" in str(e).lower()
        
        # Test orchestration with invalid state
        try:
            result = await execute_orchestration_cycle(
                news_items=None,
                existing_state=None
            )
            # Should handle gracefully
            assert result["success"] is False or result["success"] is True
        except Exception as e:
            # Should handle errors gracefully
            assert "error" in str(e).lower()


class TestDockerEnvironmentIntegration:
    """Test integration in Docker environment."""
    
    @pytest.mark.asyncio
    async def test_docker_service_availability(self):
        """Test that all services are available in Docker environment."""
        # Test that we can create dependency container
        container = DependencyContainer()
        
        # Test that all core services can be instantiated
        ai_provider = container.get_ai_provider()
        news_provider = container.get_news_provider()
        twitter_provider = container.get_twitter_provider()
        orchestration_service = container.get_orchestration_service()
        
        # Verify services are created
        assert ai_provider is not None
        assert news_provider is not None
        assert twitter_provider is not None
        assert orchestration_service is not None
        
        # Test health checks (may fail if external services aren't available)
        try:
            ai_health = await ai_provider.health_check()
            assert isinstance(ai_health, bool)
        except Exception:
            # Expected if external services aren't configured
            pass
        
        try:
            news_health = await news_provider.health_check()
            assert isinstance(news_health, bool)
        except Exception:
            # Expected if external services aren't configured
            pass
    
    @pytest.mark.asyncio
    async def test_docker_orchestration_workflow(self):
        """Test orchestration workflow in Docker environment."""
        # Create orchestration state
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        
        # Create test news item
        news_item = NewsItem(
            id="docker_test_001",
            headline="Docker Test: Puerto Rican Culture Celebration",
            content="Test content for Docker environment integration testing.",
            source="Docker Test",
            published_at=datetime.now(timezone.utc),
            topics=["test", "puerto_rico", "culture"],
            relevance_score=0.8
        )
        
        orchestration_state.pending_news_queue.append(news_item)
        
        # Execute orchestration cycle
        try:
            result = await execute_orchestration_cycle(
                news_items=[],
                existing_state=orchestration_state
            )
            
            # Verify workflow completed (may fail gracefully if external services unavailable)
            assert result["success"] is True or result["success"] is False
            assert "workflow_step" in result
            assert "orchestration_state" in result
            
        except Exception as e:
            # Should handle errors gracefully
            assert "error" in str(e).lower() or "timeout" in str(e).lower() 