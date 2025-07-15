"""
Frontend Event Bus - Real-time event communication for frontend.

This module implements the EventBus interface for real-time communication
between frontend components and the backend system using Redis pub/sub.
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.ports.frontend_port import EventBus, FrontendEvent
from app.services.redis_client import RedisClient

logger = logging.getLogger(__name__)


class FrontendEventBus(EventBus):
    """
    Redis-based implementation of the EventBus interface.
    
    This service provides real-time event communication between frontend
    components and the backend system using Redis pub/sub mechanism.
    """
    
    def __init__(self, redis_client: RedisClient):
        """
        Initialize frontend event bus.
        
        Args:
            redis_client: Redis client for pub/sub communication
        """
        self.redis_client = redis_client
        self.pubsub = None
        self._active_subscriptions: Dict[str, bool] = {}
        
        logger.info("Frontend Event Bus initialized")
    
    async def publish_event(self, event: FrontendEvent) -> None:
        """
        Publish frontend event to all subscribers.
        
        Args:
            event: Event to publish.
        """
        try:
            # Convert event to JSON
            event_json = event.json()
            
            # Publish to Redis channel
            await self.redis_client.publish("frontend:events", event_json)
            
            # Also publish to session-specific channel if session_id is provided
            if event.session_id:
                await self.redis_client.publish(
                    f"frontend:session:{event.session_id}",
                    event_json
                )
            
            logger.debug(f"Published event {event.event_type} to frontend:events")
            
        except Exception as e:
            logger.error(f"Error publishing event {event.event_type}: {e}")
            raise
    
    async def subscribe_to_events(self, session_id: str):
        """
        Subscribe to frontend events for a session.
        
        Args:
            session_id: Session ID to subscribe for.
            
        Yields:
            FrontendEvent: Events for the session.
        """
        try:
            # Mark this session as actively subscribed
            self._active_subscriptions[session_id] = True
            
            # Create pubsub connection
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to general events and session-specific events
            await self.pubsub.subscribe("frontend:events")
            await self.pubsub.subscribe(f"frontend:session:{session_id}")
            
            logger.info(f"Subscribed to events for session {session_id}")
            
            # Listen for messages
            async for message in self.pubsub.listen():
                if not self._active_subscriptions.get(session_id, False):
                    # Session unsubscribed, break the loop
                    break
                
                if message["type"] == "message":
                    try:
                        # Parse event from JSON
                        event_data = json.loads(message["data"])
                        event = FrontendEvent.parse_obj(event_data)
                        
                        # Filter events based on session permissions
                        if self._should_receive_event(event, session_id):
                            yield event
                            
                    except Exception as e:
                        logger.error(f"Error parsing event message: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in event subscription for session {session_id}: {e}")
            raise
        finally:
            # Clean up subscription
            await self._cleanup_subscription(session_id)
    
    async def unsubscribe_from_events(self, session_id: str) -> bool:
        """
        Unsubscribe from events for a session.
        
        Args:
            session_id: Session ID to unsubscribe.
            
        Returns:
            bool: True if unsubscribed successfully.
        """
        try:
            # Mark session as unsubscribed
            self._active_subscriptions[session_id] = False
            
            # Unsubscribe from Redis channels
            if self.pubsub:
                await self.pubsub.unsubscribe("frontend:events")
                await self.pubsub.unsubscribe(f"frontend:session:{session_id}")
            
            logger.info(f"Unsubscribed from events for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing session {session_id}: {e}")
            return False
    
    async def publish_system_event(self, event_type: str, data: Dict[str, Any], source: str = "system"):
        """
        Publish system-wide event.
        
        Args:
            event_type: Type of event.
            data: Event data.
            source: Source of the event.
        """
        event = FrontendEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            data=data,
            source=source
        )
        
        await self.publish_event(event)
    
    async def publish_session_event(
        self,
        session_id: str,
        event_type: str,
        data: Dict[str, Any],
        source: str = "system"
    ):
        """
        Publish event to a specific session.
        
        Args:
            session_id: Target session ID.
            event_type: Type of event.
            data: Event data.
            source: Source of the event.
        """
        event = FrontendEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            data=data,
            source=source,
            session_id=session_id
        )
        
        await self.publish_event(event)
    
    def _should_receive_event(self, event: FrontendEvent, session_id: str) -> bool:
        """
        Determine if a session should receive a specific event.
        
        Args:
            event: Event to check.
            session_id: Session ID to check for.
            
        Returns:
            bool: True if session should receive the event.
        """
        # If event has a specific session_id, only that session should receive it
        if event.session_id and event.session_id != session_id:
            return False
        
        # TODO: Implement more sophisticated permission-based filtering
        # For now, all sessions receive all events
        
        return True
    
    async def _cleanup_subscription(self, session_id: str):
        """
        Clean up subscription resources.
        
        Args:
            session_id: Session ID to clean up.
        """
        try:
            # Remove from active subscriptions
            self._active_subscriptions.pop(session_id, None)
            
            # Close pubsub connection if no active subscriptions
            if not self._active_subscriptions and self.pubsub:
                await self.pubsub.close()
                self.pubsub = None
                
        except Exception as e:
            logger.error(f"Error cleaning up subscription for session {session_id}: {e}")
    
    async def get_active_subscriptions(self) -> Dict[str, bool]:
        """
        Get currently active subscriptions.
        
        Returns:
            Dict[str, bool]: Dictionary of session IDs and their subscription status.
        """
        return self._active_subscriptions.copy()
    
    async def health_check(self) -> bool:
        """
        Check if the event bus is healthy.
        
        Returns:
            bool: True if healthy, False otherwise.
        """
        try:
            # Test Redis connection
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Event bus health check failed: {e}")
            return False 