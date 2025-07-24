from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
from app.models.demo_scenarios import DemoTriggerRequest
from app.services.demo_orchestrator import demo_orchestrator
from app.services.n8n_integration import n8n_service

router = APIRouter(prefix="/demo", tags=["N8N Demo"])

@router.post("/start")
async def start_demo(background_tasks: BackgroundTasks):
    """
    Start a demo scenario - called by N8N workflow
    
    This is the endpoint that the N8N workflow calls to trigger a demo
    """
    try:
        # Start a default demo scenario (political announcement)
        scenario_id = "political_announcement"
        
        # Validate scenario exists
        if not demo_orchestrator.get_scenario_info(scenario_id):
            raise HTTPException(status_code=404, detail=f"Default scenario {scenario_id} not found")

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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/test-webhook")
async def test_webhook_event():
    """
    Test endpoint to send a sample event to N8N webhook
    
    This helps verify the webhook connection is working
    """
    try:
        # Send a test event to N8N
        test_data = {
            "character_id": "jovani_vazquez",
            "character_name": "Jovani Vazquez",
            "event_type": "test_event",
            "timestamp": datetime.utcnow().isoformat(),
            "test_message": "This is a test event from the API"
        }
        
        success = await n8n_service.emit_event("test_event", test_data)
        
        return {
            "status": "success" if success else "failed",
            "message": "Test event sent to N8N webhook",
            "data": test_data,
            "webhook_url": n8n_service.n8n_webhook_url,
            "demo_mode": n8n_service.demo_mode
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def get_demo_scenarios():
    """Get all available demo scenarios"""
    return demo_orchestrator.get_available_scenarios()

@router.get("/scenarios/{scenario_id}")
async def get_scenario_details(scenario_id: str):
    """Get detailed information about a specific scenario"""
    scenario_info = demo_orchestrator.get_scenario_info(scenario_id)
    if not scenario_info:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return scenario_info

@router.post("/trigger-scenario")
async def trigger_demo_scenario(
    request: DemoTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a demo scenario for N8N visualization

    This will simulate news discovery and character responses
    """
    try:
        # Validate scenario exists
        if not demo_orchestrator.get_scenario_info(request.scenario_id):
            raise HTTPException(status_code=404, detail=f"Scenario {request.scenario_id} not found")

        # Start demo scenario in background
        background_tasks.add_task(
            demo_orchestrator.run_scenario,
            request.scenario_id,
            request.speed_multiplier
        )

        # Immediately notify N8N that demo is starting
        await n8n_service.emit_event("demo_started", {
            "scenario_id": request.scenario_id,
            "scenario_title": demo_orchestrator.get_scenario_title(request.scenario_id),
            "expected_duration": demo_orchestrator.get_estimated_duration(request.scenario_id),
            "speed_multiplier": request.speed_multiplier
        })

        return {
            "status": "success",
            "message": f"Demo scenario '{request.scenario_id}' started",
            "scenario": demo_orchestrator.get_scenario_info(request.scenario_id),
            "speed_multiplier": request.speed_multiplier,
            "estimated_duration": demo_orchestrator.get_estimated_duration(request.scenario_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/emergency-stop")
async def emergency_stop():
    """Stop all running demo scenarios"""
    try:
        demo_orchestrator.stop_all_scenarios()
        await n8n_service.emit_event("demo_stopped", {
            "reason": "emergency_stop",
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"status": "success", "message": "All demo scenarios stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_demo_status():
    """Get current demo status and running scenarios"""
    status = demo_orchestrator.get_demo_status()
    
    # Check N8N connection asynchronously
    status["n8n_connected"] = await demo_orchestrator.check_n8n_connection()
    
    return status

@router.post("/custom-news")
async def trigger_custom_news(
    title: str,
    content: str,
    topics: List[str],
    background_tasks: BackgroundTasks
):
    """Trigger custom news for real-time demonstration"""
    try:
        background_tasks.add_task(
            demo_orchestrator.process_custom_news,
            title, content, topics
        )

        return {
            "status": "success",
            "message": "Custom news injected into system",
            "preview": {"title": title, "topics": topics}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/n8n-status")
async def get_n8n_status():
    """Get N8N integration status"""
    return {
        "n8n_service_status": n8n_service.get_status(),
        "connection_test": await n8n_service.test_connection(),
        "demo_mode_enabled": demo_orchestrator.demo_mode
    }

@router.post("/test-connection")
async def test_n8n_connection():
    """Test N8N webhook connection"""
    try:
        connected = await n8n_service.test_connection()
        return {
            "status": "success" if connected else "failed",
            "connected": connected,
            "webhook_url": n8n_service.n8n_webhook_url,
            "demo_mode": n8n_service.demo_mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_demo_results():
    """Get results from completed demo scenarios"""
    return {
        "completed_scenarios": demo_orchestrator.scenario_results,
        "total_scenarios_run": len(demo_orchestrator.scenario_results),
        "total_events_sent": demo_orchestrator.get_event_count()
    }

@router.post("/reset")
async def reset_demo_state():
    """Reset demo state (clear results and running scenarios)"""
    try:
        demo_orchestrator.running_scenarios.clear()
        demo_orchestrator.scenario_results.clear()
        n8n_service.event_count = 0
        n8n_service.last_event_time = None
        
        return {
            "status": "success",
            "message": "Demo state reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 