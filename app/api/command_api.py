"""
Command API - REST and WebSocket endpoints for command broker.

This module provides API endpoints for submitting commands, checking status,
and real-time command communication through WebSockets.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from app.services.dependency_container import get_container, DependencyContainer
from app.ports.command_broker_port import CommandBrokerPort
from app.ports.command_broker_port import CommandRequest, CommandResponse, CommandType
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/commands", tags=["commands"])


@router.post("/submit")
async def submit_command(
    command: CommandRequest,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Submit a command for execution"""
    try:
        command_broker = container.get_command_broker()
        return await command_broker.submit_command(command)
    except Exception as e:
        logger.error(f"Error submitting command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{command_id}")
async def get_command_status(
    command_id: str,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Get the status of a command"""
    try:
        command_broker = container.get_command_broker()
        return await command_broker.get_command_status(command_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting command status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{command_id}")
async def cancel_command(
    command_id: str,
    container: DependencyContainer = Depends(get_container)
) -> Dict[str, bool]:
    """Cancel a command"""
    try:
        command_broker = container.get_command_broker()
        success = await command_broker.cancel_command(command_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error cancelling command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_command_history(
    session_id: str,
    limit: int = 50,
    container: DependencyContainer = Depends(get_container)
) -> List[CommandResponse]:
    """Get command history for a session"""
    try:
        command_broker = container.get_command_broker()
        return await command_broker.get_command_history(session_id, limit)
    except Exception as e:
        logger.error(f"Error getting command history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_commands(
    websocket: WebSocket,
    session_id: str,
    container: DependencyContainer = Depends(get_container)
):
    """WebSocket endpoint for real-time command communication"""
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        event_bus = container.get_frontend_event_bus()
        async for event in event_bus.subscribe_to_events(session_id):
            # Filter for command-related events
            if event.event_type.startswith("command_"):
                await websocket.send_text(event.json())
    except WebSocketDisconnect:
        logger.info(f"Command WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close()
        except:
            pass


# Convenience endpoints for common commands
@router.post("/trigger-scenario")
async def trigger_scenario(
    scenario_name: str,
    speed: float = 1.0,
    session_id: str = None,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Convenience endpoint to trigger a scenario"""
    try:
        command_broker = container.get_command_broker()
        
        command = CommandRequest(
            command_type=CommandType.SCENARIO_TRIGGER,
            command_id=f"scenario_{scenario_name}_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            parameters={"scenario_name": scenario_name, "speed": speed},
            timestamp=datetime.utcnow(),
            source="api"
        )
        
        return await command_broker.submit_command(command)
    except Exception as e:
        logger.error(f"Error triggering scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inject-news")
async def inject_news(
    title: str,
    content: str,
    source: str = "API",
    category: str = "custom",
    session_id: str = None,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Convenience endpoint to inject news"""
    try:
        command_broker = container.get_command_broker()
        
        command = CommandRequest(
            command_type=CommandType.NEWS_INJECTION,
            command_id=f"news_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            parameters={
                "news": {
                    "title": title,
                    "content": content,
                    "source": source,
                    "category": category,
                    "priority": 1
                }
            },
            timestamp=datetime.utcnow(),
            source="api"
        )
        
        return await command_broker.submit_command(command)
    except Exception as e:
        logger.error(f"Error injecting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-with-character")
async def chat_with_character(
    character_id: str,
    message: str,
    session_id: str = None,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Convenience endpoint to chat with a character"""
    try:
        command_broker = container.get_command_broker()
        
        command = CommandRequest(
            command_type=CommandType.CHARACTER_CHAT,
            command_id=f"chat_{character_id}_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            parameters={"character_id": character_id, "message": message},
            timestamp=datetime.utcnow(),
            source="api"
        )
        
        return await command_broker.submit_command(command)
    except Exception as e:
        logger.error(f"Error chatting with character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-status")
async def get_system_status(
    session_id: str = None,
    container: DependencyContainer = Depends(get_container)
) -> CommandResponse:
    """Convenience endpoint to get system status"""
    try:
        command_broker = container.get_command_broker()
        
        command = CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id=f"status_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            parameters={},
            timestamp=datetime.utcnow(),
            source="api"
        )
        
        return await command_broker.submit_command(command)
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 