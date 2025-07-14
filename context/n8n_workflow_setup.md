# N8N Workflow Setup Guide

## Overview

This guide helps you set up N8N workflows to visualize the Cuentamelo AI character orchestration in real-time.

## Prerequisites

1. N8N running on `http://localhost:5678`
2. Cuentamelo application running on `http://localhost:8000`
3. Demo mode enabled in environment variables

## Environment Setup

Add to your `.env` file:

```env
# N8N Demo Integration
N8N_WEBHOOK_URL=http://localhost:5678
DEMO_MODE_ENABLED=true
DEMO_SPEED_MULTIPLIER=2.0
N8N_WEBHOOK_TIMEOUT=5
```

## Webhook Endpoint

The Cuentamelo application sends events to:

```
POST http://localhost:5678/webhook/cuentamelo-event
```

## Event Types

### 1. News Discovery Events

- **Event Type**: `news_discovered`
- **Description**: New Puerto Rican news detected
- **Data**: title, source, topics, urgency_score, cultural_relevance

### 2. Character Analysis Events

- **Event Type**: `character_analyzing`
- **Description**: Character evaluating relevance
- **Data**: character_id, character_name, news_id, thinking_process

### 3. Engagement Decision Events

- **Event Type**: `engagement_decision`
- **Description**: Character decides to respond
- **Data**: character_id, decision, confidence_score, reasoning

### 4. Response Generation Events

- **Event Type**: `response_generating`
- **Description**: AI generating character response
- **Data**: character_id, prompt_context, generation_progress, language_mix

### 5. Personality Validation Events

- **Event Type**: `personality_validation`
- **Description**: Checking response matches character voice
- **Data**: character_id, consistency_score, voice_characteristics

### 6. Post Publication Events

- **Event Type**: `post_published`
- **Description**: Live post to Twitter
- **Data**: character_id, content, tweet_url, cultural_elements_used

### 7. Interaction Events

- **Event Type**: `interaction_triggered`
- **Description**: Character replying to another character
- **Data**: responder, original_poster, interaction_type

### 8. Conversation Threading Events

- **Event Type**: `conversation_threading`
- **Description**: Managing multi-character conversation
- **Data**: thread_id, participants, turn_count, topic_evolution

## Basic N8N Workflow Setup

### Step 1: Create Webhook Trigger

1. Create new workflow in N8N
2. Add "Webhook" node as trigger
3. Configure webhook:
   - **HTTP Method**: POST
   - **Path**: `/webhook/cuentamelo-event`
   - **Response Mode**: Respond to Webhook

### Step 2: Add Event Router

1. Add "Switch" node after webhook
2. Configure to route based on `{{ $json.event_type }}`
3. Add routes for each event type

### Step 3: Add Visualization Nodes

For each event type, add appropriate visualization:

#### News Discovery

- **Node**: "Set" node
- **Configuration**: Format news data for display
- **Output**: News title, source, topics

#### Character Analysis

- **Node**: "Set" node
- **Configuration**: Show character thinking process
- **Output**: Character name, analysis stage

#### Engagement Decision

- **Node**: "Set" node
- **Configuration**: Display decision with confidence
- **Output**: Decision, confidence score, reasoning

#### Response Generation

- **Node**: "Set" node
- **Configuration**: Show generation progress
- **Output**: Character, language mix, tone indicators

#### Post Publication

- **Node**: "Set" node
- **Configuration**: Display published content
- **Output**: Character, content preview, tweet URL

## Advanced Workflow Features

### Real-time Dashboard

1. **Add "Respond to Webhook" nodes** for each event type
2. **Configure responses** to include formatted data
3. **Use webhook responses** to update external dashboards

### Event Logging

1. **Add "Write Binary File" nodes** to log events
2. **Configure file paths** for different event types
3. **Include timestamps** and event metadata

### Character-specific Styling

1. **Add "Switch" nodes** to route by character_id
2. **Configure different styling** for each character
3. **Include character-specific** visual elements

## Testing the Integration

### 1. Test Connection

```bash
curl -X POST http://localhost:8000/demo/test-connection
```

### 2. List Available Scenarios

```bash
curl http://localhost:8000/demo/scenarios
```

### 3. Trigger Demo Scenario

```bash
curl -X POST http://localhost:8000/demo/trigger-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "political_announcement",
    "speed_multiplier": 2.0
  }'
```

### 4. Check Demo Status

```bash
curl http://localhost:8000/demo/status
```

## Sample N8N Workflow JSON

```json
{
  "name": "Cuentamelo Demo Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "cuentamelo-event",
        "responseMode": "responseNode"
      },
      "id": "webhook-trigger",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "rules": {
          "rules": [
            {
              "conditions": {
                "options": {
                  "caseSensitive": true,
                  "leftValue": "",
                  "typeValidation": "strict"
                },
                "conditions": [
                  {
                    "id": "event_type",
                    "leftValue": "{{ $json.event_type }}",
                    "rightValue": "news_discovered",
                    "operator": {
                      "type": "string",
                      "operation": "equals"
                    }
                  }
                ],
                "combinator": "and"
              },
              "output": 0
            }
          ]
        }
      },
      "id": "event-router",
      "name": "Event Router",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Event Router",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**

   - Check N8N is running on correct port
   - Verify webhook URL in Cuentamelo config
   - Check firewall settings

2. **Events not displaying**

   - Verify event routing in N8N workflow
   - Check event data format
   - Review N8N logs for errors

3. **Demo scenarios not working**
   - Ensure demo mode is enabled
   - Check scenario configuration
   - Verify character agents are loaded

### Debug Commands

```bash
# Test N8N service directly
python scripts/test_n8n_integration.py

# Test demo workflow
python scripts/test_n8n_demo_workflow.py

# Check application logs
tail -f logs/cuentamelo.log
```

## Next Steps

1. **Create visual dashboards** for each event type
2. **Add real-time metrics** and analytics
3. **Implement character-specific** visual themes
4. **Add cultural context** explanations
5. **Create demo narratives** for stakeholders

## Support

For issues or questions:

1. Check the application logs
2. Review N8N workflow configuration
3. Test individual components
4. Consult the implementation plan
