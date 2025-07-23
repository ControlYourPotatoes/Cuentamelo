"""
Tests for Character Analysis Controller endpoints.

This module tests all character analysis API endpoints including character listing,
scenario management, engagement analysis, and real-time streaming.
"""

import pytest
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.models.conversation import NewsItem
from app.services.dependency_container import DependencyContainer

client = TestClient(app)


class TestCharacterAnalysisController:
    """Test Character Analysis Controller endpoint functionality"""
    
    @pytest.fixture
    def mock_personality_loader(self):
        """Mock personality config loader for testing."""
        loader = MagicMock()
        loader.load_all_personalities.return_value = {
            "jovani_vazquez": {
                "character_id": "jovani_vazquez",
                "character_name": "Jovani Vázquez",
                "character_type": "influencer",
                "description": "Energetic Puerto Rican content creator and musician",
                "topics_of_interest": ["music", "daily_life", "family", "puerto_rico"],
                "base_energy": 0.9
            },
            "ciudadano_bayamon": {
                "character_id": "ciudadano_bayamon",
                "character_name": "Miguel Rivera",
                "character_type": "citizen",
                "description": "Working-class bayamonés, passionate Vaqueros fan",
                "topics_of_interest": ["vaqueros_basketball", "sports", "work_life", "family"],
                "base_energy": 0.7
            }
        }
        loader.get_available_characters.return_value = ["jovani_vazquez", "ciudadano_bayamon"]
        return loader
    
    @pytest.fixture
    def mock_character_analysis_service(self):
        """Mock character analysis service for testing."""
        service = AsyncMock()
        service.analyze_engagement = AsyncMock()
        service.create_analysis_session = AsyncMock()
        service.get_analysis_stream = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_news_scenario_service(self):
        """Mock news scenario service for testing."""
        service = AsyncMock()
        service.get_scenarios = AsyncMock()
        service.process_custom_news = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_scenarios(self):
        """Sample news scenarios for testing."""
        return [
            {
                "scenario_id": "vaqueros_championship",
                "title": "Vaqueros Win BSN Championship",
                "content": "Los Vaqueros de Bayamón conquistaron su campeonato número 17...",
                "category": "sports",
                "relevance_score": 0.95,
                "expected_engagement": {
                    "jovani_vazquez": 0.7,
                    "ciudadano_bayamon": 0.95
                }
            },
            {
                "scenario_id": "bad_bunny_concert",
                "title": "Bad Bunny Announces Surprise Concert in San Juan",
                "content": "Puerto Rican superstar Bad Bunny announced...",
                "category": "entertainment",
                "relevance_score": 0.9,
                "expected_engagement": {
                    "jovani_vazquez": 0.95,
                    "ciudadano_bayamon": 0.3
                }
            }
        ]
    
    @pytest.fixture
    def sample_engagement_analysis(self):
        """Sample engagement analysis results for testing."""
        return {
            "analysis_id": "test-analysis-123",
            "news_summary": {
                "title": "Bad Bunny Announces Surprise Concert in San Juan",
                "detected_topics": ["music", "puerto_rico", "entertainment"],
                "sentiment": "positive",
                "cultural_relevance": 0.9
            },
            "character_analyses": [
                {
                    "character_id": "jovani_vazquez",
                    "character_name": "Jovani Vázquez",
                    "engagement_decision": "engage",
                    "engagement_score": 0.85,
                    "reasoning": "High relevance to music and Puerto Rico topics, matches energetic personality",
                    "topic_matches": [
                        {"topic": "music", "weight": 0.9, "matched": True},
                        {"topic": "puerto_rico", "weight": 0.9, "matched": True}
                    ],
                    "predicted_response_tone": "enthusiastic_performative",
                    "confidence": 0.92
                },
                {
                    "character_id": "ciudadano_bayamon",
                    "character_name": "Miguel Rivera",
                    "engagement_decision": "ignore",
                    "engagement_score": 0.25,
                    "reasoning": "Low relevance to sports and work topics, doesn't match interests",
                    "topic_matches": [
                        {"topic": "music", "weight": 0.3, "matched": True},
                        {"topic": "entertainment", "weight": 0.4, "matched": True}
                    ],
                    "predicted_response_tone": None,
                    "confidence": 0.78
                }
            ]
        }
    
    @pytest.fixture
    def sample_custom_news_response(self):
        """Sample custom news processing response for testing."""
        return {
            "news_id": "custom_uuid_123",
            "formatted_content": {
                "title": "Custom news headline",
                "content": "Full news article content...",
                "detected_topics": ["local_politics", "community"],
                "sentiment": "neutral",
                "cultural_relevance": 0.6,
                "processing_metadata": {
                    "word_count": 150,
                    "reading_time": "1 min",
                    "language": "es-pr"
                }
            }
        }

    # GET /api/characters endpoint tests
    
    @patch('app.api.character_analysis.get_container')
    def test_get_characters_success(self, mock_get_container, mock_personality_loader):
        """Should successfully return list of available characters."""
        # Setup
        mock_container = MagicMock()
        mock_container.get_personality_config_loader.return_value = mock_personality_loader
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/characters")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert len(data["characters"]) == 2
        
        # Check first character
        jovani = data["characters"][0]
        assert jovani["character_id"] == "jovani_vazquez"
        assert jovani["character_name"] == "Jovani Vázquez"
        assert jovani["character_type"] == "influencer"
        assert "music" in jovani["topics_of_interest"]
        
        # Check second character
        miguel = data["characters"][1]
        assert miguel["character_id"] == "ciudadano_bayamon"
        assert miguel["character_name"] == "Miguel Rivera"
        assert miguel["character_type"] == "citizen"
        assert "vaqueros_basketball" in miguel["topics_of_interest"]
    
    @patch('app.api.character_analysis.get_container')
    def test_get_characters_with_details(self, mock_get_container, mock_personality_loader):
        """Should return characters with detailed information when include_details=true."""
        # Setup
        mock_container = MagicMock()
        mock_container.get_personality_config_loader.return_value = mock_personality_loader
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/characters?include_details=true")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert len(data["characters"]) == 2
        
        # Check that detailed fields are included
        jovani = data["characters"][0]
        assert "base_energy" in jovani
        assert jovani["base_energy"] == 0.9
    
    @patch('app.api.character_analysis.get_container')
    def test_get_characters_service_error(self, mock_get_container, mock_personality_loader):
        """Should return 500 error when character loading fails."""
        # Setup
        mock_container = MagicMock()
        mock_personality_loader.load_all_personalities.side_effect = Exception("Database error")
        mock_container.get_personality_config_loader.return_value = mock_personality_loader
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/characters")
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

    # GET /api/scenarios endpoint tests
    
    @patch('app.api.character_analysis.get_container')
    def test_get_scenarios_success(self, mock_get_container, mock_news_scenario_service, sample_scenarios):
        """Should successfully return list of available scenarios."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.get_scenarios.return_value = sample_scenarios
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/scenarios")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 2
        
        # Check first scenario
        vaqueros = data["scenarios"][0]
        assert vaqueros["scenario_id"] == "vaqueros_championship"
        assert vaqueros["title"] == "Vaqueros Win BSN Championship"
        assert vaqueros["category"] == "sports"
        assert vaqueros["relevance_score"] == 0.95
    
    @patch('app.api.character_analysis.get_container')
    def test_get_scenarios_with_category_filter(self, mock_get_container, mock_news_scenario_service, sample_scenarios):
        """Should return scenarios filtered by category."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.get_scenarios.return_value = [sample_scenarios[0]]  # Only sports
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/scenarios?category=sports")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 1
        assert data["scenarios"][0]["category"] == "sports"
    
    @patch('app.api.character_analysis.get_container')
    def test_get_scenarios_service_error(self, mock_get_container, mock_news_scenario_service):
        """Should return 500 error when scenario loading fails."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.get_scenarios.side_effect = Exception("Service error")
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/scenarios")
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

    # POST /api/analyze-engagement endpoint tests
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_success(self, mock_get_container, mock_character_analysis_service, sample_engagement_analysis):
        """Should successfully analyze character engagement for given news content."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.analyze_engagement.return_value = sample_engagement_analysis
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        
        # Mock personality loader
        mock_personality_loader = MagicMock()
        mock_personality_loader.get_available_characters.return_value = ["jovani_vazquez", "ciudadano_bayamon"]
        mock_container.get_personality_config_loader.return_value = mock_personality_loader
        
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Bad Bunny Announces Surprise Concert in San Juan",
                "content": "Puerto Rican superstar Bad Bunny announced...",
                "source": "custom_input",
                "category": "entertainment"
            },
            "characters": ["jovani_vazquez", "ciudadano_bayamon"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"] == "test-analysis-123"
        assert "news_summary" in data
        assert "character_analyses" in data
        assert len(data["character_analyses"]) == 2
        
        # Check character analysis results
        jovani_analysis = data["character_analyses"][0]
        assert jovani_analysis["character_id"] == "jovani_vazquez"
        assert jovani_analysis["engagement_decision"] == "engage"
        assert jovani_analysis["engagement_score"] == 0.85
        assert "reasoning" in jovani_analysis
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_invalid_characters(self, mock_get_container, mock_character_analysis_service):
        """Should return 400 error for invalid character IDs."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.analyze_engagement.side_effect = ValueError("Invalid character ID")
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Test news",
                "content": "Test content",
                "source": "custom_input",
                "category": "test"
            },
            "characters": ["invalid_character"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_missing_required_fields(self, mock_get_container):
        """Should return 422 error for missing required fields."""
        # Setup
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Test news"
                # Missing content field
            },
            "characters": ["jovani_vazquez"]
            # Missing analysis_options
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_service_error(self, mock_get_container, mock_character_analysis_service):
        """Should return 500 error when analysis service fails."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.analyze_engagement.side_effect = Exception("Analysis failed")
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Test news",
                "content": "Test content",
                "source": "custom_input",
                "category": "test"
            },
            "characters": ["jovani_vazquez"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

    # GET /api/analyze-stream/{session_id} endpoint tests
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_stream_success(self, mock_get_container, mock_character_analysis_service):
        """Should successfully establish SSE stream for analysis updates."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.get_analysis_stream.return_value = [
            {"event": "analysis_started", "data": {"message": "Starting analysis"}},
            {"event": "character_analyzing", "data": {"character_id": "jovani_vazquez", "progress": 50}},
            {"event": "analysis_complete", "data": {"message": "Analysis complete"}}
        ]
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        session_id = "test-session-123"
        
        # Execute
        response = client.get(f"/api/analyze-stream/{session_id}")
        
        # Assert
        assert response.status_code == 200
        # Note: SSE responses are typically handled differently in tests
        # This is a basic check that the endpoint responds
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_stream_session_not_found(self, mock_get_container, mock_character_analysis_service):
        """Should return 404 error for non-existent session."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.get_analysis_stream.side_effect = ValueError("Session not found")
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        session_id = "non-existent-session"
        
        # Execute
        response = client.get(f"/api/analyze-stream/{session_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_stream_session_expired(self, mock_get_container, mock_character_analysis_service):
        """Should return 410 error for expired session."""
        # Setup
        mock_container = MagicMock()
        mock_character_analysis_service.get_analysis_stream.side_effect = ValueError("Session expired")
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        session_id = "expired-session"
        
        # Execute
        response = client.get(f"/api/analyze-stream/{session_id}")
        
        # Assert
        assert response.status_code == 410
        data = response.json()
        assert "detail" in data
        assert "expired" in data["detail"].lower()

    # POST /api/custom-news endpoint tests
    
    @patch('app.api.character_analysis.get_container')
    def test_custom_news_success(self, mock_get_container, mock_news_scenario_service, sample_custom_news_response):
        """Should successfully process custom news content."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.process_custom_news.return_value = sample_custom_news_response
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "title": "Custom news headline",
            "content": "Full news article content...",
            "source_url": "https://example.com/news",
            "category": "local_news"
        }
        
        # Execute
        response = client.post("/api/custom-news", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["news_id"] == "custom_uuid_123"
        assert "formatted_content" in data
        assert data["formatted_content"]["title"] == "Custom news headline"
        assert "detected_topics" in data["formatted_content"]
        assert "processing_metadata" in data["formatted_content"]
    
    @patch('app.api.character_analysis.get_container')
    def test_custom_news_invalid_content(self, mock_get_container, mock_news_scenario_service):
        """Should return 400 error for invalid news content."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.process_custom_news.side_effect = ValueError("Invalid content")
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "title": "",  # Empty title
            "content": "Very short content",  # Too short
            "category": "invalid_category"
        }
        
        # Execute
        response = client.post("/api/custom-news", json=request_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()
    
    @patch('app.api.character_analysis.get_container')
    def test_custom_news_missing_required_fields(self, mock_get_container):
        """Should return 422 error for missing required fields."""
        # Setup
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        
        request_data = {
            "title": "Test title"
            # Missing content field
        }
        
        # Execute
        response = client.post("/api/custom-news", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.character_analysis.get_container')
    def test_custom_news_processing_error(self, mock_get_container, mock_news_scenario_service):
        """Should return 422 error when content processing fails."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.process_custom_news.side_effect = Exception("Processing failed")
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "title": "Test news headline",
            "content": "Test news content with valid length for processing",
            "category": "local_news"
        }
        
        # Execute
        response = client.post("/api/custom-news", json=request_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "processing" in data["detail"].lower()


class TestCharacterAnalysisValidation:
    """Test input validation for character analysis endpoints"""
    
    def test_analyze_engagement_missing_news_content(self):
        """Should return 422 error when news_content is missing."""
        request_data = {
            "characters": ["jovani_vazquez"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        response = client.post("/api/analyze-engagement", json=request_data)
        assert response.status_code == 422
    
    def test_analyze_engagement_empty_characters_list(self):
        """Should return 422 error when characters list is empty."""
        request_data = {
            "news_content": {
                "title": "Test news",
                "content": "Test content",
                "source": "custom_input",
                "category": "test"
            },
            "characters": [],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        response = client.post("/api/analyze-engagement", json=request_data)
        assert response.status_code == 422
    
    def test_custom_news_empty_title(self):
        """Should return 422 error when title is empty."""
        request_data = {
            "title": "",
            "content": "Valid content with sufficient length for processing",
            "category": "local_news"
        }
        
        response = client.post("/api/custom-news", json=request_data)
        assert response.status_code == 422
    
    def test_custom_news_short_content(self):
        """Should return 422 error when content is too short."""
        request_data = {
            "title": "Valid title",
            "content": "Too short",
            "category": "local_news"
        }
        
        response = client.post("/api/custom-news", json=request_data)
        assert response.status_code == 422


class TestCharacterAnalysisEdgeCases:
    """Test edge cases for character analysis endpoints"""
    
    @patch('app.api.character_analysis.get_container')
    def test_get_characters_empty_result(self, mock_get_container, mock_personality_loader):
        """Should handle empty character list gracefully."""
        # Setup
        mock_container = MagicMock()
        mock_personality_loader.load_all_personalities.return_value = {}
        mock_container.get_personality_config_loader.return_value = mock_personality_loader
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/characters")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert len(data["characters"]) == 0
    
    @patch('app.api.character_analysis.get_container')
    def test_get_scenarios_empty_result(self, mock_get_container, mock_news_scenario_service):
        """Should handle empty scenario list gracefully."""
        # Setup
        mock_container = MagicMock()
        mock_news_scenario_service.get_scenarios.return_value = []
        mock_container.get_news_scenario_service.return_value = mock_news_scenario_service
        mock_get_container.return_value = mock_container
        
        # Execute
        response = client.get("/api/scenarios")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 0
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_single_character(self, mock_get_container, mock_character_analysis_service, sample_engagement_analysis):
        """Should handle analysis with single character."""
        # Setup
        mock_container = MagicMock()
        # Modify sample to have only one character
        single_analysis = sample_engagement_analysis.copy()
        single_analysis["character_analyses"] = [sample_engagement_analysis["character_analyses"][0]]
        mock_character_analysis_service.analyze_engagement.return_value = single_analysis
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Test news",
                "content": "Test content",
                "source": "custom_input",
                "category": "test"
            },
            "characters": ["jovani_vazquez"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["character_analyses"]) == 1
    
    @patch('app.api.character_analysis.get_container')
    def test_analyze_engagement_large_character_list(self, mock_get_container, mock_character_analysis_service, sample_engagement_analysis):
        """Should handle analysis with many characters."""
        # Setup
        mock_container = MagicMock()
        # Create analysis with many characters
        large_analysis = sample_engagement_analysis.copy()
        large_analysis["character_analyses"] = [
            sample_engagement_analysis["character_analyses"][0],
            sample_engagement_analysis["character_analyses"][1],
            # Add more characters
            {
                "character_id": "character_3",
                "character_name": "Character Three",
                "engagement_decision": "engage",
                "engagement_score": 0.6,
                "reasoning": "Moderate relevance",
                "topic_matches": [],
                "predicted_response_tone": "neutral",
                "confidence": 0.7
            }
        ]
        mock_character_analysis_service.analyze_engagement.return_value = large_analysis
        mock_container.get_character_analysis_service.return_value = mock_character_analysis_service
        mock_get_container.return_value = mock_container
        
        request_data = {
            "news_content": {
                "title": "Test news",
                "content": "Test content",
                "source": "custom_input",
                "category": "test"
            },
            "characters": ["jovani_vazquez", "ciudadano_bayamon", "character_3"],
            "analysis_options": {
                "include_reasoning": True,
                "include_topic_analysis": True,
                "generate_responses": False
            }
        }
        
        # Execute
        response = client.post("/api/analyze-engagement", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["character_analyses"]) == 3 