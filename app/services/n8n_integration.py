import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from queue import Queue
import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)

class N8NWebhookService:
    """Service for sending real-time events to N8N workflows"""

    def __init__(self):
        self.n8n_webhook_url = settings.N8N_WEBHOOK_URL
        self.demo_mode = settings.DEMO_MODE_ENABLED
        self.event_queue = Queue()
        self.session: Optional[aiohttp.ClientSession] = None
        self.event_count = 0
        self.last_event_time: Optional[datetime] = None

    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=settings.N8N_WEBHOOK_TIMEOUT)
            )

    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Send event to N8N webhook

        Args:
            event_type: Event type from N8N_EVENTS
            data: Event data dictionary

        Returns:
            bool: True if successful, False if failed (non-blocking)
        """
        if not self.demo_mode or not self.n8n_webhook_url:
            return True  # Silent success when demo mode disabled

        try:
            await self.initialize()

            payload = {
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
                "source": "cuentamelo_langgraph",
                "demo_session_id": settings.DEMO_SESSION_ID
            }

            async with self.session.post(
                f"{self.n8n_webhook_url}/webhook/cuentamelo-event",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    self.event_count += 1
                    self.last_event_time = datetime.now(timezone.utc)
                    logger.info(f"N8N event sent: {event_type} (total: {self.event_count})")
                    return True
                else:
                    logger.warning(f"N8N webhook failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"N8N webhook error: {e}")
            return False  # Fail gracefully without breaking main flow

    def queue_event(self, event_type: str, data: Dict[str, Any]):
        """Queue event for async processing (for sync functions)"""
        if self.demo_mode:
            self.event_queue.put({
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def process_queued_events(self):
        """Process events from sync function queue"""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                await self.emit_event(event["event_type"], event["data"])
            except Exception as e:
                logger.error(f"Error processing queued event: {e}")

    async def test_connection(self) -> bool:
        """Test N8N webhook connection"""
        if not self.demo_mode or not self.n8n_webhook_url:
            return False
            
        try:
            await self.initialize()
            
            test_payload = {
                "event_type": "connection_test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"test": True},
                "source": "cuentamelo_langgraph",
                "demo_session_id": settings.DEMO_SESSION_ID
            }
            
            async with self.session.post(
                f"{self.n8n_webhook_url}/webhook/cuentamelo-event",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"N8N connection test failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "demo_mode_enabled": self.demo_mode,
            "n8n_webhook_url": self.n8n_webhook_url,
            "total_events_sent": self.event_count,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "queued_events": self.event_queue.qsize(),
            "session_active": self.session is not None
        }

    async def cleanup(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()

# Global instance
n8n_service = N8NWebhookService()

# Convenience function for direct use
async def emit_event(event_type: str, data: Dict[str, Any]) -> bool:
    """Convenience function to emit events"""
    return await n8n_service.emit_event(event_type, data)

def queue_event(event_type: str, data: Dict[str, Any]):
    """Convenience function to queue events"""
    n8n_service.queue_event(event_type, data) 