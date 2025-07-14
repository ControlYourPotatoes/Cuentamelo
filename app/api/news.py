"""
News API endpoints for receiving and processing news items.
Provides endpoints for news ingestion and character reaction orchestration.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timezone

from app.models.conversation import NewsItem
from app.agents.agent_factory import create_agent
from app.graphs.character_workflow import execute_character_workflow
from app.services.dependency_container import get_container
from app.ports.news_provider import TrendingTopic, NewsProviderInfo
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class NewsInput(BaseModel):
    """Input model for news ingestion."""
    headline: str
    content: str
    source: str
    url: Optional[str] = None
    published_at: Optional[str] = None
    relevance_score: Optional[float] = 0.8
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class NewsResponse(BaseModel):
    """Response model for news processing."""
    news_id: str
    headline: str
    characters_engaged: int
    total_characters: int
    processing_time_ms: int
    status: str
    character_responses: List[dict]


class NewsProcessingRequest(BaseModel):
    """Request model for processing news with specific characters."""
    news_input: NewsInput
    character_ids: Optional[List[str]] = None  # If None, process with all available characters
    target_topic: Optional[str] = None
    force_engagement: bool = False  # Bypass cooldown/availability checks


@router.post("/ingest", response_model=NewsResponse)
async def ingest_news(
    news_input: NewsInput,
    background_tasks: BackgroundTasks
):
    """
    Ingest a news item and trigger character reactions.
    
    This endpoint receives news and automatically processes it through
    the character workflow system to generate AI responses.
    """
    try:
        start_time = datetime.now(timezone.utc)
        
        # Create news item
        news_item = NewsItem(
            id=f"news_{datetime.now(timezone.utc).timestamp()}",
            headline=news_input.headline,
            content=news_input.content,
            source=news_input.source,
            url=news_input.url,
            published_at=news_input.published_at or datetime.now(timezone.utc).isoformat(),
            relevance_score=news_input.relevance_score or 0.8
        )
        
        # Get available characters
        available_characters = ["jovani_vazquez"]  # Currently only Jovani is configured
        
        # Process news with characters in background
        background_tasks.add_task(
            process_news_with_characters,
            news_item,
            available_characters,
            news_input.target_topic
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return NewsResponse(
            news_id=news_item.id,
            headline=news_item.headline,
            characters_engaged=0,  # Will be updated in background
            total_characters=len(available_characters),
            processing_time_ms=int(processing_time),
            status="processing",
            character_responses=[]
        )
        
    except Exception as e:
        logger.error(f"Error ingesting news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing news: {str(e)}")


@router.post("/process", response_model=NewsResponse)
async def process_news(
    request: NewsProcessingRequest
):
    """
    Process news with specific characters and return immediate responses.
    
    This endpoint processes news synchronously and returns character responses
    immediately, useful for testing and immediate feedback.
    """
    try:
        start_time = datetime.now(timezone.utc)
        
        # Create news item
        news_item = NewsItem(
            id=f"news_{datetime.now(timezone.utc).timestamp()}",
            headline=request.news_input.headline,
            content=request.news_input.content,
            source=request.news_input.source,
            url=request.news_input.url,
            published_at=request.news_input.published_at or datetime.now(timezone.utc).isoformat(),
            relevance_score=request.news_input.relevance_score or 0.8
        )
        
        # Get characters to process with
        if request.character_ids:
            character_ids = request.character_ids
        else:
            character_ids = ["jovani_vazquez"]  # Default to available characters
        
        # Process with each character
        character_responses = []
        successful_engagements = 0
        
        for character_id in character_ids:
            try:
                # Create agent
                agent = create_agent(character_id)
                if not agent:
                    logger.warning(f"Failed to create agent for {character_id}")
                    continue
                
                # Execute workflow
                result = await execute_character_workflow(
                    character_agent=agent,
                    input_context=request.news_input.content,
                    news_item=news_item,
                    target_topic=request.news_input.target_topic
                )
                
                if result["success"]:
                    response_data = {
                        "character_id": character_id,
                        "character_name": agent.character_name,
                        "engagement_decision": str(result.get("engagement_decision", "unknown")),
                        "generated_response": result.get("generated_response", ""),
                        "confidence_score": result.get("agent_state", {}).get("decision_confidence", 0.0),
                        "processing_time_ms": result.get("execution_time_ms", 0)
                    }
                    
                    character_responses.append(response_data)
                    
                    if result.get("generated_response"):
                        successful_engagements += 1
                        
            except Exception as e:
                logger.error(f"Error processing {character_id}: {str(e)}")
                character_responses.append({
                    "character_id": character_id,
                    "character_name": "Unknown",
                    "engagement_decision": "error",
                    "generated_response": f"Error: {str(e)}",
                    "confidence_score": 0.0,
                    "processing_time_ms": 0
                })
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return NewsResponse(
            news_id=news_item.id,
            headline=news_item.headline,
            characters_engaged=successful_engagements,
            total_characters=len(character_ids),
            processing_time_ms=int(processing_time),
            status="completed",
            character_responses=character_responses
        )
        
    except Exception as e:
        logger.error(f"Error processing news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing news: {str(e)}")


@router.get("/discover")
async def discover_news(
    max_results: int = 10,
    categories: Optional[List[str]] = None,
    min_relevance_score: float = 0.3
):
    """
    Discover latest news from the configured news provider.
    
    This endpoint fetches news from the configured news source
    and returns the most relevant items for character engagement.
    """
    try:
        # Get news provider from dependency container
        container = get_container()
        news_provider = container.get_news_provider()
        
        # Discover latest news
        news_items = await news_provider.discover_latest_news(
            max_results=max_results,
            categories=categories,
            min_relevance_score=min_relevance_score
        )
        
        return {
            "news_items": [
                {
                    "id": item.id,
                    "headline": item.headline,
                    "content": item.content,
                    "source": item.source,
                    "url": item.url,
                    "published_at": item.published_at,
                    "relevance_score": item.relevance_score
                }
                for item in news_items
            ],
            "total_discovered": len(news_items),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error discovering news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error discovering news: {str(e)}")


@router.get("/trending")
async def get_trending_news(max_topics: int = 10):
    """
    Get trending news topics that characters might be interested in.
    
    This endpoint fetches trending topics from the configured news provider
    for character engagement.
    """
    try:
        # Get news provider from dependency container
        container = get_container()
        news_provider = container.get_news_provider()
        
        # Get trending topics
        trending_topics = await news_provider.get_trending_topics(max_topics=max_topics)
        
        return {
            "trending_topics": [
                {
                    "term": topic.term,
                    "count": topic.count,
                    "relevance": topic.relevance,
                    "category": topic.category,
                    "metadata": topic.metadata
                }
                for topic in trending_topics
            ],
            "total_topics": len(trending_topics),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting trending topics: {str(e)}")


@router.get("/health")
async def news_health_check():
    """Health check for news processing system."""
    try:
        # Get news provider from dependency container
        container = get_container()
        news_provider = container.get_news_provider()
        
        # Test news provider health
        news_healthy = await news_provider.health_check()
        if not news_healthy:
            raise Exception("News provider health check failed")
        
        # Get provider info
        provider_info = await news_provider.get_provider_info()
        
        # Test character creation
        agent = create_agent("jovani_vazquez")
        if not agent:
            raise Exception("Failed to create test agent")
        
        return {
            "status": "healthy",
            "message": "News processing system is operational",
            "news_provider": {
                "name": provider_info.name,
                "type": provider_info.type,
                "capabilities": provider_info.capabilities
            },
            "available_characters": ["jovani_vazquez"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"News health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"News system unhealthy: {str(e)}")


async def process_news_with_characters(
    news_item: NewsItem,
    character_ids: List[str],
    target_topic: Optional[str] = None
):
    """
    Background task to process news with multiple characters.
    
    This function runs in the background to avoid blocking the API response.
    """
    try:
        logger.info(f"Processing news '{news_item.headline}' with {len(character_ids)} characters")
        
        for character_id in character_ids:
            try:
                agent = create_agent(character_id)
                if not agent:
                    continue
                
                result = await execute_character_workflow(
                    character_agent=agent,
                    input_context=news_item.content,
                    news_item=news_item,
                    target_topic=target_topic
                )
                
                if result["success"] and result.get("generated_response"):
                    logger.info(f"{agent.character_name} responded to news: {result['generated_response'][:100]}...")
                    
                    # TODO: Post to Twitter if configured
                    # TODO: Store response in database
                    
            except Exception as e:
                logger.error(f"Error processing news with {character_id}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in background news processing: {str(e)}") 