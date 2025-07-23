from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api import health, news, demo, webhooks, dashboard, frontend, command_api, character_analysis
from app.services.demo_orchestrator import demo_orchestrator
from app.services.n8n_integration import n8n_service

app = FastAPI(
    title="Cuentamelo",
    description="LangGraph-powered AI character orchestration for social media",
    version="1.0.0"
)

# Mount static files for dashboard
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(news.router, prefix="/news", tags=["news"])
app.include_router(demo.router, tags=["N8N Demo"])  # demo router already has /demo prefix
app.include_router(webhooks.router, tags=["Webhooks"])  # webhooks router already has /webhooks prefix
app.include_router(dashboard.router, tags=["Dashboard"])  # dashboard router already has /api/dashboard prefix
app.include_router(frontend.router, tags=["Frontend"])  # frontend router already has /api/frontend prefix
app.include_router(command_api.router, tags=["Commands"])  # command_api router already has /api/commands prefix
app.include_router(character_analysis.router, prefix="/api", tags=["Character Analysis"])

# Direct route for N8N workflow compatibility
@app.post("/api/demo/start")
async def api_demo_start(background_tasks: BackgroundTasks):
    """
    Direct endpoint for N8N workflow - called by N8N workflow
    
    This is the endpoint that the N8N workflow calls to trigger a demo
    """
    try:
        # Start a default demo scenario (political announcement)
        scenario_id = "political_announcement"
        
        # Validate scenario exists
        if not demo_orchestrator.get_scenario_info(scenario_id):
            return {
                "status": "error",
                "message": f"Default scenario {scenario_id} not found"
            }

        # Start demo scenario in background
        background_tasks.add_task(
            demo_orchestrator.run_scenario,
            scenario_id,
            1.0  # Default speed
        )

        # Immediately notify N8N that demo is starting
        await n8n_service.emit_event("demo_started", {
            "scenario_id": scenario_id,
            "scenario_title": demo_orchestrator.get_scenario_title(scenario_id),
            "expected_duration": demo_orchestrator.get_estimated_duration(scenario_id),
            "speed_multiplier": 1.0,
            "triggered_by": "n8n_workflow"
        })

        return {
            "status": "success",
            "message": f"Demo scenario '{scenario_id}' started via N8N workflow",
            "scenario": demo_orchestrator.get_scenario_info(scenario_id),
            "speed_multiplier": 1.0,
            "estimated_duration": demo_orchestrator.get_estimated_duration(scenario_id)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

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