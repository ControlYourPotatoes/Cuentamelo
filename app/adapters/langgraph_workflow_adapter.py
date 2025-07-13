"""
LangGraph workflow adapter that implements WorkflowExecutorPort.
Handles proper compilation and execution of LangGraph workflows.
"""
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from app.ports.workflow_executor import WorkflowExecutorPort, WorkflowExecutionResult

logger = logging.getLogger(__name__)


class LangGraphWorkflowAdapter(WorkflowExecutorPort):
    """Adapter for executing LangGraph workflows with proper compilation."""
    
    def __init__(self):
        """Initialize the LangGraph workflow adapter."""
        self.executor_type = "langgraph"
        self.version = self._get_langgraph_version()
    
    async def execute_workflow(
        self,
        workflow_definition: Any,  # StateGraph
        initial_state: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionResult:
        """
        Execute a LangGraph workflow with proper compilation.
        
        Args:
            workflow_definition: StateGraph workflow definition
            initial_state: Initial state for the workflow
            config: Optional configuration (unused for LangGraph)
            
        Returns:
            WorkflowExecutionResult: Result of the workflow execution
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Compile the workflow
            logger.debug("Compiling LangGraph workflow")
            compiled_workflow = workflow_definition.compile()
            
            # Execute the workflow
            logger.debug("Executing compiled workflow")
            final_state = await compiled_workflow.ainvoke(initial_state)
            
            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Create result
            result = WorkflowExecutionResult(
                success=True,
                final_state=final_state,
                execution_time_ms=execution_time_ms,
                metadata={
                    "executor_type": self.executor_type,
                    "version": self.version,
                    "compilation_successful": True,
                    "execution_method": "ainvoke"
                }
            )
            
            logger.info(f"Workflow executed successfully in {execution_time_ms}ms")
            return result
            
        except Exception as e:
            # Calculate execution time even for failures
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            logger.error(f"Workflow execution failed: {str(e)}")
            
            # Return error result
            return WorkflowExecutionResult(
                success=False,
                final_state=initial_state,
                execution_time_ms=execution_time_ms,
                error_details=str(e),
                metadata={
                    "executor_type": self.executor_type,
                    "version": self.version,
                    "compilation_successful": False,
                    "error_type": type(e).__name__
                }
            )
    
    async def health_check(self) -> bool:
        """
        Check if LangGraph is available and healthy.
        
        Returns:
            bool: True if LangGraph is available
        """
        try:
            from langgraph.graph import StateGraph
            return True
        except ImportError:
            logger.warning("LangGraph not available")
            return False
    
    def get_executor_info(self) -> Dict[str, Any]:
        """
        Get information about the LangGraph workflow executor.
        
        Returns:
            Dict containing executor information
        """
        return {
            "executor_type": self.executor_type,
            "version": self.version,
            "capabilities": [
                "async_execution",
                "workflow_compilation",
                "state_management",
                "conditional_routing"
            ],
            "supported_workflow_types": ["StateGraph"],
            "execution_methods": ["ainvoke"]
        }
    
    def _get_langgraph_version(self) -> str:
        """Get the LangGraph version."""
        try:
            import langgraph
            return getattr(langgraph, '__version__', 'unknown')
        except ImportError:
            return 'not_installed' 