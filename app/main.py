from fastapi import FastAPI
from app.config import settings
from app.api import health

app = FastAPI(
    title="Cuentamelo",
    description="LangGraph-powered AI character orchestration for social media",
    version="1.0.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Cuentamelo - AI Character Twitter Platform",
        "status": "running",
        "version": "1.0.0",
        "description": "Puerto Rican AI characters engaging with local news"
    }

@app.get("/info")
async def app_info():
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "default_language": settings.default_language,
        "posting_rate_limit": settings.posting_rate_limit,
        "max_conversation_turns": settings.max_conversation_turns
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 