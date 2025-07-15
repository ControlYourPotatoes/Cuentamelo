"""
Command Handler Service - Business logic for command execution.

This service handles the execution of different types of commands and integrates
with existing services like frontend, orchestration, and event bus.
"""

import logging
from typing import Dict, Any, callable
from datetime import datetime
from app.ports.command_broker_port import CommandType, CommandStatus, CommandRequest, CommandResponse
from app.ports.frontend_port import FrontendPort, FrontendEvent, UserInteraction, CustomNews, ScenarioCreate
from app.ports.orchestration_service import OrchestrationServicePort
from app.ports.frontend_port import EventBus, UserSessionManager

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles command execution and business logic"""
    
    def __init__(
        self,
        frontend_service: FrontendPort,
        orchestration_service: OrchestrationServicePort,
        event_bus: EventBus,
        session_manager: UserSessionManager
    ):
        self.frontend_service = frontend_service
        self.orchestration_service = orchestration_service
        self.event_bus = event_bus
        self.session_manager = session_manager
        self.command_executors = self._register_command_executors()
    
    def _register_command_executors(self) -> Dict[CommandType, callable]:
        """Register command executors for each command type"""
        return {
            CommandType.SCENARIO_TRIGGER: self._execute_scenario_trigger,
            CommandType.NEWS_INJECTION: self._execute_news_injection,
            CommandType.CHARACTER_CHAT: self._execute_character_chat,
            CommandType.SYSTEM_STATUS: self._execute_system_status,
            CommandType.SCENARIO_CREATE: self._execute_scenario_create,
            CommandType.CHARACTER_CONFIG: self._execute_character_config,
            CommandType.ANALYTICS_QUERY: self._execute_analytics_query
        }
    
    async def execute_command(self, command: CommandRequest) -> CommandResponse:
        """Execute a command based on its type"""
        start_time = datetime.utcnow()
        
        try:
            # Validate command
            if command.command_type not in self.command_executors:
                raise ValueError(f"Unknown command type: {command.command_type}")
            
            # Execute command
            executor = self.command_executors[command.command_type]
            result = await executor(command)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return CommandResponse(
                command_id=command.command_id,
                status=CommandStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                metadata={"source": command.source}
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Command execution failed: {e}", exc_info=True)
            
            return CommandResponse(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                metadata={"source": command.source}
            )
    
    async def _execute_scenario_trigger(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute scenario trigger command"""
        scenario_name = command.parameters.get("scenario_name")
        speed = command.parameters.get("speed", 1.0)
        
        if not scenario_name:
            raise ValueError("scenario_name is required for scenario trigger command")
        
        # Use existing orchestration service
        result = await self.orchestration_service.trigger_scenario(scenario_name, speed)
        
        # Emit event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="scenario_triggered",
            timestamp=datetime.utcnow(),
            data={"scenario_name": scenario_name, "speed": speed, "result": result},
            source="command_handler",
            session_id=command.session_id
        ))
        
        return {"scenario_name": scenario_name, "result": result}
    
    async def _execute_news_injection(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute news injection command"""
        news_data = command.parameters.get("news")
        
        if not news_data:
            raise ValueError("news data is required for news injection command")
        
        custom_news = CustomNews(**news_data)
        result = await self.frontend_service.inject_custom_news(custom_news)
        
        # Emit event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="news_injected",
            timestamp=datetime.utcnow(),
            data={"news_id": result.news_id, "news": news_data},
            source="command_handler",
            session_id=command.session_id
        ))
        
        return {"news_id": result.news_id, "status": result.status}
    
    async def _execute_character_chat(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute character chat command"""
        character_id = command.parameters.get("character_id")
        message = command.parameters.get("message")
        
        if not character_id or not message:
            raise ValueError("character_id and message are required for character chat command")
        
        interaction = UserInteraction(
            session_id=command.session_id or "cli_session",
            character_id=character_id,
            message=message
        )
        
        response = await self.frontend_service.user_interact_with_character(interaction)
        
        # Emit event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="character_chat",
            timestamp=datetime.utcnow(),
            data={
                "character_id": character_id,
                "message": message,
                "response": response.message
            },
            source="command_handler",
            session_id=command.session_id
        ))
        
        return {
            "character_id": character_id,
            "message": response.message,
            "timestamp": response.timestamp.isoformat()
        }
    
    async def _execute_system_status(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute system status command"""
        overview = await self.frontend_service.get_dashboard_overview()
        
        return {
            "system_status": overview.system.dict(),
            "character_count": len(overview.characters),
            "active_scenarios": overview.active_scenarios
        }
    
    async def _execute_scenario_create(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute scenario creation command"""
        scenario_data = command.parameters.get("scenario")
        
        if not scenario_data:
            raise ValueError("scenario data is required for scenario creation command")
        
        scenario_create = ScenarioCreate(**scenario_data)
        result = await self.frontend_service.create_custom_scenario(scenario_create)
        
        # Emit event
        await self.event_bus.publish_event(FrontendEvent(
            event_type="scenario_created",
            timestamp=datetime.utcnow(),
            data={"scenario_id": result.scenario_id, "scenario": scenario_data},
            source="command_handler",
            session_id=command.session_id
        ))
        
        return {"scenario_id": result.scenario_id, "status": result.status}
    
    async def _execute_character_config(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute character configuration command"""
        character_id = command.parameters.get("character_id")
        config = command.parameters.get("config")
        
        if not character_id or not config:
            raise ValueError("character_id and config are required for character config command")
        
        # TODO: Implement character configuration
        # This would integrate with the existing agent factory
        logger.info(f"Character config command received for {character_id}: {config}")
        
        return {"character_id": character_id, "config_updated": True}
    
    async def _execute_analytics_query(self, command: CommandRequest) -> Dict[str, Any]:
        """Execute analytics query command"""
        query_type = command.parameters.get("query_type")
        filters = command.parameters.get("filters", {})
        
        if not query_type:
            raise ValueError("query_type is required for analytics query command")
        
        # TODO: Implement analytics queries
        # This would integrate with the analytics engine
        logger.info(f"Analytics query received: {query_type} with filters {filters}")
        
        return {"query_type": query_type, "results": {}} 