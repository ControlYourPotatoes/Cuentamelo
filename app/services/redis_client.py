import redis.asyncio as redis
from app.config import settings

async def get_redis_health():
    """Check Redis connectivity for health endpoints"""
    try:
        # Parse Redis URL to extract password
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        return {"status": "healthy", "cache": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "cache": "redis", "error": str(e)}

async def get_redis_client():
    """Get a Redis client for general use"""
    return redis.from_url(settings.redis_url) 