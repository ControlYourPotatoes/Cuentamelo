"""
Frontend Event Bus - Real-time event communication for frontend.

This module implements the EventBus interface for real-time communication
between frontend components and the backend system using Redis pub/sub.
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
from app.ports.frontend_port import FrontendEvent, EventBus, EventSubscriber

logger = logging.getLogger(__name__)


class FrontendEventBus(EventBus):
    """
    Redis-based implementation of the EventBus interface.
    
    This service provides real-time event communication between frontend
    components and the backend system using Redis pub/sub mechanism.
    """
    
    def __init__(self, redis_client):
        """
        Initialize frontend event bus.
        
        Args:
            redis_client: Redis client for pub/sub communication
        """
        self.redis_client = redis_client
        self.subscribers: Dict[str, List[EventSubscriber]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        logger.info("Frontend Event Bus initialized")
    
    async def publish_event(self, event: FrontendEvent) -> bool:
        """
        Publish frontend event to all subscribers.
        
        Args:
            event: Event to publish.
        """
        try:
            # Convert event to JSON for Redis
            event_json = event.model_dump_json()
            
            # Publish to Redis channel
            channel = f"frontend_events:{event.session_id}" if event.session_id else "frontend_events:global"
            await self.redis_client.publish(channel, event_json)
            
            # Also notify local subscribers
            await self._notify_subscribers(event)
            
            logger.debug(f"Published event {event.event_type} to {channel}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            return False
    
    async def subscribe(self, event_type: str, subscriber: EventSubscriber, session_id: str = None) -> bool:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to.
            subscriber: The subscriber callback.
            session_id: Optional session ID to subscribe to.
            
        Returns:
            bool: True if subscribed successfully.
        """
        try:
            key = f"{event_type}:{session_id}" if session_id else event_type
            if key not in self.subscribers:
                self.subscribers[key] = []
            self.subscribers[key].append(subscriber)
            
            logger.debug(f"Subscribed {subscriber} to {event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {event_type}: {e}")
            return False
    
    async def unsubscribe(self, event_type: str, subscriber: EventSubscriber, session_id: str = None) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of event to unsubscribe from.
            subscriber: The subscriber callback.
            session_id: Optional session ID to unsubscribe from.
            
        Returns:
            bool: True if unsubscribed successfully.
        """
        try:
            key = f"{event_type}:{session_id}" if session_id else event_type
            if key in self.subscribers and subscriber in self.subscribers[key]:
                self.subscribers[key].remove(subscriber)
                logger.debug(f"Unsubscribed {subscriber} from {event_type}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {event_type}: {e}")
            return False
    
    async def subscribe_to_events(self, session_id: str):
        """
        Subscribe to frontend events for a session.
        
        Args:
            session_id: Session ID to subscribe for.
            
        Yields:
            FrontendEvent: Events for the session.
        """
        try:
            # Subscribe to session-specific events
            pubsub = await self.redis_client._get_client().pubsub()
            await pubsub.subscribe(f"frontend_events:{session_id}")
            await pubsub.subscribe("frontend_events:global")
            
            while True:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        event_data = json.loads(message['data'])
                        event = FrontendEvent.model_validate(event_data)
                        
                        # Filter events for this session
                        if event.session_id is None or event.session_id == session_id:
                            yield event
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
                    
        except Exception as e:
            logger.error(f"Error in event subscription for session {session_id}: {e}")
        finally:
            if pubsub:
                await pubsub.close()

    async def _notify_subscribers(self, event: FrontendEvent):
        """
        Notify all subscribers of an event.
        
        Args:
            event: The event to notify about.
        """
        try:
            # Notify global subscribers
            if event.event_type in self.subscribers:
                for subscriber in self.subscribers[event.event_type]:
                    try:
                        await subscriber(event)
                    except Exception as e:
                        logger.error(f"Subscriber error for {event.event_type}: {e}")
            
            # Notify session-specific subscribers
            session_key = f"{event.event_type}:{event.session_id}"
            if session_key in self.subscribers:
                for subscriber in self.subscribers[session_key]:
                    try:
                        await subscriber(event)
                    except Exception as e:
                        logger.error(f"Session subscriber error for {event.event_type}: {e}")
                        
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
    
    async def start(self):
        """
        Start the event bus and begin listening for Redis events.
        """
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._listen_for_events())
        logger.info("Frontend event bus started")
    
    async def stop(self):
        """
        Stop the event bus.
        """
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Frontend event bus stopped")
    
    async def _listen_for_events(self):
        """
        Listen for events from Redis and forward to local subscribers.
        """
        try:
            # Subscribe to global events
            pubsub = await self.redis_client._get_client().pubsub()
            await pubsub.subscribe("frontend_events:global")
            
            while self._running:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        event_data = json.loads(message['data'])
                        event = FrontendEvent.model_validate(event_data)
                        await self._notify_subscribers(event)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
                    
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
        finally:
            if pubsub:
                await pubsub.close() 