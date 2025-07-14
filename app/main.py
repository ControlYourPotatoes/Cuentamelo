from fastapi import FastAPI
from app.config import settings
from app.api import health, news, demo, webhooks

app = FastAPI(
    title="Cuentamelo",
    description="LangGraph-powered AI character orchestration for social media",
    version="1.0.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(news.router, prefix="/news", tags=["news"])
app.include_router(demo.router, prefix="/demo", tags=["N8N Demo"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {
        "message": "Cuentamelo - AI Character Twitter Platform",
        "status": "running",
        "version": "1.0.0",
        "description": "Puerto Rican AI characters engaging with local news",
        "features": [
            "LangGraph agent orchestration",
            "Puerto Rican character personalities",
            "Twitter integration",
            "N8N visual demonstration layer"
        ]
    }

@app.get("/info")
async def app_info():
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "default_language": settings.default_language,
        "posting_rate_limit": settings.posting_rate_limit,
        "max_conversation_turns": settings.max_conversation_turns,
        "n8n_integration": {
            "demo_mode_enabled": settings.DEMO_MODE_ENABLED,
            "n8n_webhook_url": settings.N8N_WEBHOOK_URL,
            "demo_session_id": settings.DEMO_SESSION_ID
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 