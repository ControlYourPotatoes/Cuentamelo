"""
LangGraph character workflow for Puerto Rican AI personality orchestration.
Manages the complete character response lifecycle from content analysis to posting.
"""
from typing import Dict, List, Optional, Any, TypedDict
import asyncio
import logging
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.models.conversation import (
    AgentState, ConversationMessage, NewsItem, CharacterReaction,
    AgentDecision, create_agent_state, ThreadEngagementState, MessageType
)
from app.agents.base_character import BaseCharacterAgent

logger = logging.getLogger(__name__)


class CharacterWorkflowState(TypedDict):
    """State for character workflow execution."""
    # Input
    character_agent: BaseCharacterAgent
    input_context: str
    news_item: Optional[NewsItem]
    conversation_history: Optional[List[ConversationMessage]]
    target_topic: Optional[str]
    
    # Thread Context (ENHANCED)
    thread_id: Optional[str]
    thread_context: Optional[str]
    is_new_thread: bool
    thread_engagement_state: Optional[ThreadEngagementState]
    
    # Agent State
    agent_state: AgentState
    
    # Workflow Results
    engagement_decision: Optional[AgentDecision]
    generated_response: Optional[str]
    character_reaction: Optional[CharacterReaction]
    final_message: Optional[ConversationMessage]
    
    # Metadata
    workflow_step: str
    execution_time_ms: int
    error_details: Optional[str]
    success: bool


def create_character_workflow() -> StateGraph:
    """
    Create the main character workflow graph.
    
    Workflow steps:
    1. Initialize -> Agent state setup
    2. Analyze Context -> Content relevance analysis  
    3. Make Decision -> Engagement decision making
    4. Generate Response -> Content generation (if engaging)
    5. Validate Response -> Personality consistency check
    6. Format Output -> Prepare final message
    7. End -> Complete workflow
    """
    
    workflow = StateGraph(CharacterWorkflowState)
    
    # Add workflow nodes
    workflow.add_node("initialize", initialize_agent_state)
    workflow.add_node("analyze_context", analyze_context_relevance)
    workflow.add_node("make_decision", make_engagement_decision)
    workflow.add_node("generate_response", generate_character_response)
    workflow.add_node("validate_response", validate_response_consistency)
    workflow.add_node("format_output", format_final_output)
    workflow.add_node("handle_error", handle_workflow_error)
    
    # Define workflow edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "analyze_context")
    workflow.add_edge("analyze_context", "make_decision")
    
    # Conditional routing based on engagement decision
    workflow.add_conditional_edges(
        "make_decision",
        route_after_decision,
        {
            "engage": "generate_response",
            "ignore": "format_output",
            "defer": "format_output",
            "error": "handle_error"
        }
    )
    
    workflow.add_edge("generate_response", "validate_response")
    
    # Conditional routing based on validation
    workflow.add_conditional_edges(
        "validate_response",
        route_after_validation,
        {
            "valid": "format_output",
            "invalid": "generate_response",  # Retry generation
            "error": "handle_error"
        }
    )
    
    workflow.add_edge("format_output", END)
    workflow.add_edge("handle_error", END)
    
    return workflow


# Node implementations

