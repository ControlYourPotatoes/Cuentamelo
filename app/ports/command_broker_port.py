"""
Command Broker Port - Abstract interfaces for command processing.

This module defines the abstract interfaces that command broker implementations must follow,
following the Ports & Adapters pattern used throughout the project.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class CommandType(Enum):
    """Types of commands that can be executed"""
    SCENARIO_TRIGGER = "scenario_trigger"
    NEWS_INJECTION = "news_injection"
    CHARACTER_CHAT = "character_chat"
    SYSTEM_STATUS = "system_status"
    SCENARIO_CREATE = "scenario_create"
    CHARACTER_CONFIG = "character_config"
    ANALYTICS_QUERY = "analytics_query"


class CommandStatus(Enum):
    """Status of command execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandRequest(BaseModel):
    """Command request from any interface"""
    command_type: CommandType
    command_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    parameters: Dict[str, Any] = {}
    timestamp: datetime
    source: str  # "web", "cli", "api"
    priority: int = 1


class CommandResponse(BaseModel):
    """Response to a command execution"""
    command_id: str
    status: CommandStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class CommandBrokerPort(ABC):
    """Abstract interface for command broker operations"""
    
    @abstractmethod
    async def submit_command(self, command: CommandRequest) -> CommandResponse:
        """Submit a command for execution"""
        pass
    
    @abstractmethod
    async def get_command_status(self, command_id: str) -> CommandResponse:
        """Get the status of a command"""
        pass
    
    @abstractmethod
    async def cancel_command(self, command_id: str) -> bool:
        """Cancel a pending command"""
        pass
    
    @abstractmethod
    async def get_command_history(self, session_id: str, limit: int = 50) -> List[CommandResponse]:
        """Get command history for a session"""
        pass 