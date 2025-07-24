"""
Workflow execution port for LangGraph workflows.
Defines the interface for executing workflows with proper compilation and error handling.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


class WorkflowExecutionResult:
    """Result of a workflow execution."""
    
    def __init__(
        self,
        success: bool,
        final_state: Dict[str, Any],
        execution_time_ms: int,
        error_details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.final_state = final_state
        self.execution_time_ms = execution_time_ms
        self.error_details = error_details
        self.metadata = metadata or {}


class WorkflowExecutorPort(ABC):
    """Port for executing LangGraph workflows with proper compilation and error handling."""
    
    @abstractmethod
    async def execute_workflow(
        self,
        workflow_definition: Any,  # StateGraph
        initial_state: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow with given state and configuration.
        
        Args:
            workflow_definition: The workflow definition (StateGraph)
            initial_state: Initial state for the workflow
            config: Optional configuration for execution
            
        Returns:
            WorkflowExecutionResult: Result of the workflow execution
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the workflow executor is available and healthy.
        
        Returns:
            bool: True if the executor is available
        """
        pass
    
    @abstractmethod
    def get_executor_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow executor.
        
        Returns:
            Dict containing executor type, version, capabilities, etc.
        """
        pass 