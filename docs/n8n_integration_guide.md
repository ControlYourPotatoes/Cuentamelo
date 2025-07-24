# N8N Integration Guide

## Overview

The N8N integration provides a visual demonstration layer for the AI character orchestration system. It allows real-time visualization of agent workflows, character interactions, and news processing through N8N workflows.

## Architecture

```
┌─────────────────────────────────────────────┐
│                N8N WORKFLOWS                │
│   (Visual Demonstration Layer)              │
└─────────────────┬───────────────────────────┘
                  │ Webhook Events (Real-time)
┌─────────────────▼───────────────────────────┐
│       PYTHON LANGGRAPH SYSTEM               │
│    ├── Event Decorators                     │
│    ├── N8N Webhook Service                  │
│    ├── Demo Orchestrator                    │
│    └── Core AI Logic                        │
└─────────────────────────────────────────────┘
```

## Components

### 1. Event System

The system emits 10 different event types for N8N visualization:

- **news_discovered**: New Puerto Rican news detected
- **character_analyzing**: Character evaluating news relevance
- **engagement_decision**: Character decides to respond
- **response_generating**: AI generating character response
- **personality_validation**: Checking response matches character voice
- **interaction_triggered**: Character replying to another character
- **post_published**: Live post to Twitter
- **conversation_threading**: Managing multi-character conversation
- **demo_started**: Demo scenario begins
- **demo_stopped**: Demo scenario ends

### 2. Demo Scenarios

Four pre-configured demo scenarios with authentic Puerto Rican cultural context:

1. **political_announcement**: Infrastructure investment announcement
2. **cultural_festival**: Puerto Rican music festival
3. **economic_development**: Technology hub inauguration
4. **emergency_response**: Tropical storm alert

### 3. API Endpoints

#### Demo Control

- `GET /demo/scenarios` - List available scenarios
- `GET /demo/scenarios/{id}` - Get scenario details
- `POST /demo/trigger-scenario` - Start a demo scenario
- `POST /demo/emergency-stop` - Stop all scenarios
- `GET /demo/status` - Get current demo status
- `POST /demo/custom-news` - Inject custom news

#### N8N Integration

- `GET /demo/n8n-status` - Get N8N connection status
- `POST /demo/test-connection` - Test N8N webhook
- `GET /demo/results` - Get demo results
- `POST /demo/reset` - Reset demo state

#### Webhooks

- `POST /webhooks/n8n-callback` - Receive N8N callbacks
- `POST /webhooks/n8n-status` - Receive N8N status updates
- `GET /webhooks/health` - Webhook health check

## Configuration

### Environment Variables

```env
# N8N Integration Settings
N8N_WEBHOOK_URL=http://localhost:5678
DEMO_MODE_ENABLED=true
DEMO_SPEED_MULTIPLIER=2.0
N8N_WEBHOOK_TIMEOUT=5
```

### Default Settings

- **N8N Webhook URL**: `http://localhost:5678`
- **Demo Mode**: `false` (disabled by default)
- **Speed Multiplier**: `1.0` (normal speed)
- **Webhook Timeout**: `5` seconds

## Usage

### 1. Enable Demo Mode

Set the environment variable to enable N8N integration:

```bash
export DEMO_MODE_ENABLED=true
```

### 2. Start the Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test N8N Integration

```bash
python scripts/test_n8n_integration.py
```

### 4. Trigger Demo Scenarios

#### Via API

```bash
# List available scenarios
curl http://localhost:8000/demo/scenarios

# Trigger a scenario
curl -X POST http://localhost:8000/demo/trigger-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "political_announcement",
    "speed_multiplier": 2.0
  }'

# Check demo status
curl http://localhost:8000/demo/status
```

#### Via Python

```python
from app.services.demo_orchestrator import demo_orchestrator

# Run a demo scenario
await demo_orchestrator.run_scenario("political_announcement", speed_multiplier=2.0)

# Get available scenarios
scenarios = demo_orchestrator.get_available_scenarios()
```

### 5. Add Event Decorators to Existing Code

The system uses decorators to emit events without modifying core logic:

```python
from app.utils.event_decorators import emit_n8n_event, emit_news_discovered

# Simple event emission
@emit_n8n_event("news_discovered")
async def discover_news():
    # Your existing news discovery logic
    return news_data

# Event with custom data extraction
@emit_n8n_event("character_analyzing", extract_character_data())
async def analyze_news(self, news_data):
    # Your existing analysis logic
    return analysis_result
```

## N8N Workflow Setup

### 1. Install N8N

```bash
npm install n8n -g
n8n start
```

### 2. Create Webhook Nodes

Create webhook nodes in N8N to receive events:

- **Webhook URL**: `http://localhost:5678/webhook/cuentamelo-event`
- **Method**: POST
- **Authentication**: None (for demo)

### 3. Event Processing

Each event contains:

```json
{
  "event_type": "news_discovered",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "title": "News Title",
    "source": "News Source",
    "topics": ["topic1", "topic2"],
    "urgency_score": 0.8,
    "cultural_relevance": 0.9
  },
  "source": "cuentamelo_langgraph",
  "demo_session_id": "uuid-here"
}
```

### 4. Visual Dashboard

Create N8N workflows to visualize:

- Character decision-making process
- News discovery and analysis
- Character interactions and conversations
- Cultural authenticity metrics
- Performance analytics

## Testing

### Run Integration Tests

```bash
python scripts/test_n8n_integration.py
```

### Test Individual Components

```python
# Test N8N service
from app.services.n8n_integration import n8n_service
status = await n8n_service.test_connection()

# Test demo orchestrator
from app.services.demo_orchestrator import demo_orchestrator
scenarios = demo_orchestrator.get_available_scenarios()

# Test event decorators
from app.utils.event_decorators import emit_n8n_event
@emit_n8n_event("test_event")
async def test_function():
    return "test"
```

## Error Handling

The system is designed to fail gracefully:

- **N8N Offline**: Events are queued but don't break main functionality
- **Webhook Failures**: Logged but don't affect core operations
- **Demo Mode Disabled**: Silent success (no events sent)
- **Invalid Scenarios**: Proper error responses with details

## Performance Considerations

- **Async Processing**: All webhook calls are non-blocking
- **Event Queuing**: Sync functions queue events for async processing
- **Connection Pooling**: HTTP sessions are reused
- **Timeout Handling**: 5-second timeout prevents hanging
- **Graceful Degradation**: System works without N8N

## Cultural Authenticity

The demo scenarios include authentic Puerto Rican cultural elements:

- **Language Mix**: Spanish, English, and Spanglish
- **Cultural References**: Local expressions and traditions
- **Hashtags**: Puerto Rico relevant tags (#PuertoRico, #Boricua)
- **Character Voices**: Distinct personalities for each character
- **Cultural Context**: Realistic Puerto Rican scenarios

## Future Enhancements

- **Real-time Analytics**: Live performance metrics
- **Custom Scenarios**: User-defined demo scenarios
- **Advanced Visualizations**: Interactive dashboards
- **Multi-language Support**: Additional cultural contexts
- **Integration APIs**: Third-party workflow connections
