import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.services.n8n_integration import n8n_service
from app.models.demo_scenarios import DEMO_SCENARIOS

logger = logging.getLogger(__name__)

async def simulate_character_workflow(character_id: str, news_data: Dict[str, Any], speed_multiplier: float = 1.0):
    """
    Simulate a complete character workflow for demo purposes
    
    This function simulates the entire process a character goes through:
    1. Analyzing news
    2. Making engagement decision
    3. Generating response
    4. Validating personality
    5. Publishing post
    """
    
    # Step 1: Character Analysis
    await asyncio.sleep(1 / speed_multiplier)
    await n8n_service.emit_event("character_analyzing", {
        "character_id": character_id,
        "character_name": character_id.replace("_", " ").title(),
        "news_id": news_data.get("id", "demo_news"),
        "thinking_process": [
            "Evaluating cultural relevance",
            "Checking personality alignment", 
            "Assessing engagement potential",
            "Analyzing topic fit"
        ],
        "analysis_stage": "completed",
        "processing_time": 1.0
    })
    
    # Step 2: Engagement Decision
    await asyncio.sleep(0.5 / speed_multiplier)
    decision = True  # For demo, always engage
    confidence = 0.85
    
    await n8n_service.emit_event("engagement_decision", {
        "character_id": character_id,
        "decision": decision,
        "confidence_score": confidence,
        "reasoning": f"Character {character_id} decides to engage based on cultural relevance and topic alignment",
        "cultural_context": news_data.get("cultural_context", "Puerto Rican cultural context"),
        "personality_factors": ["cultural_relevance", "topic_alignment", "engagement_potential"]
    })
    
    if not decision:
        return
    
    # Step 3: Response Generation
    await asyncio.sleep(2 / speed_multiplier)
    
    language_mix = "spanish" if character_id == "political_figure" else "spanglish"
    tone_indicators = ["professional"] if character_id == "political_figure" else ["energetic", "casual"]
    
    await n8n_service.emit_event("response_generating", {
        "character_id": character_id,
        "prompt_context": f"Generate response to: {news_data.get('title', 'News title')}",
        "generation_progress": 100,
        "language_mix": language_mix,
        "tone_indicators": tone_indicators,
        "cultural_elements": ["puerto_rico", "cultural_identity", "community"]
    })
    
    # Step 4: Personality Validation
    await asyncio.sleep(0.5 / speed_multiplier)
    
    voice_characteristics = {
        "formality": 0.8 if character_id == "political_figure" else 0.3,
        "energy": 0.9 if character_id == "jovani_vazquez" else 0.6,
        "cultural_authenticity": 0.95
    }
    
    await n8n_service.emit_event("personality_validation", {
        "character_id": character_id,
        "consistency_score": 0.95,
        "adjustments_made": [],
        "voice_characteristics": voice_characteristics,
        "cultural_authenticity": 0.95
    })
    
    # Step 5: Post Publication
    await asyncio.sleep(1 / speed_multiplier)
    
    sample_content = f"Demo response from {character_id} about {news_data.get('title', 'news')} #PuertoRico #Boricua"
    
    await n8n_service.emit_event("post_published", {
        "character_id": character_id,
        "content": sample_content,
        "tweet_url": f"https://twitter.com/CuentameloAgent/status/demo_{character_id}_{datetime.utcnow().timestamp()}",
        "character_voice_sample": sample_content,
        "cultural_elements_used": ["#PuertoRico", "#Boricua"],
        "post_metrics": {
            "character_count": len(sample_content),
            "hashtag_count": 2,
            "mention_count": 0
        }
    })

