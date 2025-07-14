import asyncio
import functools
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List
from app.services.n8n_integration import N8NWebhookService

logger = logging.getLogger(__name__)

def emit_n8n_event(event_type: str, data_extractor: Optional[Callable] = None):
    """
    Decorator to emit N8N events from existing functions without modifying core logic

    Args:
        event_type: Type of event from N8N_EVENTS
        data_extractor: Optional function to extract relevant data from function args/result
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                # Execute original function
                result = await func(*args, **kwargs)
                
                # Extract event data
                if data_extractor:
                    event_data = data_extractor(args, kwargs, result)
                else:
                    event_data = _default_data_extractor(func.__name__, args, kwargs, result, start_time)

                # Emit to N8N (non-blocking)
                asyncio.create_task(
                    N8NWebhookService.emit_event(event_type, event_data)
                )

                return result
                
            except Exception as e:
                # Log error but don't break the main function
                logger.error(f"Error in N8N event emission for {func.__name__}: {e}")
                # Still execute original function
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                # For sync functions, just add to event queue
                result = func(*args, **kwargs)

                if data_extractor:
                    event_data = data_extractor(args, kwargs, result)
                else:
                    event_data = _default_data_extractor(func.__name__, args, kwargs, result, start_time)

                # Queue event for async processing
                N8NWebhookService.queue_event(event_type, event_data)

                return result
                
            except Exception as e:
                # Log error but don't break the main function
                logger.error(f"Error in N8N event emission for {func.__name__}: {e}")
                # Still execute original function
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator

def _default_data_extractor(func_name: str, args: tuple, kwargs: dict, result: Any, start_time: datetime) -> Dict:
    """Default data extraction for events"""
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "function": func_name,
        "timestamp": start_time.isoformat(),
        "processing_time": processing_time,
        "args_count": len(args),
        "kwargs_keys": list(kwargs.keys()),
        "result_type": type(result).__name__,
        "success": True
    }

def extract_character_data(character_field: str = "self"):
    """
    Factory function to create data extractors for character-related events
    
    Args:
        character_field: Name of the character parameter (usually "self" for methods)
    """
    def extractor(args, kwargs, result):
        # Try to get character from args (usually self)
        character = None
        if args and hasattr(args[0], 'character_id'):
            character = args[0]
        
        if not character:
            return _default_data_extractor("unknown", args, kwargs, result, datetime.utcnow())
        
        return {
            "character_id": getattr(character, 'character_id', 'unknown'),
            "character_name": getattr(character, 'name', 'unknown'),
            "function": "character_operation",
            "timestamp": datetime.utcnow().isoformat(),
            "result_type": type(result).__name__,
            "success": True
        }
    
    return extractor

def extract_news_data():
    """Factory function to create data extractors for news-related events"""
    def extractor(args, kwargs, result):
        # Look for news data in args or kwargs
        news_data = None
        for arg in args:
            if isinstance(arg, dict) and 'title' in arg:
                news_data = arg
                break
        
        if not news_data:
            for value in kwargs.values():
                if isinstance(value, dict) and 'title' in value:
                    news_data = value
                    break
        
        if not news_data:
            return _default_data_extractor("news_operation", args, kwargs, result, datetime.utcnow())
        
        return {
            "title": news_data.get('title', 'Unknown'),
            "source": news_data.get('source', 'Unknown'),
            "topics": news_data.get('topics', []),
            "urgency_score": news_data.get('urgency_score', 0.0),
            "cultural_relevance": news_data.get('cultural_relevance', 0.0),
            "content_preview": news_data.get('content', '')[:100] + "..." if len(news_data.get('content', '')) > 100 else news_data.get('content', ''),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return extractor

def extract_twitter_data():
    """Factory function to create data extractors for Twitter-related events"""
    def extractor(args, kwargs, result):
        # Extract Twitter posting data
        content = kwargs.get('content', '')
        character_id = kwargs.get('character_id', 'unknown')
        
        return {
            "character_id": character_id,
            "content": content,
            "tweet_url": result.get('tweet_url', '') if isinstance(result, dict) else '',
            "character_voice_sample": content[:100] + "..." if len(content) > 100 else content,
            "cultural_elements_used": _extract_cultural_elements(content),
            "post_metrics": {
                "character_count": len(content),
                "hashtag_count": content.count("#"),
                "mention_count": content.count("@")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return extractor

def _extract_cultural_elements(content: str) -> List[str]:
    """Extract cultural elements from content"""
    cultural_elements = []
    
    # Puerto Rican expressions
    pr_expressions = [
        "wepa", "brutal", "chévere", "bregar", "janguiar", "parquear",
        "guagua", "zafacón", "chinchorro", "jíbaro", "boricua"
    ]
    
    # Puerto Rican hashtags
    pr_hashtags = [
        "#PuertoRico", "#Boricua", "#PR", "#SanJuan", "#IslaDelEncanto"
    ]
    
    content_lower = content.lower()
    
    for expression in pr_expressions:
        if expression in content_lower:
            cultural_elements.append(expression)
    
    for hashtag in pr_hashtags:
        if hashtag in content:
            cultural_elements.append(hashtag)
    
    return cultural_elements

# Convenience decorators for common event types
def emit_news_discovered():
    """Decorator for news discovery events"""
    return emit_n8n_event("news_discovered", extract_news_data())

def emit_character_analyzing():
    """Decorator for character analysis events"""
    return emit_n8n_event("character_analyzing", extract_character_data())

def emit_engagement_decision():
    """Decorator for engagement decision events"""
    return emit_n8n_event("engagement_decision", extract_character_data())

def emit_response_generating():
    """Decorator for response generation events"""
    return emit_n8n_event("response_generating", extract_character_data())

def emit_post_published():
    """Decorator for Twitter posting events"""
    return emit_n8n_event("post_published", extract_twitter_data()) 