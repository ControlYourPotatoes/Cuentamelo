"""
Tests for News API endpoints.

This module tests all news API endpoints including news discovery,
injection, processing, and trending topics.
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation import NewsItem
from app.services.dependency_container import DependencyContainer

client = TestClient(app)


class TestNewsAPIEndpoints:
    """Test News API endpoint functionality"""
    
    @pytest.fixture
    def mock_news_provider(self):
        """Mock news provider for testing."""
        provider = AsyncMock()
        provider.discover_latest_news = AsyncMock()
        provider.get_trending_topics = AsyncMock()
        provider.search_news = AsyncMock()
        provider.get_news_by_category = AsyncMock()
        provider.health_check = AsyncMock(return_value=True)
        return provider
    
    @pytest.fixture
    def mock_container(self, mock_news_provider):
        """Mock dependency container with news provider."""
        container = MagicMock()
        container.get_news_provider.return_value = mock_news_provider
        return container
    
    @pytest.fixture
    def sample_news_items(self):
        """Sample news items for testing."""
        return [
            NewsItem(
                id="news_001",
                headline="Breaking: New Puerto Rican Music Festival Announced",
                content="A major music festival featuring local and international artists will take place in San Juan next month.",
                topics=["music", "entertainment", "culture", "tourism", "san juan"],
                source="Puerto Rico Daily News",
                published_at=datetime.now(timezone.utc),
                relevance_score=0.8
            ),
            NewsItem(
                id="news_002",
                headline="Traffic Chaos in Bayamón: Major Construction Project Delays Commuters",
                content="Ongoing construction on Highway 22 in Bayamón is causing significant delays for morning commuters.",
                topics=["traffic", "construction", "bayamón", "transportation", "daily life"],
                source="El Nuevo Día",
                published_at=datetime.now(timezone.utc),
                relevance_score=0.6
            ),
            NewsItem(
                id="news_003",
                headline="Cultural Heritage: Restoration of Historic Buildings in Old San Juan",
                content="The government has announced funding for the restoration of several historic buildings in Old San Juan.",
                topics=["culture", "history", "old san juan", "heritage", "restoration"],
                source="Caribbean Business",
                published_at=datetime.now(timezone.utc),
                relevance_score=0.7
            )
        ]
    
    @pytest.fixture
    def sample_trending_topics(self):
        """Sample trending topics for testing."""
        return [
            {"topic": "music festival", "count": 15, "trend": "rising"},
            {"topic": "traffic bayamón", "count": 12, "trend": "stable"},
            {"topic": "old san juan", "count": 8, "trend": "rising"},
            {"topic": "puerto rico tourism", "count": 6, "trend": "falling"}
        ]
    
    @patch('app.api.news.get_container')
    def test_discover_latest_news_success(self, mock_get_container, mock_container,
                                         mock_news_provider, sample_news_items):
        """Should successfully discover latest news."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.discover_latest_news.return_value = sample_news_items
        
        # Execute
        response = client.get("/news/discover")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["headline"] == "Breaking: New Puerto Rican Music Festival Announced"
        assert data[0]["relevance_score"] == 0.8
        assert data[1]["headline"] == "Traffic Chaos in Bayamón: Major Construction Project Delays Commuters"
        assert data[2]["headline"] == "Cultural Heritage: Restoration of Historic Buildings in Old San Juan"
        mock_news_provider.discover_latest_news.assert_called_once()
    
    @patch('app.api.news.get_container')
    def test_discover_latest_news_error(self, mock_get_container, mock_container,
                                       mock_news_provider):
        """Should handle news discovery errors."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.discover_latest_news.side_effect = Exception("News discovery failed")
        
        # Execute
        response = client.get("/news/discover")
        
        # Assert
        assert response.status_code == 500
        assert "News discovery failed" in response.json()["detail"]
    
    @patch('app.api.news.get_container')
    def test_get_trending_topics_success(self, mock_get_container, mock_container,
                                        mock_news_provider, sample_trending_topics):
        """Should successfully get trending topics."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_trending_topics.return_value = sample_trending_topics
        
        # Execute
        response = client.get("/news/trending")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["topic"] == "music festival"
        assert data[0]["count"] == 15
        assert data[0]["trend"] == "rising"
        assert data[1]["topic"] == "traffic bayamón"
        assert data[1]["trend"] == "stable"
        mock_news_provider.get_trending_topics.assert_called_once()
    
    @patch('app.api.news.get_container')
    def test_search_news_success(self, mock_get_container, mock_container,
                                mock_news_provider, sample_news_items):
        """Should successfully search for news."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.search_news.return_value = sample_news_items[:2]  # Return first 2 items
        
        # Execute
        response = client.get("/news/search?query=music festival&limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["headline"] == "Breaking: New Puerto Rican Music Festival Announced"
        mock_news_provider.search_news.assert_called_once_with("music festival", 10)
    
    @patch('app.api.news.get_container')
    def test_search_news_without_limit(self, mock_get_container, mock_container,
                                      mock_news_provider, sample_news_items):
        """Should search news with default limit."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.search_news.return_value = sample_news_items
        
        # Execute
        response = client.get("/news/search?query=traffic")
        
        # Assert
        assert response.status_code == 200
        mock_news_provider.search_news.assert_called_once_with("traffic", 20)  # Default limit
    
    @patch('app.api.news.get_container')
    def test_get_news_by_category_success(self, mock_get_container, mock_container,
                                         mock_news_provider, sample_news_items):
        """Should successfully get news by category."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_news_by_category.return_value = sample_news_items[:1]  # Return first item
        
        # Execute
        response = client.get("/news/category/entertainment?limit=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["headline"] == "Breaking: New Puerto Rican Music Festival Announced"
        mock_news_provider.get_news_by_category.assert_called_once_with("entertainment", 5)
    
    @patch('app.api.news.get_container')
    def test_get_news_by_category_default_limit(self, mock_get_container, mock_container,
                                                mock_news_provider, sample_news_items):
        """Should get news by category with default limit."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_news_by_category.return_value = sample_news_items
        
        # Execute
        response = client.get("/news/category/politics")
        
        # Assert
        assert response.status_code == 200
        mock_news_provider.get_news_by_category.assert_called_once_with("politics", 20)  # Default limit
    
    @patch('app.api.news.get_container')
    def test_inject_custom_news_success(self, mock_get_container, mock_container):
        """Should successfully inject custom news."""
        # Setup
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.post("/news/inject", json={
            "title": "Custom Test News",
            "content": "This is a custom news item for testing",
            "source": "Test Source",
            "category": "test",
            "priority": 1
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "news_id" in data
        assert data["message"] == "News injected successfully"
    
    @patch('app.api.news.get_container')
    def test_inject_custom_news_invalid_data(self, mock_get_container, mock_container):
        """Should handle invalid custom news data."""
        # Setup
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.post("/news/inject", json={
            "title": "Test",  # Missing required fields
        })
        
        # Assert
        assert response.status_code == 422
    
    @patch('app.api.news.get_container')
    def test_get_news_health_success(self, mock_get_container, mock_container,
                                    mock_news_provider):
        """Should successfully get news service health."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.health_check.return_value = True
        
        # Execute
        response = client.get("/news/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "news"
        mock_news_provider.health_check.assert_called_once()
    
    @patch('app.api.news.get_container')
    def test_get_news_health_unhealthy(self, mock_get_container, mock_container,
                                      mock_news_provider):
        """Should handle unhealthy news service."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.health_check.return_value = False
        
        # Execute
        response = client.get("/news/health")
        
        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["service"] == "news"
    
    @patch('app.api.news.get_container')
    def test_get_news_health_error(self, mock_get_container, mock_container,
                                  mock_news_provider):
        """Should handle news health check errors."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.health_check.side_effect = Exception("Health check failed")
        
        # Execute
        response = client.get("/news/health")
        
        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "Health check failed" in data["detail"]


class TestNewsAPIValidation:
    """Test News API validation and error handling"""
    
    def test_search_news_missing_query(self):
        """Should handle missing search query."""
        response = client.get("/news/search")
        assert response.status_code == 422
    
    def test_search_news_invalid_limit(self):
        """Should handle invalid search limit."""
        response = client.get("/news/search?query=test&limit=invalid")
        assert response.status_code == 422
    
    def test_get_news_by_category_missing_category(self):
        """Should handle missing category parameter."""
        response = client.get("/news/category/")
        assert response.status_code == 404
    
    def test_get_news_by_category_invalid_limit(self):
        """Should handle invalid category limit."""
        response = client.get("/news/category/politics?limit=invalid")
        assert response.status_code == 422
    
    def test_inject_news_invalid_json(self):
        """Should handle invalid JSON in news injection."""
        response = client.post("/news/inject", data="invalid json")
        assert response.status_code == 422
    
    def test_inject_news_missing_required_fields(self):
        """Should handle missing required fields in news injection."""
        response = client.post("/news/inject", json={"title": "Test"})
        assert response.status_code == 422


class TestNewsAPIEdgeCases:
    """Test News API edge cases and boundary conditions"""
    
    @patch('app.api.news.get_container')
    def test_discover_latest_news_empty_result(self, mock_get_container, mock_container,
                                              mock_news_provider):
        """Should handle empty news discovery results."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.discover_latest_news.return_value = []
        
        # Execute
        response = client.get("/news/discover")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('app.api.news.get_container')
    def test_get_trending_topics_empty_result(self, mock_get_container, mock_container,
                                             mock_news_provider):
        """Should handle empty trending topics results."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_trending_topics.return_value = []
        
        # Execute
        response = client.get("/news/trending")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('app.api.news.get_container')
    def test_search_news_no_results(self, mock_get_container, mock_container,
                                   mock_news_provider):
        """Should handle search with no results."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.search_news.return_value = []
        
        # Execute
        response = client.get("/news/search?query=nonexistent")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('app.api.news.get_container')
    def test_get_news_by_category_no_results(self, mock_get_container, mock_container,
                                            mock_news_provider):
        """Should handle category search with no results."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_news_by_category.return_value = []
        
        # Execute
        response = client.get("/news/category/nonexistent")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @patch('app.api.news.get_container')
    def test_search_news_large_limit(self, mock_get_container, mock_container,
                                    mock_news_provider, sample_news_items):
        """Should handle search with large limit."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.search_news.return_value = sample_news_items
        
        # Execute
        response = client.get("/news/search?query=test&limit=100")
        
        # Assert
        assert response.status_code == 200
        mock_news_provider.search_news.assert_called_once_with("test", 100)
    
    @patch('app.api.news.get_container')
    def test_get_news_by_category_large_limit(self, mock_get_container, mock_container,
                                              mock_news_provider, sample_news_items):
        """Should handle category search with large limit."""
        # Setup
        mock_get_container.return_value = mock_container
        mock_news_provider.get_news_by_category.return_value = sample_news_items
        
        # Execute
        response = client.get("/news/category/politics?limit=100")
        
        # Assert
        assert response.status_code == 200
        mock_news_provider.get_news_by_category.assert_called_once_with("politics", 100) 