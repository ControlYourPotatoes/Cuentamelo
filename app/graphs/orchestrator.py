"""
Master Orchestration Workflow for Puerto Rican AI Character Platform
Coordinates multiple characters, manages news processing, and handles character interactions.
"""
from typing import Dict, List, Optional, Any, TypedDict
import asyncio
import logging
from datetime import datetime, timedelta

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.models.conversation import (
    OrchestrationState, AgentState, ConversationMessage, NewsItem, 
    CharacterReaction, ConversationThread, create_orchestration_state,
    update_conversation_activity, is_character_available
)
from app.agents.base_character import BaseCharacterAgent
from app.agents.jovani_vazquez import create_jovani_vazquez
from app.graphs.character_workflow import execute_character_workflow

logger = logging.getLogger(__name__)


class OrchestrationWorkflowState(TypedDict):
    """State for master orchestration workflow."""
    # Core state
    orchestration_state: OrchestrationState
    
    # Current processing
    current_news_item: Optional[NewsItem]
    processing_characters: List[str]
    character_agents: Dict[str, BaseCharacterAgent]
    
    # Results
    character_reactions: List[CharacterReaction]
    new_conversations: List[ConversationThread]
    system_messages: List[str]
    
    # Workflow control
    workflow_step: str
    execution_time_ms: int
    error_details: Optional[str]
    success: bool


def create_orchestration_workflow() -> StateGraph:
    """
    Create the master orchestration workflow.
    
    Workflow steps:
    1. Initialize -> Load characters and setup state
    2. Process News Queue -> Handle pending news items
    3. Character Processing -> Execute character workflows
    4. Manage Interactions -> Handle character-to-character interactions
    5. Update State -> Persist results and update system state
    6. Cleanup -> Resource cleanup and rate limiting
    """
    
    workflow = StateGraph(OrchestrationWorkflowState)
    
    # Add workflow nodes
    workflow.add_node("initialize", initialize_orchestration)
    workflow.add_node("process_news_queue", process_news_queue)
    workflow.add_node("character_processing", execute_character_processing)
    workflow.add_node("manage_interactions", manage_character_interactions)
    workflow.add_node("update_state", update_orchestration_state)
    workflow.add_node("cleanup", cleanup_and_rate_limit)
    workflow.add_node("handle_error", handle_orchestration_error)
    
    # Define workflow edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "process_news_queue")
    
    # Conditional routing based on news queue
    workflow.add_conditional_edges(
        "process_news_queue",
        route_after_news_processing,
        {
            "has_news": "character_processing",
            "no_news": "manage_interactions",
            "error": "handle_error"
        }
    )
    
    workflow.add_edge("character_processing", "manage_interactions")
    workflow.add_edge("manage_interactions", "update_state")
    workflow.add_edge("update_state", "cleanup")
    workflow.add_edge("cleanup", END)
    workflow.add_edge("handle_error", END)
    
    return workflow


# Character registry and factory functions
def get_available_characters() -> Dict[str, BaseCharacterAgent]:
    """Get all available character agents."""
    characters = {
        "jovani_vazquez": create_jovani_vazquez(),
        # TODO: Add other characters as they're implemented
        # "political_figure": create_political_figure(),
        # "ciudadano_boricua": create_ciudadano_boricua(),
        # "cultural_historian": create_cultural_historian()
    }
    return characters


# Node implementations

