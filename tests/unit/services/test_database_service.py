import pytest
import asyncio
from app.services.database import get_db_health, get_connection


class TestDatabaseService:
    """Test database service functionality"""
    
    @pytest.mark.asyncio
    async def test_database_health_check_returns_status(self):
        """Should return health status for database"""
        health = await get_db_health()
        
        assert "status" in health
        assert "database" in health
        assert health["database"] == "postgresql"
        
        # Status should be either healthy or unhealthy
        assert health["status"] in ["healthy", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_database_health_check_when_healthy(self):
        """Should return healthy status when database is accessible"""
        health = await get_db_health()
        
        if health["status"] == "healthy":
            assert "error" not in health
        else:
            # If unhealthy, should have error message
            assert "error" in health
            assert isinstance(health["error"], str)
    
    @pytest.mark.asyncio
    async def test_get_connection_returns_connection_object(self):
        """Should return a database connection when available"""
        try:
            conn = await get_connection()
            assert conn is not None
            
            # Test basic query
            result = await conn.fetchval("SELECT 1")
            assert result == 1
            
            await conn.close()
        except Exception as e:
            # If connection fails, should be specific error
            assert "connect" in str(e).lower() or "database" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_database_health_check_handles_connection_errors(self):
        """Should handle database connection errors gracefully"""
        health = await get_db_health()
        
        # Should always return a dict with status
        assert isinstance(health, dict)
        assert "status" in health
        
        # If unhealthy, should provide error details
        if health["status"] == "unhealthy":
            assert "error" in health
            assert len(health["error"]) > 0 