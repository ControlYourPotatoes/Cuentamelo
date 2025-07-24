import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test FastAPI endpoint functionality"""
    
    def test_root_endpoint_returns_app_info(self):
        """Should return application information at root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "status" in data
        assert "version" in data
        assert data["status"] == "running"
        assert "Cuentamelo" in data["message"]
    
    def test_info_endpoint_returns_configuration(self):
        """Should return app configuration details"""
        response = client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["app_name"] == "Cuentamelo"
        assert data["default_language"] == "es-pr"
        assert data["posting_rate_limit"] > 0
        assert data["max_conversation_turns"] > 0
        assert isinstance(data["debug"], bool)
    
    def test_basic_health_endpoint_responds(self):
        """Should return basic health status"""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "AI Character Platform"
    
    def test_detailed_health_endpoint_checks_services(self):
        """Should return detailed health status for all services"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
        assert "api" in data["services"]
        
        # API should always be healthy
        assert data["services"]["api"] == "healthy"
    
    def test_database_specific_health_endpoint(self):
        """Should return database-specific health status"""
        response = client.get("/health/db")
        
        # Should either be 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "healthy"
            assert data["database"] == "postgresql"
        else:
            # If 503, should have error details
            assert "detail" in data
    
    def test_redis_specific_health_endpoint(self):
        """Should return Redis-specific health status"""
        response = client.get("/health/redis")
        
        # Should either be 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "healthy"
            assert data["cache"] == "redis"
    
    def test_nonexistent_endpoint_returns_404(self):
        """Should return 404 for non-existent endpoints"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404 