async def simulate_multi_character_conversation(scenario_id: str, speed_multiplier: float = 1.0):
    """
    Simulate a multi-character conversation for a given scenario
    """
    if scenario_id not in DEMO_SCENARIOS:
        logger.error(f"Scenario {scenario_id} not found")
        return
    
    scenario = DEMO_SCENARIOS[scenario_id]
    characters = scenario.expected_characters
    
    if len(characters) < 2:
        return
    
    # Simulate conversation threading
    await asyncio.sleep(1 / speed_multiplier)
    
    await n8n_service.emit_event("conversation_threading", {
        "thread_id": f"demo_thread_{scenario_id}",
        "participants": characters,
        "turn_count": len(characters),
        "topic_evolution": scenario.topics,
        "cultural_dynamics": scenario.cultural_context,
        "engagement_level": 0.85
    })
    
    # Simulate character interactions
    for i, responder in enumerate(characters[1:], 1):
        await asyncio.sleep(1 / speed_multiplier)
        
        original_poster = characters[i-1]
        interaction_type = "agreement" if i % 2 == 0 else "addition"
        
        await n8n_service.emit_event("interaction_triggered", {
            "responder": responder,
            "original_poster": original_poster,
            "interaction_type": interaction_type,
            "conversation_context": f"Response to {original_poster}'s post about {scenario.title}",
            "relationship_dynamic": "supportive"
        })

def get_cultural_elements_for_character(character_id: str) -> List[str]:
    """
    Get cultural elements specific to a character
    """
    cultural_elements = {
        "jovani_vazquez": [
            "youth_culture", "entertainment", "social_media", "spanglish",
            "wepa", "brutal", "chévere", "#PuertoRico", "#Boricua"
        ],
        "political_figure": [
            "government", "policy", "formal_spanish", "professional",
            "comunidad", "trabajo", "desarrollo", "#PR", "#SanJuan"
        ],
        "ciudadano_boricua": [
            "daily_life", "practical_concerns", "casual_spanish", "community",
            "bregar", "janguiar", "guagua", "#IslaDelEncanto"
        ],
        "cultural_historian": [
            "heritage", "tradition", "education", "formal_spanish",
            "historia", "cultura", "tradición", "#PuertoRico", "#Cultura"
        ]
    }
    
    return cultural_elements.get(character_id, ["puerto_rico", "cultural_identity"])

def get_character_voice_characteristics(character_id: str) -> Dict[str, float]:
    """
    Get voice characteristics for a character
    """
    characteristics = {
        "jovani_vazquez": {
            "formality": 0.2,
            "energy": 0.95,
            "cultural_authenticity": 0.9,
            "spanglish_usage": 0.8,
            "emoji_usage": 0.9
        },
        "political_figure": {
            "formality": 0.9,
            "energy": 0.4,
            "cultural_authenticity": 0.85,
            "spanglish_usage": 0.1,
            "emoji_usage": 0.2
        },
        "ciudadano_boricua": {
            "formality": 0.3,
            "energy": 0.6,
            "cultural_authenticity": 0.95,
            "spanglish_usage": 0.4,
            "emoji_usage": 0.5
        },
        "cultural_historian": {
            "formality": 0.7,
            "energy": 0.5,
            "cultural_authenticity": 0.95,
            "spanglish_usage": 0.2,
            "emoji_usage": 0.3
        }
    }
    
    return characteristics.get(character_id, {
        "formality": 0.5,
        "energy": 0.5,
        "cultural_authenticity": 0.8,
        "spanglish_usage": 0.3,
        "emoji_usage": 0.4
    })

async def create_demo_news_event(title: str, content: str, topics: List[str], urgency_score: float = 0.7):
    """
    Create a demo news discovery event
    """
    await n8n_service.emit_event("news_discovered", {
        "title": title,
        "source": "Demo News Source",
        "topics": topics,
        "urgency_score": urgency_score,
        "cultural_relevance": 0.8,
        "content_preview": content[:100] + "..." if len(content) > 100 else content
    })

def validate_demo_scenario(scenario_id: str) -> bool:
    """
    Validate that a demo scenario exists and is properly configured
    """
    if scenario_id not in DEMO_SCENARIOS:
        return False
    
    scenario = DEMO_SCENARIOS[scenario_id]
    
    # Check required fields
    required_fields = ["id", "title", "content", "topics", "expected_characters"]
    for field in required_fields:
        if not hasattr(scenario, field) or not getattr(scenario, field):
            return False
    
    # Check that expected characters have engagement predictions
    for character in scenario.expected_characters:
        if character not in scenario.engagement_predictions:
            return False
    
    return True 