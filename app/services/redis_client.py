import redis.asyncio as redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper for caching and state management.
    
    This provides a clean interface for Redis operations with proper
    connection management and error handling.
    """
    
    def __init__(self, redis_url: str = None):
        """
        Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL (defaults to settings)
        """
        self.redis_url = redis_url or settings.redis_url
        self._client = None
    
    async def _get_client(self):
        """Get Redis client, creating if necessary."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
        return self._client
    
    async def ping(self) -> bool:
        """
        Ping Redis server to check connectivity.
        
        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            client = await self._get_client()
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return False
    
    async def get(self, key: str) -> str:
        """
        Get value from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            Value as string, or None if not found
        """
        try:
            client = await self._get_client()
            value = await client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            if ttl:
                await client.setex(key, ttl, value)
            else:
                await client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis set failed for key {key}: {str(e)}")
            return False
    
    async def setex(self, key: str, ttl: int, value: str) -> bool:
        """
        Set value in Redis with expiration.
        
        Args:
            key: Redis key
            ttl: Time to live in seconds
            value: Value to store
            
        Returns:
            True if successful, False otherwise
        """
        return await self.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            client = await self._get_client()
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis exists failed for key {key}: {str(e)}")
            return False
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


# Legacy functions for backward compatibility
async def get_redis_health():
    """Check Redis connectivity for health endpoints"""
    try:
        client = RedisClient()
        healthy = await client.ping()
        await client.close()
        return {"status": "healthy" if healthy else "unhealthy", "cache": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "cache": "redis", "error": str(e)}

async def get_redis_client():
    """Get a Redis client for general use"""
    return RedisClient() 