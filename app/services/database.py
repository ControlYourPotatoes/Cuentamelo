import asyncpg
from app.config import settings

async def get_db_health():
    """Check database connectivity for health endpoints"""
    try:
        conn = await asyncpg.connect(settings.database_url)
        # Simple query to test connection
        await conn.execute("SELECT 1")
        await conn.close()
        return {"status": "healthy", "database": "postgresql"}
    except Exception as e:
        return {"status": "unhealthy", "database": "postgresql", "error": str(e)}

async def get_connection():
    """Get a database connection for general use"""
    return await asyncpg.connect(settings.database_url) 