from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/n8n-callback")
async def n8n_callback(request: Request):
    """
    Receive callbacks from N8N workflows
    
    This endpoint can be used by N8N to send data back to our system
    """
    try:
        data = await request.json()
        logger.info(f"Received N8N callback: {data}")
        
        # Process the callback data
        # This could be used for:
        # - Acknowledging events
        # - Receiving processed data from N8N
        # - Status updates from N8N workflows
        
        return {
            "status": "success",
            "message": "Callback received and processed",
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Error processing N8N callback: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/n8n-status")
async def n8n_status_update(request: Request):
    """
    Receive status updates from N8N workflows
    
    This can be used to track the status of N8N workflows
    """
    try:
        data = await request.json()
        logger.info(f"Received N8N status update: {data}")
        
        # Process status update
        # This could update our internal tracking of N8N workflow status
        
        return {
            "status": "success",
            "message": "Status update received",
            "workflow_status": data.get("status", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Error processing N8N status update: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def webhook_health():
    """Health check for webhook endpoints"""
    return {
        "status": "healthy",
        "endpoints": [
            "/webhooks/n8n-callback",
            "/webhooks/n8n-status"
        ],
        "message": "Webhook endpoints are ready to receive N8N callbacks"
    } 