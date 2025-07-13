"""
LangGraph character workflow for Puerto Rican AI personality orchestration.
Manages the complete character response lifecycle from content analysis to posting.
"""
from typing import Dict, List, Optional, Any, TypedDict
import asyncio
import logging
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.models.conversation import (
    AgentState, ConversationMessage, NewsItem, CharacterReaction,
    AgentDecision, create_agent_state
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
    
    # Thread Context (NEW)
    thread_id: Optional[str]
    thread_context: Optional[str]
    is_new_thread: bool
    thread_engagement_state: Optional[Any]  # ThreadEngagementState
    
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
        start_time = datetime.utcnow()
        
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
            "has_conversation_history": bool(state.get("conversation_history"))
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
    """Make the engagement decision based on context analysis."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        context = state["input_context"]
        
        agent_state.current_step = "make_decision"
        
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
    """Generate character response using Claude API with thread awareness."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        context = state["input_context"]
        
        agent_state.current_step = "generate_response"
        
        # THREAD-AWARE CONTEXT ENHANCEMENT
        enhanced_context = context
        
        # Check if this is a thread reply
        if state.get("thread_engagement_state") and not state.get("is_new_thread", True):
            thread_state = state["thread_engagement_state"]
            thread_context = thread_state.get_thread_context(character_agent.character_id)
            enhanced_context = f"Thread context: {thread_context}\n\nOriginal content: {context}"
            
            # Add Twitter-specific context
            enhanced_context += "\n\nIMPORTANT: This is a reply to an existing Twitter thread. Keep your response concise and engaging. Reference the thread context naturally."
        else:
            # New thread - add Twitter context
            enhanced_context += "\n\nIMPORTANT: This is a new Twitter post. Make it engaging and start a conversation. Use appropriate hashtags and mentions if relevant."
        
        # Generate response using character agent
        claude_response = await character_agent.generate_response(
            state=agent_state,
            context=enhanced_context,
            conversation_history=state.get("conversation_history"),
            target_topic=state.get("target_topic")
        )
        
        # Store generated content
        agent_state.generated_content = claude_response.content
        agent_state.personality_consistency_score = claude_response.confidence_score
        agent_state.response_time_ms = claude_response.response_time_ms
        agent_state.content_approved = claude_response.character_consistency
        
        state["agent_state"] = agent_state
        state["generated_response"] = claude_response.content
        state["workflow_step"] = "generate_response"
        
        logger.info(f"Generated {'thread reply' if not state.get('is_new_thread', True) else 'new post'} for {character_agent.character_name}: {len(claude_response.content)} chars")
        
        return state
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def validate_response_consistency(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Validate response for personality consistency and quality."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        
        agent_state.current_step = "validate_response"
        
        generated_response = state.get("generated_response", "")
        
        # Basic validation checks
        is_valid = True
        validation_issues = []
        
        # Check response length
        if len(generated_response.strip()) < 10:
            is_valid = False
            validation_issues.append("Response too short")
        
        if len(generated_response) > agent_state.max_response_length:
            is_valid = False
            validation_issues.append("Response too long")
        
        # Check personality consistency score
        if agent_state.personality_consistency_score < 0.6:
            is_valid = False
            validation_issues.append("Low personality consistency")
        
        # Check for obvious errors
        if "[error" in generated_response.lower():
            is_valid = False
            validation_issues.append("Contains error message")
        
        # Update agent state
        agent_state.content_approved = is_valid
        if validation_issues:
            agent_state.error_message = "; ".join(validation_issues)
        
        state["agent_state"] = agent_state
        state["workflow_step"] = "validate_response"
        
        logger.info(f"Response validation for {character_agent.character_name}: {'valid' if is_valid else 'invalid'}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error validating response: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def format_final_output(state: CharacterWorkflowState) -> CharacterWorkflowState:
    """Format the final output based on workflow results."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        
        agent_state.current_step = "format_output"
        
        # Create final message if response was generated and approved
        final_message = None
        character_reaction = None
        
        if (state["engagement_decision"] == AgentDecision.ENGAGE and 
            agent_state.content_approved and 
            state.get("generated_response")):
            
            # Create conversation message
            final_message = ConversationMessage(
                character_id=character_agent.character_id,
                character_name=character_agent.character_name,
                content=state["generated_response"],
                message_type=state.get("message_type", "character_reply"),
                engagement_score=agent_state.personality_consistency_score
            )
            
            # Create character reaction if this was a news response
            if state.get("news_item"):
                character_reaction = CharacterReaction(
                    character_id=character_agent.character_id,
                    character_name=character_agent.character_name,
                    news_item_id=state["news_item"].id,
                    reaction_content=state["generated_response"],
                    decision=state["engagement_decision"],
                    confidence_score=agent_state.personality_consistency_score,
                    reasoning=agent_state.decision_reasoning
                )
        
        # Mark workflow as complete
        agent_state.workflow_complete = True
        agent_state.current_step = "complete"
        
        state["agent_state"] = agent_state
        state["final_message"] = final_message
        state["character_reaction"] = character_reaction
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
    """Handle workflow errors and provide fallback response."""
    try:
        character_agent = state["character_agent"]
        agent_state = state["agent_state"]
        
        agent_state.current_step = "handle_error"
        agent_state.workflow_complete = True
        agent_state.error_count += 1
        
        # Log error details
        error_msg = state.get("error_details", "Unknown error")
        logger.error(f"Workflow error for {character_agent.character_name}: {error_msg}")
        
        state["agent_state"] = agent_state
        state["workflow_step"] = "handle_error"
        state["success"] = False
        
        return state
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
        state["error_details"] = f"Error handler failed: {str(e)}"
        return state


# Conditional routing functions

def route_after_decision(state: CharacterWorkflowState) -> str:
    """Route workflow based on engagement decision."""
    decision = state.get("engagement_decision")
    
    if not decision:
        return "error"
    
    if decision == AgentDecision.ENGAGE:
        return "engage"
    elif decision == AgentDecision.IGNORE:
        return "ignore"
    elif decision == AgentDecision.DEFER:
        return "defer"
    else:
        return "error"


def route_after_validation(state: CharacterWorkflowState) -> str:
    """Route workflow based on validation results."""
    agent_state = state.get("agent_state")
    
    if not agent_state:
        return "error"
    
    if agent_state.content_approved:
        return "valid"
    elif agent_state.error_count >= 3:  # Max retries reached
        return "error"
    else:
        return "invalid"  # Retry generation


# Workflow execution helper

async def execute_character_workflow(
    character_agent: BaseCharacterAgent,
    input_context: str,
    news_item: Optional[NewsItem] = None,
    conversation_history: Optional[List[ConversationMessage]] = None,
    target_topic: Optional[str] = None
) -> CharacterWorkflowState:
    """
    Execute the character workflow for given input.
    
    Args:
        character_agent: The character agent to execute
        input_context: Context to respond to
        news_item: Optional news item for news reactions
        conversation_history: Optional conversation history
        target_topic: Optional target topic focus
        
    Returns:
        CharacterWorkflowState: Final workflow state
    """
    workflow = create_character_workflow()
    
    # Initialize workflow state
    initial_state = CharacterWorkflowState(
        character_agent=character_agent,
        input_context=input_context,
        news_item=news_item,
        conversation_history=conversation_history,
        target_topic=target_topic,
        agent_state=create_agent_state(
            character_agent.character_id,
            character_agent.character_name
        ),
        engagement_decision=None,
        generated_response=None,
        character_reaction=None,
        final_message=None,
        workflow_step="start",
        execution_time_ms=0,
        error_details=None,
        success=False
    )
    
    # Execute workflow
    start_time = datetime.utcnow()
    
    try:
        final_state = await workflow.ainvoke(initial_state)
        
        # Calculate execution time
        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        final_state["execution_time_ms"] = execution_time_ms
        
        return final_state
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        
        # Return error state
        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        initial_state["error_details"] = str(e)
        initial_state["execution_time_ms"] = execution_time_ms
        initial_state["success"] = False
        
        return initial_state 