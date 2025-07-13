# N8N Visual Demonstration Layer - Implementation Plan

## Overview

**Objective**: Add N8N as a visual demonstration layer that shows AI agent orchestration happening in our Python LangGraph system in real-time, creating a powerful dual demo with visual workflows for stakeholders and technical depth for engineers.

**Implementation Strategy**: Non-invasive integration that enhances existing system without breaking core functionality.

## Architecture Integration

### Current System (Unchanged)

```
Python LangGraph Core System:
├── Character Agents (Jovani, Politician, Ciudadano, Historian)
├── News Monitor Agent
├── Interaction Manager
├── Twitter Connector
└── FastAPI API Layer
```

### N8N Integration Points

```
┌─────────────────────────────────────────────┐
│                N8N WORKFLOWS                │
│   ┌─────────────┐  ┌─────────────┐         │
│   │ News Flow   │  │ Character   │         │
│   │ Monitoring  │  │ Interaction │         │
│   └─────────────┘  └─────────────┘         │
│   ┌─────────────┐  ┌─────────────┐         │
│   │ Response    │  │ Analytics   │         │
│   │ Generation  │  │ Dashboard   │         │
│   └─────────────┘  └─────────────┘         │
└─────────────────┬───────────────────────────┘
                  │ Webhook Events (Real-time)
┌─────────────────▼───────────────────────────┐
│       EXISTING PYTHON LANGGRAPH             │
│    ├── Event Decorators (New)               │
│    ├── Webhook Service (New)                │
│    ├── Demo Controllers (New)               │
│    └── Core Logic (Unchanged)               │
└─────────────────────────────────────────────┘
```

## Implementation Components

### 1. Event System Architecture

#### Event Types for N8N Visualization

```python
N8N_EVENTS = {
    "news_discovered": {
        "description": "📰 New Puerto Rican news detected",
        "data": {
            "title": str,
            "source": str,
            "topics": List[str],
            "urgency_score": float,
            "cultural_relevance": float,
            "timestamp": datetime
        },
        "n8n_node": "news_monitor",
        "visual_style": "success"
    },
    "character_analyzing": {
        "description": "🤖 Character evaluating relevance",
        "data": {
            "character_id": str,
            "character_name": str,
            "news_id": str,
            "thinking_process": List[str],
            "analysis_stage": str,
            "processing_time": float
        },
        "n8n_node": "character_analysis",
        "visual_style": "processing"
    },
    "engagement_decision": {
        "description": "🎯 Character decides to respond",
        "data": {
            "character_id": str,
            "decision": bool,
            "confidence_score": float,
            "reasoning": str,
            "cultural_context": str,
            "personality_factors": List[str]
        },
        "n8n_node": "decision_engine",
        "visual_style": "decision"
    },
    "response_generating": {
        "description": "✍️ AI generating character response",
        "data": {
            "character_id": str,
            "prompt_context": str,
            "generation_progress": int,
            "language_mix": str,  # "spanish", "english", "spanglish"
            "tone_indicators": List[str],
            "cultural_elements": List[str]
        },
        "n8n_node": "ai_generation",
        "visual_style": "active"
    },
    "personality_validation": {
        "description": "🎭 Checking response matches character voice",
        "data": {
            "character_id": str,
            "consistency_score": float,
            "adjustments_made": List[str],
            "voice_characteristics": Dict[str, float],
            "cultural_authenticity": float
        },
        "n8n_node": "personality_check",
        "visual_style": "validation"
    },
    "interaction_triggered": {
        "description": "💬 Character replying to another character",
        "data": {
            "responder": str,
            "original_poster": str,
            "interaction_type": str,  # "agreement", "debate", "addition", "question"
            "conversation_context": str,
            "relationship_dynamic": str
        },
        "n8n_node": "character_interaction",
        "visual_style": "interaction"
    },
    "post_published": {
        "description": "🐦 Live post to Twitter",
        "data": {
            "character_id": str,
            "content": str,
            "tweet_url": str,
            "character_voice_sample": str,
            "cultural_elements_used": List[str],
            "post_metrics": Dict[str, int]
        },
        "n8n_node": "social_publish",
        "visual_style": "success"
    },
    "conversation_threading": {
        "description": "🧵 Managing multi-character conversation",
        "data": {
            "thread_id": str,
            "participants": List[str],
            "turn_count": int,
            "topic_evolution": List[str],
            "cultural_dynamics": str,
            "engagement_level": float
        },
        "n8n_node": "thread_manager",
        "visual_style": "flow"
    }
}
```