async def initialize_orchestration(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Initialize the orchestration system with characters and state."""
    try:
        # Load available characters
        characters = get_available_characters()
        character_ids = list(characters.keys())
        
        # Create or update orchestration state
        if "orchestration_state" not in state or not state["orchestration_state"]:
            orchestration_state = create_orchestration_state(character_ids)
        else:
            orchestration_state = state["orchestration_state"]
            orchestration_state.active_characters = character_ids
        
        # Update system status
        orchestration_state.orchestration_active = True
        orchestration_state.last_activity = datetime.utcnow()
        
        # Initialize workflow state
        state["orchestration_state"] = orchestration_state
        state["character_agents"] = characters
        state["processing_characters"] = []
        state["character_reactions"] = []
        state["new_conversations"] = []
        state["system_messages"] = []
        state["workflow_step"] = "initialize"
        state["success"] = True
        
        logger.info(f"Initialized orchestration with {len(characters)} characters")
        
        return state
        
    except Exception as e:
        logger.error(f"Error initializing orchestration: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def process_news_queue(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Process pending news items and prepare for character processing."""
    try:
        orchestration_state = state["orchestration_state"]
        
        # Check if there are pending news items
        if not orchestration_state.pending_news_queue:
            state["current_news_item"] = None
            state["workflow_step"] = "process_news_queue"
            logger.info("No pending news items to process")
            return state
        
        # Get the next news item
        current_news = orchestration_state.pending_news_queue.pop(0)
        state["current_news_item"] = current_news
        
        # Determine which characters should process this news
        processing_characters = []
        characters = state["character_agents"]
        
        for char_id, character_agent in characters.items():
            # Check if character is available
            char_state = orchestration_state.character_states.get(char_id)
            if not char_state or not is_character_available(char_state):
                continue
            
            # Check topic relevance
            if current_news.topics:
                relevance = character_agent.get_topic_relevance(current_news.topics)
                if relevance >= 0.3:  # Minimum relevance threshold
                    processing_characters.append(char_id)
            else:
                # If no topics specified, let all available characters decide
                processing_characters.append(char_id)
        
        state["processing_characters"] = processing_characters
        state["workflow_step"] = "process_news_queue"
        
        logger.info(f"Processing news: {current_news.headline[:50]}... with {len(processing_characters)} characters")
        
        return state
        
    except Exception as e:
        logger.error(f"Error processing news queue: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def execute_character_processing(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Execute character workflows for current news item."""
    try:
        current_news = state["current_news_item"]
        processing_characters = state["processing_characters"]
        character_agents = state["character_agents"]
        orchestration_state = state["orchestration_state"]
        
        if not current_news or not processing_characters:
            state["workflow_step"] = "character_processing"
            return state
        
        # Execute character workflows in parallel
        tasks = []
        for char_id in processing_characters:
            if char_id in character_agents:
                character_agent = character_agents[char_id]
                task = execute_character_workflow(
                    character_agent=character_agent,
                    input_context=f"{current_news.headline}\n{current_news.content}",
                    news_item=current_news,
                    target_topic="news_reaction"
                )
                tasks.append((char_id, task))
        
        # Wait for all character workflows to complete
        reactions = []
        for char_id, task in tasks:
            try:
                workflow_result = await task
                
                # Update character state in orchestration
                if workflow_result["success"] and workflow_result.get("agent_state"):
                    orchestration_state.character_states[char_id] = workflow_result["agent_state"]
                
                # Collect character reaction
                if workflow_result.get("character_reaction"):
                    reactions.append(workflow_result["character_reaction"])
                    
                    # Track that this character processed the news
                    if char_id not in current_news.processed_by_characters:
                        current_news.processed_by_characters.append(char_id)
                
                logger.info(f"Character {char_id} workflow completed: {workflow_result['success']}")
                
            except Exception as e:
                logger.error(f"Error in character workflow for {char_id}: {str(e)}")
                continue
        
        # Store results
        state["character_reactions"] = reactions
        state["orchestration_state"] = orchestration_state
        state["workflow_step"] = "character_processing"
        
        # Update orchestration metrics
        orchestration_state.processed_news_count += 1
        orchestration_state.character_reactions.extend(reactions)
        
        logger.info(f"Completed character processing: {len(reactions)} reactions generated")
        
        return state
        
    except Exception as e:
        logger.error(f"Error executing character processing: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def manage_character_interactions(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Manage character-to-character interactions and conversation threading."""
    try:
        reactions = state["character_reactions"]
        orchestration_state = state["orchestration_state"]
        character_agents = state["character_agents"]
        
        new_conversations = []
        
        # Create conversations from character reactions
        if len(reactions) >= 2:  # Need at least 2 characters for interaction
            
            # Group reactions by news item
            news_reactions = {}
            for reaction in reactions:
                if reaction.decision.value == "engage" and reaction.reaction_content:
                    news_id = reaction.news_item_id
                    if news_id not in news_reactions:
                        news_reactions[news_id] = []
                    news_reactions[news_id].append(reaction)
            
            # Create conversation threads for each news item with multiple reactions
            for news_id, news_reaction_list in news_reactions.items():
                if len(news_reaction_list) >= 2:
                    
                    # Create conversation thread
                    participants = [r.character_id for r in news_reaction_list]
                    
                    # Find the original news item
                    original_context = ""
                    if state.get("current_news_item") and state["current_news_item"].id == news_id:
                        original_context = state["current_news_item"].headline
                    
                    conversation = ConversationThread(
                        title=f"Reacciones a: {original_context[:50]}...",
                        original_context=original_context,
                        participants=participants,
                        topic_tags=["news_reaction"]
                    )
                    
                    # Add initial messages from reactions
                    for reaction in news_reaction_list:
                        message = ConversationMessage(
                            character_id=reaction.character_id,
                            character_name=reaction.character_name,
                            content=reaction.reaction_content,
                            message_type="news_reaction",
                            engagement_score=reaction.confidence_score
                        )
                        conversation.messages.append(message)
                    
                    conversation = update_conversation_activity(conversation)
                    new_conversations.append(conversation)
                    
                    logger.info(f"Created conversation thread with {len(participants)} participants")
        
        # Store new conversations
        state["new_conversations"] = new_conversations
        orchestration_state.active_conversations.extend(new_conversations)
        state["orchestration_state"] = orchestration_state
        state["workflow_step"] = "manage_interactions"
        
        logger.info(f"Managed interactions: {len(new_conversations)} new conversations")
        
        return state
        
    except Exception as e:
        logger.error(f"Error managing character interactions: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def update_orchestration_state(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Update the orchestration state with processing results."""
    try:
        orchestration_state = state["orchestration_state"]
        
        # Update activity timestamp
        orchestration_state.last_activity = datetime.utcnow()
        
        # Update performance metrics
        total_reactions = len(state["character_reactions"])
        successful_reactions = len([r for r in state["character_reactions"] 
                                  if r.decision.value == "engage"])
        
        orchestration_state.performance_metrics.update({
            "total_reactions": orchestration_state.performance_metrics.get("total_reactions", 0) + total_reactions,
            "successful_reactions": orchestration_state.performance_metrics.get("successful_reactions", 0) + successful_reactions,
            "conversation_threads": len(orchestration_state.active_conversations),
            "last_processing_time": datetime.utcnow().isoformat()
        })
        
        # Clean up old conversations (remove inactive ones older than 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        active_conversations = [
            conv for conv in orchestration_state.active_conversations
            if conv.is_active and conv.last_activity > cutoff_time
        ]
        orchestration_state.active_conversations = active_conversations
        
        state["orchestration_state"] = orchestration_state
        state["workflow_step"] = "update_state"
        
        logger.info(f"Updated orchestration state: {total_reactions} reactions, {len(active_conversations)} active conversations")
        
        return state
        
    except Exception as e:
        logger.error(f"Error updating orchestration state: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def cleanup_and_rate_limit(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Cleanup resources and apply rate limiting."""
    try:
        orchestration_state = state["orchestration_state"]
        
        # Rate limiting - reset hourly API call counter if needed
        now = datetime.utcnow()
        if now > orchestration_state.rate_limit_reset:
            orchestration_state.api_calls_this_hour = 0
            orchestration_state.rate_limit_reset = now + timedelta(hours=1)
        
        # Update API call count (estimate based on character processing)
        api_calls_used = len(state["processing_characters"]) * 2  # Rough estimate
        orchestration_state.api_calls_this_hour += api_calls_used
        
        # System messages for monitoring
        system_messages = []
        if orchestration_state.api_calls_this_hour > 80:  # Warning threshold
            system_messages.append("Warning: High API usage this hour")
        
        if len(orchestration_state.active_conversations) > 20:
            system_messages.append("Info: High number of active conversations")
        
        state["system_messages"] = system_messages
        state["orchestration_state"] = orchestration_state
        state["workflow_step"] = "cleanup"
        state["success"] = True
        
        logger.info(f"Cleanup completed: {api_calls_used} API calls used, {len(system_messages)} system messages")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        state["error_details"] = str(e)
        state["success"] = False
        return state


async def handle_orchestration_error(state: OrchestrationWorkflowState) -> OrchestrationWorkflowState:
    """Handle orchestration workflow errors."""
    try:
        error_msg = state.get("error_details", "Unknown orchestration error")
        logger.error(f"Orchestration workflow error: {error_msg}")
        
        # Update orchestration state error count
        if "orchestration_state" in state and state["orchestration_state"]:
            state["orchestration_state"].error_count += 1
        
        state["workflow_step"] = "handle_error"
        state["success"] = False
        
        return state
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
        state["error_details"] = f"Error handler failed: {str(e)}"
        return state


# Conditional routing functions

def route_after_news_processing(state: OrchestrationWorkflowState) -> str:
    """Route workflow based on news processing results."""
    current_news = state.get("current_news_item")
    processing_characters = state.get("processing_characters", [])
    
    if state.get("error_details"):
        return "error"
    elif current_news and processing_characters:
        return "has_news"
    else:
        return "no_news"


# Main orchestration execution function

async def execute_orchestration_cycle(
    news_items: List[NewsItem] = None,
    existing_state: Optional[OrchestrationState] = None
) -> OrchestrationWorkflowState:
    """
    Execute a complete orchestration cycle.
    
    Args:
        news_items: List of news items to process
        existing_state: Existing orchestration state to continue from
        
    Returns:
        OrchestrationWorkflowState: Final workflow state
    """
    workflow = create_orchestration_workflow()
    
    # Prepare orchestration state
    if existing_state:
        orchestration_state = existing_state
        if news_items:
            orchestration_state.pending_news_queue.extend(news_items)
    else:
        orchestration_state = create_orchestration_state(["jovani_vazquez"])
        if news_items:
            orchestration_state.pending_news_queue = news_items
    
    # Initialize workflow state
    initial_state = OrchestrationWorkflowState(
        orchestration_state=orchestration_state,
        current_news_item=None,
        processing_characters=[],
        character_agents={},
        character_reactions=[],
        new_conversations=[],
        system_messages=[],
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
        
        logger.info(f"Orchestration cycle completed in {execution_time_ms}ms")
        
        return final_state
        
    except Exception as e:
        logger.error(f"Orchestration workflow execution failed: {str(e)}")
        
        # Return error state
        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        initial_state["error_details"] = str(e)
        initial_state["execution_time_ms"] = execution_time_ms
        initial_state["success"] = False
        
        return initial_state


# Utility functions for external integration

async def add_news_item(news_item: NewsItem, orchestration_state: OrchestrationState) -> None:
    """Add a news item to the processing queue."""
    orchestration_state.pending_news_queue.append(news_item)
    logger.info(f"Added news item to queue: {news_item.headline[:50]}...")


async def get_orchestration_status(orchestration_state: OrchestrationState) -> Dict[str, Any]:
    """Get current status of the orchestration system."""
    return {
        "active": orchestration_state.orchestration_active,
        "pending_news": len(orchestration_state.pending_news_queue),
        "active_characters": len(orchestration_state.active_characters),
        "active_conversations": len(orchestration_state.active_conversations),
        "processed_news_count": orchestration_state.processed_news_count,
        "api_calls_this_hour": orchestration_state.api_calls_this_hour,
        "last_activity": orchestration_state.last_activity.isoformat(),
        "performance_metrics": orchestration_state.performance_metrics
    } 