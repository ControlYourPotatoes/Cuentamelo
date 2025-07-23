from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import asyncio

from app.services.n8n_integration import n8n_service
from app.services.demo_orchestrator import demo_orchestrator
from app.agents.agent_factory import agent_factory
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Pydantic models for dashboard data
class SystemStatus(BaseModel):
    status: str
    uptime: float
    active_characters: int
    total_events: int
    last_event_time: Optional[datetime]
    demo_mode: bool

class CharacterStatus(BaseModel):
    id: str
    name: str
    status: str  # "active", "thinking", "responding", "idle"
    last_activity: Optional[datetime]
    engagement_count: int
    response_count: int
    personality_traits: List[str]

class DashboardOverview(BaseModel):
    system: SystemStatus
    characters: List[CharacterStatus]
    recent_events: List[Dict[str, Any]]
    active_scenarios: List[str]

class ScenarioCreate(BaseModel):
    name: str
    description: str
    news_content: str
    characters: List[str]
    speed_multiplier: float = 1.0

class CustomNews(BaseModel):
    title: str
    content: str
    source: str = "custom"
    topics: List[str] = []
    urgency_score: float = 0.5

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview():
    """Get comprehensive dashboard overview"""
    try:
        # Get system status
        n8n_status = n8n_service.get_status()
        
        system_status = SystemStatus(
            status="healthy" if n8n_status["session_active"] else "degraded",
            uptime=0.0,  # TODO: Implement uptime tracking
            active_characters=len(agent_factory.get_active_agents()),
            total_events=n8n_status["total_events_sent"],
            last_event_time=datetime.fromisoformat(n8n_status["last_event_time"]) if n8n_status["last_event_time"] else None,
            demo_mode=settings.DEMO_MODE_ENABLED
        )
        
        # Get character statuses
        characters = []
        for agent_id, agent in agent_factory.get_all_agents().items():
            character_status = CharacterStatus(
                id=agent_id,
                name=agent.name if hasattr(agent, 'name') else agent_id,
                status="active",  # TODO: Implement real status tracking
                last_activity=datetime.now(timezone.utc),
                engagement_count=0,  # TODO: Track from database
                response_count=0,    # TODO: Track from database
                personality_traits=agent.personality_traits if hasattr(agent, 'personality_traits') else []
            )
            characters.append(character_status)
        
        # Get recent events (last 10)
        recent_events = []  # TODO: Implement event history tracking
        
        # Get active scenarios
        active_scenarios = demo_orchestrator.get_active_scenarios() if hasattr(demo_orchestrator, 'get_active_scenarios') else []
        
        return DashboardOverview(
            system=system_status,
            characters=characters,
            recent_events=recent_events,
            active_scenarios=active_scenarios,
            analytics=AnalyticsSummary()  # TODO: Replace with real analytics summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

@router.get("/characters/status", response_model=List[CharacterStatus])
async def get_characters_status():
    """Get status of all AI characters"""
    try:
        characters = []
        for agent_id, agent in agent_factory.get_all_agents().items():
            character_status = CharacterStatus(
                id=agent_id,
                name=agent.name if hasattr(agent, 'name') else agent_id,
                status="active",
                last_activity=datetime.now(timezone.utc),
                engagement_count=0,
                response_count=0,
                personality_traits=agent.personality_traits if hasattr(agent, 'personality_traits') else []
            )
            characters.append(character_status)
        
        return characters
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get character status: {str(e)}")

@router.put("/characters/{character_id}/config")
async def update_character_config(character_id: str, config: Dict[str, Any]):
    """Update character configuration"""
    try:
        agent = agent_factory.get_agent(character_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        
        # Update character configuration
        # TODO: Implement character configuration update logic
        
        # Emit event for n8n visualization
        await n8n_service.emit_event("character_updated", {
            "character_id": character_id,
            "config": config,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {"message": f"Character {character_id} configuration updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character config: {str(e)}")

@router.post("/scenarios/custom")
async def create_custom_scenario(scenario: ScenarioCreate):
    """Create and execute a custom scenario"""
    try:
        # Create custom scenario
        scenario_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # TODO: Implement scenario creation logic
        # This would involve:
        # 1. Creating a custom news item
        # 2. Setting up character participation
        # 3. Configuring execution speed
        # 4. Starting the scenario
        
        # Emit event for n8n visualization
        await n8n_service.emit_event("custom_scenario_created", {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "characters": scenario.characters,
            "speed_multiplier": scenario.speed_multiplier,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "scenario_id": scenario_id,
            "message": "Custom scenario created and started",
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create custom scenario: {str(e)}")

@router.post("/news/inject")
async def inject_custom_news(news: CustomNews):
    """Inject custom news for testing"""
    try:
        # TODO: Implement custom news injection
        # This would involve:
        # 1. Adding the news to the discovery queue
        # 2. Triggering the news processing workflow
        # 3. Notifying relevant characters
        
        # Emit event for n8n visualization
        await n8n_service.emit_event("custom_news_injected", {
            "title": news.title,
            "content": news.content,
            "source": news.source,
            "topics": news.topics,
            "urgency_score": news.urgency_score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "message": "Custom news injected successfully",
            "news_id": f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inject custom news: {str(e)}")

@router.get("/analytics/metrics")
async def get_analytics_metrics():
    """Get analytics metrics for dashboard"""
    try:
        # TODO: Implement real analytics collection
        # This would involve:
        # 1. Character engagement metrics
        # 2. Response quality analysis
        # 3. Cultural relevance tracking
        # 4. Performance monitoring
        
        metrics = {
            "engagement_data": {
                "total_engagements": 0,
                "engagement_rate": 0.0,
                "top_characters": [],
                "engagement_trend": []
            },
            "performance_data": {
                "avg_response_time": 0.0,
                "success_rate": 0.0,
                "error_rate": 0.0,
                "performance_trend": []
            },
            "cultural_data": {
                "cultural_elements_used": [],
                "language_distribution": {},
                "cultural_relevance_score": 0.0
            }
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics metrics: {str(e)}")

@router.post("/user/interact")
async def user_interact_with_character(character_id: str, message: str, context: Optional[str] = None):
    """Allow users to interact directly with AI characters"""
    try:
        agent = agent_factory.get_agent(character_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
        
        # TODO: Implement direct character interaction
        # This would involve:
        # 1. Processing the user message
        # 2. Generating character response
        # 3. Maintaining conversation context
        
        # Emit event for n8n visualization
        await n8n_service.emit_event("user_interaction", {
            "character_id": character_id,
            "user_message": message,
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Mock response for now
        response = f"Character {character_id} received your message: '{message}'"
        
        return {
            "character_id": character_id,
            "user_message": message,
            "character_response": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to interact with character: {str(e)}")

@router.get("/scenarios/templates")
async def get_scenario_templates():
    """Get available scenario templates"""
    try:
        # TODO: Implement scenario template system
        templates = [
            {
                "id": "political_announcement",
                "name": "Political Announcement",
                "description": "Gobernador anuncia nueva inversión en infraestructura",
                "characters": ["political_figure", "ciudadano_boricua", "jovani_vazquez"],
                "estimated_duration": 300  # seconds
            },
            {
                "id": "cultural_festival",
                "name": "Cultural Festival",
                "description": "Festival de música puertorriqueña atrae miles de visitantes",
                "characters": ["jovani_vazquez", "cultural_historian", "ciudadano_boricua"],
                "estimated_duration": 240
            },
            {
                "id": "economic_development",
                "name": "Economic Development",
                "description": "Nuevo hub tecnológico se inaugura en San Juan",
                "characters": ["jovani_vazquez", "political_figure"],
                "estimated_duration": 180
            }
        ]
        
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scenario templates: {str(e)}") 