### 2. Demo Scenarios for Live Demonstration

```python
DEMO_SCENARIOS = {
    "political_announcement": {
        "title": "Gobernador anuncia nueva inversión en infraestructura",
        "content": "El gobierno destinará $100 millones para mejorar las carreteras del área metropolitana, priorizando las arterias principales que conectan San Juan con Bayamón y Carolina.",
        "topics": ["gobierno", "infraestructura", "economia", "transporte"],
        "expected_characters": ["political_figure", "ciudadano_boricua", "jovani_vazquez"],
        "cultural_context": "Infrastructure is a daily concern for Puerto Ricans due to traffic and road conditions",
        "engagement_predictions": {
            "political_figure": {"probability": 0.95, "tone": "official_support"},
            "ciudadano_boricua": {"probability": 0.85, "tone": "cautious_optimism"},
            "jovani_vazquez": {"probability": 0.70, "tone": "energetic_commentary"}
        },
        "demo_talking_points": [
            "Watch how each character's personality affects their response",
            "Political figure responds professionally in Spanish",
            "Ciudadano shows skepticism based on past experiences",
            "Jovani adds entertainment value with Spanglish commentary"
        ]
    },
    "cultural_festival": {
        "title": "Festival de música puertorriqueña atrae miles de visitantes",
        "content": "El Festival Nacional de Salsa y Merengue en el Coliseo de Puerto Rico presenta artistas locales e internacionales, con presentaciones especiales de Roberto Roena y La Sonora Ponceña.",
        "topics": ["cultura", "musica", "turismo", "arte", "tradicion"],
        "expected_characters": ["jovani_vazquez", "cultural_historian", "ciudadano_boricua"],
        "cultural_context": "Music festivals are central to Puerto Rican cultural identity and community gathering",
        "engagement_predictions": {
            "jovani_vazquez": {"probability": 0.90, "tone": "excited_promotion"},
            "cultural_historian": {"probability": 0.85, "tone": "educational_context"},
            "ciudadano_boricua": {"probability": 0.75, "tone": "proud_celebration"}
        },
        "demo_talking_points": [
            "Cultural historian provides historical context",
            "Jovani promotes the event with enthusiasm",
            "Regular citizen expresses cultural pride",
            "Character interactions create natural conversation"
        ]
    },
    "economic_development": {
        "title": "Nuevo hub tecnológico se inaugura en San Juan",
        "content": "El nuevo Centro de Innovación Tecnológica abrirá sus puertas en Santurce, ofreciendo espacios para startups locales, programas de mentoría y acceso a capital de inversión internacional.",
        "topics": ["tecnologia", "emprendimiento", "san_juan", "economia", "innovacion"],
        "expected_characters": ["jovani_vazquez", "political_figure"],
        "cultural_context": "Technology sector represents hope for economic diversification and youth opportunities",
        "engagement_predictions": {
            "jovani_vazquez": {"probability": 0.80, "tone": "opportunity_excitement"},
            "political_figure": {"probability": 0.90, "tone": "economic_vision"}
        },
        "demo_talking_points": [
            "Shows different perspectives on economic development",
            "Political figure emphasizes policy impact",
            "Jovani focuses on opportunities for young people",
            "Demonstrates AI understanding of Puerto Rican economic context"
        ]
    },
    "emergency_response": {
        "title": "Servicio Nacional de Meteorología emite alerta de tormenta tropical",
        "content": "Se aproxima un sistema tropical que podría afectar el este de Puerto Rico en las próximas 48 horas. Autoridades recomiendan preparativos y revisión de planes de emergencia.",
        "topics": ["emergencia", "clima", "seguridad", "preparacion"],
        "expected_characters": ["political_figure", "ciudadano_boricua"],
        "cultural_context": "Hurricane/storm preparedness is critical cultural knowledge in Puerto Rico",
        "engagement_predictions": {
            "political_figure": {"probability": 0.95, "tone": "official_guidance"},
            "ciudadano_boricua": {"probability": 0.90, "tone": "practical_preparation"}
        },
        "demo_talking_points": [
            "Shows AI understanding of emergency protocols",
            "Characters provide different types of helpful information",
            "Demonstrates cultural knowledge of hurricane preparedness",
            "Highlights practical AI application for community safety"
        ]
    }
}
```

### 3. File Structure Updates

#### New Files to Create