async def initialize_agent_state(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Initialize the agent state for workflow execution."""
    try:
        start_time = datetime.now(timezone.utc)
        
        character_agent = state["character_agent"]
        
        # Create or update agent state
        if "agent_state" not in state or not state["agent_state"]:
            agent_state = create_agent_state(
                character_agent.character_id,
                character_agent.character_name
            )
        else:
            agent_state = state["agent_state"]
        
        # Update state for current workflow
        agent_state.current_context = state["input_context"]
        agent_state.current_step = "initialize"
        agent_state.workflow_complete = False
        agent_state.error_message = None
        
        # Initialize thread engagement state if needed
        if state.get("is_new_thread", True) and not state.get("thread_engagement_state"):
            thread_id = state.get("thread_id", f"thread_{datetime.now(timezone.utc).timestamp()}")
            state["thread_engagement_state"] = ThreadEngagementState(
                thread_id=thread_id,
                original_content=state["input_context"]
            )
        
        state["agent_state"] = agent_state
        state["workflow_step"] = "initialize"
        state["success"] = True
        
        logger.info(f"Initialized workflow for {character_agent.character_name}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error initializing agent state: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def analyze_context_relevance(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Analyze the relevance of input context to the character."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        context = state["input_context"]
        news_item = state.get("news_item")
        
        agent_state.current_step = "analyze_context"
        
        # Calculate engagement probability
        engagement_prob = character_agent.calculate_engagement_probability(
            context=context,
            conversation_history=state.get("conversation_history"),
            news_item=news_item
        )
        
        # Store analysis results in agent state
        agent_state.decision_confidence = engagement_prob
        agent_state.relevant_context = {
            "engagement_probability": engagement_prob,
            "context_length": len(context),
            "has_news_item": news_item is not None,
            "has_conversation_history": bool(state.get("conversation_history")),
            "is_new_thread": state.get("is_new_thread", True),
            "thread_aware": state.get("thread_engagement_state") is not None
        }
        
        state["agent_state"] = agent_state
        state["workflow_step"] = "analyze_context"
        
        logger.info(f"Context analysis for {character_agent.character_name}: {engagement_prob:.2f}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error analyzing context: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def make_engagement_decision(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Make the engagement decision based on context analysis and thread state."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        context = state["input_context"]
        thread_state = state.get("thread_engagement_state")
        is_new_thread = state.get("is_new_thread", True)
        
        agent_state.current_step = "make_decision"
        
        # Check thread engagement limits if this is a reply
        if not is_new_thread and thread_state:
            if not thread_state.can_character_reply(character_agent.character_id):
                logger.info(f"{character_agent.character_name} cannot reply - thread limit reached")
                state["engagement_decision"] = AgentDecision.DEFER
                state["workflow_step"] = "make_decision"
                return state
        
        # Make engagement decision
        decision = await character_agent.make_engagement_decision(
            state=agent_state,
            context=context,
            conversation_history=state.get("conversation_history"),
            news_item=state.get("news_item")
        )
        
        agent_state.last_decision = decision
        state["agent_state"] = agent_state
        state["engagement_decision"] = decision
        state["workflow_step"] = "make_decision"
        
        logger.info(f"Engagement decision for {character_agent.character_name}: {decision}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error making engagement decision: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def generate_character_response(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Generate character response using AI provider with thread awareness."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        context = state["input_context"]
        thread_state = state.get("thread_engagement_state")
        is_new_thread = state.get("is_new_thread", True)
        
        agent_state.current_step = "generate_response"
        
        # Get thread context for replies
        thread_context = None
        if not is_new_thread and thread_state:
            thread_context = thread_state.get_thread_context(character_agent.character_id)
        
        # Generate response using character agent
        response = await character_agent.generate_response(
            state=agent_state,
            context=context,
            conversation_history=state.get("conversation_history"),
            target_topic=state.get("target_topic"),
            thread_context=thread_context,
            is_new_thread=is_new_thread
        )
        
        # Store response
        state["generated_response"] = response.content
        state["workflow_step"] = "generate_response"
        
        # Update thread state if this is a reply
        if not is_new_thread and thread_state and response.content:
            thread_state.add_character_reply(character_agent.character_id, response.content)
        
        logger.info(f"Generated response for {character_agent.character_name}: {len(response.content)} chars")
        
        return state
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def validate_response_consistency(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Validate that the generated response maintains character consistency."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        generated_response = state.get("generated_response")
        
        agent_state.current_step = "validate_response"
        
        if not generated_response:
            state["workflow_step"] = "validate_response"
            return state
        
        # Validate personality consistency using AI provider
        if character_agent.ai_provider:
            is_consistent = await character_agent.ai_provider.validate_personality_consistency(
                personality_data=character_agent.personality_data,
                generated_content=generated_response
            )
        else:
            # Fallback validation - check for signature phrases
            is_consistent = any(
                phrase.lower() in generated_response.lower() 
                for phrase in character_agent.personality_data.signature_phrases[:3]
            )
        
        # Update agent state
        agent_state.content_approved = is_consistent
        agent_state.personality_consistency_score = 1.0 if is_consistent else 0.0
        
        state["agent_state"] = agent_state
        state["workflow_step"] = "validate_response"
        
        logger.info(f"Response validation for {character_agent.character_name}: {'valid' if is_consistent else 'invalid'}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error validating response: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def format_final_output(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Format the final output message."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        decision = state.get("engagement_decision")
        generated_response = state.get("generated_response")
        
        agent_state.current_step = "format_output"
        
        if decision == AgentDecision.ENGAGE and generated_response:
            # Create conversation message
            message = ConversationMessage(
                character_id=character_agent.character_id,
                character_name=character_agent.character_name,
                content=generated_response,
                message_type=MessageType.CHARACTER_REPLY if not state.get("is_new_thread", True) else MessageType.CONVERSATION_START,
                engagement_score=agent_state.personality_consistency_score,
                metadata={
                    "thread_id": state.get("thread_id"),
                    "is_new_thread": state.get("is_new_thread", True),
                    "personality_consistency": agent_state.content_approved,
                    "response_time_ms": agent_state.response_time_ms
                }
            )
            
            state["final_message"] = message
            
            # Create character reaction if this is a news response
            if state.get("news_item"):
                reaction = CharacterReaction(
                    character_id=character_agent.character_id,
                    character_name=character_agent.character_name,
                    news_item_id=state["news_item"].id,
                    reaction_content=generated_response,
                    decision=decision,
                    confidence_score=agent_state.decision_confidence,
                    reasoning=agent_state.decision_reasoning
                )
                state["character_reaction"] = reaction
        
        # Mark workflow as complete
        agent_state.workflow_complete = True
        state["agent_state"] = agent_state
        state["workflow_step"] = "format_output"
        state["success"] = True
        
        logger.info(f"Formatted output for {character_agent.character_name}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error formatting output: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def handle_workflow_error(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Handle workflow errors gracefully."""
    try:
        character_agent = state["character_agent"]
        agent_state = state.get("agent_state")
        
        if agent_state:
            agent_state.current_step = "error"
            agent_state.workflow_complete = True
            agent_state.error_message = state.get("error_details", "Unknown error")
            state["agent_state"] = agent_state
        
        state["workflow_step"] = "handle_error"
        state["success"] = False
        
        logger.error(f"Workflow error for {character_agent.character_name}: {state.get('error_details')}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


# Routing functions

def route_after_decision(state: CharacterWorkflowState) -> str:
    """Route workflow based on engagement decision."""
    decision = state.get("engagement_decision")
    
    if decision == AgentDecision.ENGAGE:
        return "engage"
    elif decision == AgentDecision.IGNORE:
        return "ignore"
    elif decision == AgentDecision.DEFER:
        return "defer"
    else:
        return "error"


def route_after_validation(state: CharacterWorkflowState) -> str:
    """Route workflow based on response validation."""
    agent_state = state.get("agent_state")
    
    if not agent_state:
        return "error"
    
    if agent_state.content_approved:
        return "valid"
    else:
        # Retry generation if not consistent
        retry_count = state.get("retry_count", 0)
        if retry_count < 2:  # Max 2 retries
            state["retry_count"] = retry_count + 1
            return "invalid"
        else:
            return "error"


# Main execution function

async def execute_character_workflow(
    character_agent: BaseCharacterAgent,
    input_context: str,
    news_item: Optional[NewsItem] = None,
    conversation_history: Optional[List[ConversationMessage]] = None,
    target_topic: Optional[str] = None,
    thread_id: Optional[str] = None,
    thread_context: Optional[str] = None,
    is_new_thread: bool = True,
    thread_engagement_state: Optional[ThreadEngagementState] = None,
    workflow_executor: Optional['WorkflowExecutorPort'] = None
) -> CharacterWorkflowState:
    """
    Execute the complete character workflow.
    
    Args:
        character_agent: The character agent to execute
        input_context: Content to respond to
        news_item: News item if this is a news reaction
        conversation_history: Previous conversation messages
        target_topic: Specific topic to focus on
        thread_id: Thread identifier for replies
        thread_context: Context from existing thread
        is_new_thread: Whether this is a new thread or reply
        thread_engagement_state: Thread engagement state for rate limiting
        workflow_executor: Workflow executor (injected dependency)
        
    Returns:
        CharacterWorkflowState: Complete workflow result
    """
    try:
        # Create workflow state
        workflow_state = CharacterWorkflowState(
            character_agent=character_agent,
            input_context=input_context,
            news_item=news_item,
            conversation_history=conversation_history or [],
            target_topic=target_topic,
            thread_id=thread_id,
            thread_context=thread_context,
            is_new_thread=is_new_thread,
            thread_engagement_state=thread_engagement_state,
            agent_state=None,
            engagement_decision=None,
            generated_response=None,
            character_reaction=None,
            final_message=None,
            workflow_step="",
            execution_time_ms=0,
            error_details=None,
            success=False
        )
        
        # Create workflow
        workflow = create_character_workflow()
        
        # Use injected workflow executor or create default
        if workflow_executor is None:
            from app.adapters.langgraph_workflow_adapter import LangGraphWorkflowAdapter
            workflow_executor = LangGraphWorkflowAdapter()
        
        # Execute workflow using the executor
        execution_result = await workflow_executor.execute_workflow(
            workflow_definition=workflow,
            initial_state=workflow_state
        )
        
        # Extract result
        if execution_result.success:
            result = execution_result.final_state
            result["execution_time_ms"] = execution_result.execution_time_ms
            return result
        else:
            # Return error state
            workflow_state["workflow_step"] = "error"
            workflow_state["execution_time_ms"] = execution_result.execution_time_ms
            workflow_state["error_details"] = execution_result.error_details
            workflow_state["success"] = False
            return workflow_state
        
    except Exception as e:
        logger.error(f"Error executing character workflow: {str(e)}")
        return CharacterWorkflowState(
            character_agent=character_agent,
            input_context=input_context,
            news_item=news_item,
            conversation_history=conversation_history or [],
            target_topic=target_topic,
            thread_id=thread_id,
            thread_context=thread_context,
            is_new_thread=is_new_thread,
            thread_engagement_state=thread_engagement_state,
            agent_state=None,
            engagement_decision=None,
            generated_response=None,
            character_reaction=None,
            final_message=None,
            workflow_step="error",
            execution_time_ms=0,
            error_details=str(e),
            success=False
        ) 