"""
Frontend API - API endpoints for frontend operations.

This module provides REST API endpoints for frontend operations including
dashboard data, character interactions, and real-time events.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.services.dependency_container import get_container, DependencyContainer
from app.ports.frontend_port import (
    FrontendPort, DashboardOverview, CharacterStatus, ScenarioCreate,
    ScenarioResult, CustomNews, NewsInjectionResult, UserInteraction,
    CharacterResponse, FrontendEvent
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/frontend", tags=["frontend"])


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    session_id: str,
    container: DependencyContainer = Depends(get_container)
) -> DashboardOverview:
    """
    Get comprehensive dashboard overview.
    
    Args:
        session_id: User session ID
        container: Dependency container
        
    Returns:
        DashboardOverview: Complete dashboard data
    """
    try:
        frontend_service = container.get_frontend_service()
        return await frontend_service.get_dashboard_overview()
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/characters/status")
async def get_character_status(
    container: DependencyContainer = Depends(get_container)
) -> List[CharacterStatus]:
    """
    Get status of all AI characters.
    
    Args:
        container: Dependency container
        
    Returns:
        List[CharacterStatus]: List of all character statuses
    """
    try:
        frontend_service = container.get_frontend_service()
        return await frontend_service.get_character_status()
    except Exception as e:
        logger.error(f"Error getting character status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/create")
async def create_custom_scenario(
    scenario: ScenarioCreate,
    container: DependencyContainer = Depends(get_container)
) -> ScenarioResult:
    """
    Create and execute custom scenario.
    
    Args:
        scenario: Scenario configuration
        container: Dependency container
        
    Returns:
        ScenarioResult: Result of scenario execution
    """
    try:
        frontend_service = container.get_frontend_service()
        return await frontend_service.create_custom_scenario(scenario)
    except Exception as e:
        logger.error(f"Error creating custom scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news/inject")
async def inject_custom_news(
    news: CustomNews,
    container: DependencyContainer = Depends(get_container)
) -> NewsInjectionResult:
    """
    Inject custom news for testing.
    
    Args:
        news: Custom news to inject
        container: Dependency container
        
    Returns:
        NewsInjectionResult: Result of news injection
    """
    try:
        frontend_service = container.get_frontend_service()
        return await frontend_service.inject_custom_news(news)
    except Exception as e:
        logger.error(f"Error injecting custom news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/characters/interact")
async def interact_with_character(
    interaction: UserInteraction,
    container: DependencyContainer = Depends(get_container)
) -> CharacterResponse:
    """
    Allow users to interact directly with AI characters.
    
    Args:
        interaction: User interaction details
        container: Dependency container
        
    Returns:
        CharacterResponse: Character's response to the interaction
    """
    try:
        frontend_service = container.get_frontend_service()
        return await frontend_service.user_interact_with_character(interaction)
    except ValueError as e:
        logger.error(f"Invalid interaction: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in user interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/events/{session_id}")
async def websocket_events(
    websocket: WebSocket,
    session_id: str,
    container: DependencyContainer = Depends(get_container)
):
    """
    WebSocket endpoint for real-time events.
    
    Args:
        websocket: WebSocket connection
        session_id: User session ID
        container: Dependency container
    """
    await websocket.accept()
    
    try:
        event_bus = container.get_frontend_event_bus()
        
        # Send connection confirmation
        await websocket.send_text(
            FrontendEvent(
                event_type="websocket_connected",
                timestamp=FrontendEvent.__fields__["timestamp"].type_(),
                data={"session_id": session_id, "message": "Connected to event stream"},
                source="frontend_api"
            ).json()
        )
        
        # Subscribe to events and forward them to WebSocket
        async for event in event_bus.subscribe_to_events(session_id):
            try:
                await websocket.send_text(event.json())
            except Exception as e:
                logger.error(f"Error sending event to WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection for session {session_id}: {e}")
        try:
            await websocket.close()
        except:
            pass


@router.get("/health")
async def frontend_health_check(
    container: DependencyContainer = Depends(get_container)
) -> Dict[str, Any]:
    """
    Health check for frontend services.
    
    Args:
        container: Dependency container
        
    Returns:
        Dict[str, Any]: Health status of frontend services
    """
    try:
        frontend_service = container.get_frontend_service()
        event_bus = container.get_frontend_event_bus()
        
        # Basic health checks
        health_status = {
            "frontend_service": "healthy",
            "event_bus": "healthy",
            "timestamp": FrontendEvent.__fields__["timestamp"].type_().isoformat()
        }
        
        # Check event bus health
        try:
            event_bus_healthy = await event_bus.health_check()
            health_status["event_bus"] = "healthy" if event_bus_healthy else "degraded"
        except Exception as e:
            logger.error(f"Event bus health check failed: {e}")
            health_status["event_bus"] = "down"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Frontend health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/create")
async def create_session(
    user_id: str = None,
    container: DependencyContainer = Depends(get_container)
) -> Dict[str, Any]:
    """
    Create a new user session.
    
    Args:
        user_id: Optional user ID for authenticated sessions
        container: Dependency container
        
    Returns:
        Dict[str, Any]: Session information
    """
    try:
        session_manager = container.get_user_session_manager()
        session = await session_manager.create_session(user_id)
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "permissions": session.permissions,
            "created_at": session.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    container: DependencyContainer = Depends(get_container)
) -> Dict[str, Any]:
    """
    Get session information.
    
    Args:
        session_id: Session ID to retrieve
        container: Dependency container
        
    Returns:
        Dict[str, Any]: Session information
    """
    try:
        session_manager = container.get_user_session_manager()
        session = await session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "permissions": session.permissions,
            "preferences": session.preferences,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def invalidate_session(
    session_id: str,
    container: DependencyContainer = Depends(get_container)
) -> Dict[str, str]:
    """
    Invalidate a session.
    
    Args:
        session_id: Session ID to invalidate
        container: Dependency container
        
    Returns:
        Dict[str, str]: Success message
    """
    try:
        session_manager = container.get_user_session_manager()
        success = await session_manager.invalidate_session(session_id)
        
        if success:
            return {"message": f"Session {session_id} invalidated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error invalidating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 