```
app/
├── services/
│   ├── n8n_integration.py          # Webhook service and event management
│   └── demo_orchestrator.py        # Demo scenario management
├── api/
│   ├── demo.py                     # Demo control endpoints
│   └── webhooks.py                 # N8N webhook receivers
├── models/
│   ├── demo_scenarios.py           # Demo scenario data models
│   └── n8n_events.py              # Event schema definitions
├── utils/
│   ├── event_decorators.py         # Event emission decorators
│   └── demo_helpers.py             # Demo utility functions
└── config/
    └── n8n_settings.py             # N8N-specific configuration
```

#### Files to Modify

```
Existing Files - Add N8N Integration:
├── app/agents/base_character.py    # Add event decorators
├── app/agents/orchestrator.py      # Add workflow event tracking
├── app/tools/twitter_connector.py  # Add posting event notifications
├── app/main.py                     # Include demo routes
├── app/config.py                   # Add N8N environment variables
└── requirements.txt                # Add N8N webhook dependencies
```

## Implementation Details

### 1. Event Decorator System

**File**: `app/utils/event_decorators.py`

```python
import asyncio
import functools
import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.services.n8n_integration import N8NWebhookService

def emit_n8n_event(event_type: str, data_extractor: Optional[callable] = None):
    """
    Decorator to emit N8N events from existing functions without modifying core logic

    Args:
        event_type: Type of event from N8N_EVENTS
        data_extractor: Optional function to extract relevant data from function args/result
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Execute original function
            result = await func(*args, **kwargs)

            # Extract event data
            if data_extractor:
                event_data = data_extractor(args, kwargs, result)
            else:
                event_data = _default_data_extractor(func.__name__, args, kwargs, result)

            # Emit to N8N (non-blocking)
            asyncio.create_task(
                N8NWebhookService.emit_event(event_type, event_data)
            )

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just add to event queue
            result = func(*args, **kwargs)

            if data_extractor:
                event_data = data_extractor(args, kwargs, result)
            else:
                event_data = _default_data_extractor(func.__name__, args, kwargs, result)

            # Queue event for async processing
            N8NWebhookService.queue_event(event_type, event_data)

            return result

        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator

def _default_data_extractor(func_name: str, args: tuple, kwargs: dict, result: Any) -> Dict:
    """Default data extraction for events"""
    return {
        "function": func_name,
        "timestamp": datetime.utcnow().isoformat(),
        "args_count": len(args),
        "kwargs_keys": list(kwargs.keys()),
        "result_type": type(result).__name__
    }
```

### 2. N8N Webhook Service

**File**: `app/services/n8n_integration.py`

```python
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from queue import Queue
import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)

class N8NWebhookService:
    """Service for sending real-time events to N8N workflows"""

    def __init__(self):
        self.n8n_webhook_url = settings.N8N_WEBHOOK_URL
        self.demo_mode = settings.DEMO_MODE_ENABLED
        self.event_queue = Queue()
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)  # 5 second timeout
            )

    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Send event to N8N webhook

        Args:
            event_type: Event type from N8N_EVENTS
            data: Event data dictionary

        Returns:
            bool: True if successful, False if failed (non-blocking)
        """
        if not self.demo_mode or not self.n8n_webhook_url:
            return True  # Silent success when demo mode disabled

        try:
            await self.initialize()

            payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "source": "cuentamelo_langgraph",
                "demo_session_id": settings.DEMO_SESSION_ID
            }

            async with self.session.post(
                f"{self.n8n_webhook_url}/webhook/cuentamelo-event",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info(f"N8N event sent: {event_type}")
                    return True
                else:
                    logger.warning(f"N8N webhook failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"N8N webhook error: {e}")
            return False  # Fail gracefully without breaking main flow

    def queue_event(self, event_type: str, data: Dict[str, Any]):
        """Queue event for async processing (for sync functions)"""
        if self.demo_mode:
            self.event_queue.put({
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

    async def process_queued_events(self):
        """Process events from sync function queue"""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                await self.emit_event(event["event_type"], event["data"])
            except Exception as e:
                logger.error(f"Error processing queued event: {e}")

    async def cleanup(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()

# Global instance
n8n_service = N8NWebhookService()

# Convenience function for direct use
async def emit_event(event_type: str, data: Dict[str, Any]) -> bool:
    """Convenience function to emit events"""
    return await n8n_service.emit_event(event_type, data)
```

### 3. Demo Control API

