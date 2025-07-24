from fastapi import APIRouter, HTTPException
from app.services.database import get_db_health
from app.services.redis_client import get_redis_health
import asyncio

router = APIRouter()

@router.get("/")
async def basic_health():
    return {"status": "healthy", "service": "AI Character Platform"}

@router.get("/detailed")
async def detailed_health():
    try:
        db_health = await get_db_health()
        redis_health = await get_redis_health()

        return {
            "status": "healthy",
            "services": {
                "database": db_health,
                "redis": redis_health,
                "api": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/db")
async def database_health():
    """Specific database health check"""
    db_health = await get_db_health()
    if db_health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=db_health)
    return db_health

@router.get("/redis")
async def redis_health():
    """Specific Redis health check"""
    redis_health = await get_redis_health()
    if redis_health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=redis_health)
    return redis_health 