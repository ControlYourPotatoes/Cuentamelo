"""
Command Handler Service - Business logic for command execution.

This service handles the execution of different types of commands and integrates
with existing services like frontend, orchestration, and event bus.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from app.ports.command_broker_port import CommandRequest, CommandResponse, CommandStatus, CommandType
from app.ports.ai_provider import AIProviderPort
from app.ports.news_provider import NewsProviderPort
from app.ports.twitter_provider import TwitterProviderPort
from app.ports.orchestration_service import OrchestrationServicePort
from app.models.conversation import NewsItem

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles execution of different command types"""
    
    def __init__(
        self,
        ai_provider: AIProviderPort,
        news_provider: NewsProviderPort,
        twitter_provider: TwitterProviderPort,
        orchestration_service: OrchestrationServicePort
    ):
        self.ai_provider = ai_provider
        self.news_provider = news_provider
        self.twitter_provider = twitter_provider
        self.orchestration_service = orchestration_service
    
    async def execute_command(self, command: CommandRequest) -> CommandResponse:
        """Execute a command based on its type"""
        logger.info(f"Executing command {command.command_id} of type {command.command_type.value}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            if command.command_type == CommandType.NEWS_INJECTION:
                result = await self._handle_news_injection(command)
            elif command.command_type == CommandType.CHARACTER_CHAT:
                result = await self._handle_character_chat(command)
            elif command.command_type == CommandType.SCENARIO_TRIGGER:
                result = await self._handle_scenario_trigger(command)
            elif command.command_type == CommandType.SYSTEM_STATUS:
                result = await self._handle_system_status(command)
            else:
                result = {"error": f"Unknown command type: {command.command_type.value}"}
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return CommandResponse(
                command_id=command.command_id,
                status=CommandStatus.COMPLETED,
                result=result,
                timestamp=datetime.now(timezone.utc),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error executing command {command.command_id}: {e}")
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return CommandResponse(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                result={"error": str(e)},
                timestamp=datetime.now(timezone.utc),
                execution_time=execution_time
            )
    
    async def _handle_news_injection(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute news injection command"""
        logger.info(f"Handling news injection for command {command.command_id}")
        
        news_data = command.parameters.get("news", {})
        news_item = NewsItem(
            id=f"injected_{command.command_id}",
            headline=news_data.get("title", "Injected News"),
            content=news_data.get("content", "Injected content"),
            topics=news_data.get("topics", []),
            source=news_data.get("source", "Injected"),
            published_at=datetime.now(timezone.utc),
            relevance_score=news_data.get("relevance_score", 0.5)
        )
        
        # TODO: Integrate with news processing pipeline
        # For now, just return success
        return {
            "success": True,
            "news_id": news_item.id,
            "message": "News injected successfully"
        }
    
    async def _handle_character_chat(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute character chat command"""
        logger.info(f"Handling character chat for command {command.command_id}")
        
        character_id = command.parameters.get("character_id")
        message = command.parameters.get("message", "")
        
        if not character_id:
            return {"error": "Character ID is required"}
        
        # TODO: Implement character chat logic
        # For now, return a mock response
        return {
            "success": True,
            "character_id": character_id,
            "response": f"Mock response from {character_id}: {message}",
            "message": "Processed successfully"
        }
    
    async def _handle_scenario_trigger(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute scenario trigger command"""
        logger.info(f"Handling scenario trigger for command {command.command_id}")
        
        scenario_name = command.parameters.get("scenario_name")
        speed = command.parameters.get("speed", 1.0)
        
        if not scenario_name:
            return {"error": "Scenario name is required"}
        
        # TODO: Implement scenario execution
        # For now, return success
        return {
            "success": True,
            "scenario_name": scenario_name,
            "speed": speed,
            "message": "Scenario triggered successfully"
        }
    
    async def _handle_system_status(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute system status command"""
        logger.info(f"Handling system status for command {command.command_id}")
        
        # Check health of all providers
        ai_health = await self.ai_provider.health_check()
        news_health = await self.news_provider.health_check()
        twitter_health = await self.twitter_provider.health_check()
        
        return {
            "success": True,
            "status": "overall",
            "providers": {
                "ai": "healthy" if ai_health else "unhealthy",
                "news": "healthy" if news_health else "unhealthy",
                "twitter": "healthy" if twitter_health else "unhealthy"
            },
            "message": "System status retrieved successfully"
        } 