**File**: `app/api/demo.py`

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from app.models.demo_scenarios import DemoScenario, DemoTriggerRequest
from app.services.demo_orchestrator import DemoOrchestrator
from app.services.n8n_integration import n8n_service

router = APIRouter(prefix="/demo", tags=["N8N Demo"])

demo_orchestrator = DemoOrchestrator()

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def get_demo_scenarios():
    """Get all available demo scenarios"""
    return demo_orchestrator.get_available_scenarios()

@router.post("/trigger-scenario")
async def trigger_demo_scenario(
    request: DemoTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a demo scenario for N8N visualization

    This will simulate news discovery and character responses
    """
    try:
        # Start demo scenario in background
        background_tasks.add_task(
            demo_orchestrator.run_scenario,
            request.scenario_id,
            request.speed_multiplier
        )

        # Immediately notify N8N that demo is starting
        await n8n_service.emit_event("demo_started", {
            "scenario_id": request.scenario_id,
            "scenario_title": demo_orchestrator.get_scenario_title(request.scenario_id),
            "expected_duration": demo_orchestrator.get_estimated_duration(request.scenario_id),
            "speed_multiplier": request.speed_multiplier
        })

        return {
            "status": "success",
            "message": f"Demo scenario '{request.scenario_id}' started",
            "scenario": demo_orchestrator.get_scenario_info(request.scenario_id)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/emergency-stop")
async def emergency_stop():
    """Stop all running demo scenarios"""
    try:
        demo_orchestrator.stop_all_scenarios()
        await n8n_service.emit_event("demo_stopped", {
            "reason": "emergency_stop",
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"status": "success", "message": "All demo scenarios stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_demo_status():
    """Get current demo status and running scenarios"""
    return {
        "demo_mode_enabled": n8n_service.demo_mode,
        "n8n_connected": await demo_orchestrator.check_n8n_connection(),
        "running_scenarios": demo_orchestrator.get_running_scenarios(),
        "total_events_sent": demo_orchestrator.get_event_count()
    }

@router.post("/custom-news")
async def trigger_custom_news(
    title: str,
    content: str,
    topics: List[str],
    background_tasks: BackgroundTasks
):
    """Trigger custom news for real-time demonstration"""
    try:
        background_tasks.add_task(
            demo_orchestrator.process_custom_news,
            title, content, topics
        )

        return {
            "status": "success",
            "message": "Custom news injected into system",
            "preview": {"title": title, "topics": topics}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 4. Integration Points in Existing Code

#### Character Agent Integration

**File**: `app/agents/base_character.py` (Add to existing methods)

```python
from app.utils.event_decorators import emit_n8n_event

class BaseCharacter:
    # ... existing code ...

    @emit_n8n_event("character_analyzing")
    async def should_engage(self, content: Dict[str, Any]) -> bool:
        """Existing logic with N8N event emission"""
        # ... existing engagement logic ...

        # Event data will be automatically extracted
        return engagement_decision

    @emit_n8n_event("engagement_decision")
    async def make_engagement_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Existing decision logic with enhanced event data"""
        decision_data = {
            "character_id": self.character_id,
            "character_name": self.name,
            "decision": analysis["should_engage"],
            "confidence_score": analysis["confidence"],
            "reasoning": analysis["reasoning"],
            "cultural_context": analysis.get("cultural_relevance", ""),
            "personality_factors": analysis.get("personality_alignment", [])
        }

        # ... existing logic ...
        return decision_data

    @emit_n8n_event("response_generating")
    async def generate_response(self, context: Dict[str, Any]) -> str:
        """Existing response generation with progress tracking"""

        # Enhanced event data for N8N visualization
        generation_data = {
            "character_id": self.character_id,
            "prompt_context": context.get("prompt_preview", ""),
            "generation_progress": 0,
            "language_mix": self.language_preference,
            "tone_indicators": self.personality_traits,
            "cultural_elements": context.get("cultural_references", [])
        }

        # ... existing generation logic ...

        return response
```

#### Twitter Connector Integration

**File**: `app/tools/twitter_connector.py` (Add to posting method)

```python
from app.utils.event_decorators import emit_n8n_event

class TwitterConnector:
    # ... existing code ...

    @emit_n8n_event("post_published")
    async def post_tweet(self, content: str, character_id: str) -> Dict[str, Any]:
        """Existing Twitter posting with N8N notification"""

        # ... existing posting logic ...

        # Enhanced event data for N8N
        post_data = {
            "character_id": character_id,
            "content": content,
            "tweet_url": f"https://twitter.com/user/status/{tweet_id}",
            "character_voice_sample": content[:100] + "...",
            "cultural_elements_used": self._extract_cultural_elements(content),
            "post_metrics": {
                "character_count": len(content),
                "hashtag_count": content.count("#"),
                "mention_count": content.count("@")
            }
        }

        return post_data
```

### 5. Environment Configuration Updates

**File**: `app/config.py` (Add N8N settings)

```python
# ... existing configuration ...

# N8N Integration Settings
N8N_WEBHOOK_URL: str = Field(default="http://localhost:5678", env="N8N_WEBHOOK_URL")
DEMO_MODE_ENABLED: bool = Field(default=False, env="DEMO_MODE_ENABLED")
DEMO_SESSION_ID: str = Field(default_factory=lambda: str(uuid.uuid4()), env="DEMO_SESSION_ID")
N8N_WEBHOOK_TIMEOUT: int = Field(default=5, env="N8N_WEBHOOK_TIMEOUT")
DEMO_SPEED_MULTIPLIER: float = Field(default=1.0, env="DEMO_SPEED_MULTIPLIER")
```

**File**: `.env` (Add environment variables)

```env
# N8N Demo Integration
N8N_WEBHOOK_URL=http://localhost:5678
DEMO_MODE_ENABLED=true
DEMO_SPEED_MULTIPLIER=2.0
N8N_WEBHOOK_TIMEOUT=5
```

## N8N Workflow Design

### 1. Master Demo Workflow

```
START (Manual Trigger)
  ↓
Demo Scenario Selection
  ↓
Initialize Character Dashboards
  ↓
Wait for Webhook Events
  ↓
Route Events to Appropriate Sub-Workflows
  ↓
Update Visual Dashboards
  ↓
END (Manual Stop or Timeout)
```

### 2. Character Response Workflow

```
News Event Received
  ↓
Character Analysis Visualization
  ↓
Decision Engine Display
  ↓
Response Generation Progress
  ↓
Personality Validation Check
  ↓
Live Tweet Publication
  ↓
Engagement Metrics Update
```

### 3. Multi-Character Interaction Workflow

```
Initial Post Published
  ↓
Trigger Other Character Analysis
  ↓
Show Character-to-Character Decisions
  ↓
Display Conversation Threading
  ↓
Update Relationship Dynamics
  ↓
Show Cultural Context Evolution
```

## Development Timeline

### Day 1: Foundation

- [ ] Create event decorator system
- [ ] Implement N8N webhook service
- [ ] Add basic event emission to 2-3 key functions
- [ ] Create simple N8N workflow for testing
- [ ] Verify end-to-end event flow

### Day 2: Full Integration

- [ ] Add event decorators to all character agents
- [ ] Implement demo scenario system
- [ ] Create comprehensive N8N workflows
- [ ] Add demo control API endpoints
- [ ] Test all demo scenarios

### Day 3: Polish & Demo Preparation

- [ ] Enhance N8N visual design
- [ ] Add cultural context explanations
- [ ] Create demo narrative script
- [ ] Performance optimization
- [ ] Backup demonstration plan

## Success Metrics

### Technical Achievement

- [ ] Real-time event streaming to N8N (< 1 second latency)
- [ ] All 8 event types successfully visualized
- [ ] Non-invasive integration (zero core logic changes)
- [ ] Graceful degradation when N8N offline
- [ ] 4 complete demo scenarios working

### Demo Impact

- [ ] Visual appeal for non-technical stakeholders
- [ ] Technical depth demonstration for engineers
- [ ] Cultural authenticity showcase
- [ ] Production readiness evidence
- [ ] Live Twitter integration working

## Risk Mitigation

### Technical Risks

1. **N8N Connection Issues**: Graceful degradation, offline mode
2. **Performance Impact**: Async processing, event queuing
3. **Integration Complexity**: Decorator pattern minimizes core changes
4. **Demo Failures**: Multiple backup scenarios, manual triggers

### Demo Risks

1. **Live API Failures**: Pre-recorded backup demos
2. **Network Issues**: Local N8N instance as backup
3. **Timing Issues**: Adjustable speed multipliers
4. **Complexity Overwhelm**: Simple 30-second demo version ready

This implementation plan creates a stunning visual demonstration while maintaining the technical depth and production readiness of the core Python LangGraph system.
