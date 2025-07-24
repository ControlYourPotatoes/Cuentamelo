"""
Command Broker Service - Central command processing and routing.

This service acts as the central broker for all commands from different interfaces
(web, CLI, API) and handles command persistence, status tracking, and event emission.
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.ports.command_broker_port import CommandBrokerPort, CommandRequest, CommandResponse, CommandStatus
from app.ports.frontend_port import FrontendEvent, EventBus
from app.services.redis_client import RedisClient
from app.services.command_handler import CommandHandler

logger = logging.getLogger(__name__)


class CommandBrokerService(CommandBrokerPort):
    """Central command broker that handles all interface commands"""
    
    def __init__(
        self,
        command_handler: CommandHandler,
        redis_client: RedisClient,
        event_bus: EventBus
    ):
        self.command_handler = command_handler
        self.redis_client = redis_client
        self.event_bus = event_bus
        self.active_commands: Dict[str, CommandRequest] = {}
    
    async def submit_command(self, command: CommandRequest) -> CommandResponse:
        """Submit a command for execution"""
        logger.info(f"Submitting command {command.command_id} of type {command.command_type.value}")
        
        # Store command in Redis for persistence
        await self.redis_client.set(
            f"command:{command.command_id}",
            command.model_dump_json(),
            ttl=3600  # 1 hour
        )
        
        # Add to active commands
        self.active_commands[command.command_id] = command
        
        # Emit command submitted event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="command_submitted",
            timestamp=datetime.now(timezone.utc),
            data={
                "command_id": command.command_id, 
                "command_type": command.command_type.value,
                "source": command.source
            },
            source="command_broker",
            session_id=command.session_id
        ))
        
        # Execute command asynchronously
        response = await self.command_handler.execute_command(command)
        
        # Store response
        await self.redis_client.set(
            f"command_response:{command.command_id}",
            response.model_dump_json(),
            ttl=3600  # 1 hour
        )
        
        # Remove from active commands
        if command.command_id in self.active_commands:
            del self.active_commands[command.command_id]
        
        # Emit command completed event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="command_completed",
            timestamp=datetime.now(timezone.utc),
            data={
                "command_id": command.command_id, 
                "status": response.status.value,
                "execution_time": response.execution_time
            },
            source="command_broker",
            session_id=command.session_id
        ))
        
        logger.info(f"Command {command.command_id} completed with status {response.status.value}")
        return response
    
    async def get_command_status(self, command_id: str) -> CommandResponse:
        """Get the status of a command"""
        logger.debug(f"Getting status for command {command_id}")
        
        # Check if command is still active
        if command_id in self.active_commands:
            return CommandResponse(
                command_id=command_id,
                status=CommandStatus.EXECUTING,
                execution_time=0.0,  # Still executing, no time yet
                timestamp=datetime.now(timezone.utc),
                metadata={"active": True}
            )
        
        # Get response from Redis
        response_data = await self.redis_client.get(f"command_response:{command_id}")
        if response_data:
            return CommandResponse.model_validate_json(response_data)
        
        # Check if command exists but no response
        command_data = await self.redis_client.get(f"command:{command_id}")
        if command_data:
            return CommandResponse(
                command_id=command_id,
                status=CommandStatus.PENDING,
                execution_time=0.0,  # Not started yet
                timestamp=datetime.now(timezone.utc),
                metadata={"command_found": True}
            )
        
        raise ValueError(f"Command {command_id} not found")
    
    async def cancel_command(self, command_id: str) -> bool:
        """Cancel a pending command"""
        logger.info(f"Attempting to cancel command {command_id}")
        
        if command_id in self.active_commands:
            del self.active_commands[command_id]
            
            # Emit command cancelled event
            await self.event_bus.publish_event(FrontendEvent(
                event_type="command_cancelled",
                timestamp=datetime.now(timezone.utc),
                data={"command_id": command_id},
                source="command_broker"
            ))
            
            logger.info(f"Command {command_id} cancelled successfully")
            return True
        
        logger.warning(f"Command {command_id} not found in active commands")
        return False
    
    async def get_command_history(self, session_id: str, limit: int = 50) -> List[CommandResponse]:
        logger.debug(f"Getting command history for session {session_id}, limit {limit}")
        try:
            # Properly await the Redis client and keys method
            client = await self.redis_client._get_client()
            all_keys = await client.keys("command_response:*")
            responses = []
            for key in all_keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                response_data = await self.redis_client.get(key_str)
                if response_data:
                    try:
                        response = CommandResponse.model_validate_json(response_data)
                        command_id = key_str.replace("command_response:", "")
                        command_data = await self.redis_client.get(f"command:{command_id}")
                        if command_data:
                            command = CommandRequest.model_validate_json(command_data)
                            if command.session_id == session_id:
                                responses.append(response)
                    except Exception as e:
                        logger.warning(f"Failed to parse command response from {key_str}: {e}")
                        continue
            responses.sort(key=lambda x: x.timestamp, reverse=True)
            return responses[:limit]
        except Exception as e:
            logger.error(f"Error retrieving command history for session {session_id}: {e}")
            return []
    
    async def get_active_commands(self) -> List[CommandRequest]:
        """Get list of currently active commands"""
        return list(self.active_commands.values())
    
    async def cleanup_expired_commands(self):
        """Clean up expired commands from memory"""
        # This could be called periodically to clean up stale commands
        # For now, just log the current active commands
        logger.info(f"Active commands: {len(self.active_commands)}")
        for cmd_id, cmd in self.active_commands.items():
            logger.debug(f"Active command: {cmd_id} - {cmd.command_type.value}") 