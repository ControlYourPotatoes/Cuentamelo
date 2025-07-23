# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-07-22-interactive-demo-dashboard/spec.md

> Created: 2025-07-22
> Version: 1.0.0

## Endpoints

### GET /api/characters

**Purpose:** List all available AI characters for selection in dashboard and CLI
**Parameters:** 
- `include_details` (optional, boolean): Include personality configuration details
**Response:** JSON array of character objects
**Errors:** 500 if character loading fails

```json
{
  "characters": [
    {
      "character_id": "jovani_vazquez",
      "character_name": "Jovani Vázquez",
      "character_type": "influencer",
      "description": "Energetic Puerto Rican content creator and musician",
      "topics_of_interest": ["music", "daily_life", "family", "puerto_rico"],
      "base_energy": 0.9
    },
    {
      "character_id": "ciudadano_bayamon",
      "character_name": "Miguel Rivera",
      "character_type": "citizen", 
      "description": "Working-class bayamonés, passionate Vaqueros fan",
      "topics_of_interest": ["vaqueros_basketball", "sports", "work_life", "family"],
      "base_energy": 0.7
    }
  ]
}
```

### GET /api/scenarios

**Purpose:** List available predefined news scenarios for demo selection
**Parameters:** 
- `category` (optional, string): Filter by category (sports, politics, entertainment, etc.)
**Response:** JSON array of scenario objects
**Errors:** 500 if scenario loading fails

```json
{
  "scenarios": [
    {
      "scenario_id": "vaqueros_championship",
      "title": "Vaqueros Win BSN Championship",
      "content": "Los Vaqueros de Bayamón conquistaron su campeonato número 17...",
      "category": "sports",
      "relevance_score": 0.95,
      "expected_engagement": {
        "jovani_vazquez": 0.7,
        "ciudadano_bayamon": 0.95
      }
    }
  ]
}
```

### POST /api/analyze-engagement

**Purpose:** Analyze character engagement decisions for given news content
**Parameters:** Request body with news content and character selection
**Response:** Analysis results with engagement decisions and reasoning
**Errors:** 400 for invalid input, 500 for analysis failures

**Request Body:**
```json
{
  "news_content": {
    "title": "Bad Bunny Announces Surprise Concert in San Juan",
    "content": "Puerto Rican superstar Bad Bunny announced...",
    "source": "custom_input",
    "category": "entertainment"
  },
  "characters": ["jovani_vazquez", "ciudadano_bayamon"],
  "analysis_options": {
    "include_reasoning": true,
    "include_topic_analysis": true,
    "generate_responses": false
  }
}
```

**Response:**
```json
{
  "analysis_id": "uuid-session-id",  
  "news_summary": {
    "title": "Bad Bunny Announces Surprise Concert in San Juan",
    "detected_topics": ["music", "puerto_rico", "entertainment"],
    "sentiment": "positive",
    "cultural_relevance": 0.9
  },
  "character_analyses": [
    {
      "character_id": "jovani_vazquez",
      "character_name": "Jovani Vázquez",
      "engagement_decision": "engage",
      "engagement_score": 0.85,
      "reasoning": "High relevance to music and Puerto Rico topics, matches energetic personality",
      "topic_matches": [
        {"topic": "music", "weight": 0.9, "matched": true},
        {"topic": "puerto_rico", "weight": 0.9, "matched": true}
      ],
      "predicted_response_tone": "enthusiastic_performative",
      "confidence": 0.92
    },
    {
      "character_id": "ciudadano_bayamon", 
      "character_name": "Miguel Rivera",
      "engagement_decision": "ignore",
      "engagement_score": 0.25,
      "reasoning": "Low relevance to sports and work topics, doesn't match interests",
      "topic_matches": [
        {"topic": "music", "weight": 0.3, "matched": true},
        {"topic": "entertainment", "weight": 0.4, "matched": true}
      ],
      "predicted_response_tone": null,
      "confidence": 0.78
    }
  ]
}
```

### GET /api/analyze-stream/{session_id}

**Purpose:** Server-Sent Events stream for real-time analysis updates
**Parameters:** 
- `session_id` (path): Session ID from analyze-engagement response
**Response:** SSE stream with analysis progress updates
**Errors:** 404 if session not found, 410 if session expired

**SSE Events:**
```
event: analysis_started
data: {"message": "Starting character analysis", "timestamp": "2025-07-22T21:00:00Z"}

event: character_analyzing  
data: {"character_id": "jovani_vazquez", "stage": "topic_analysis", "progress": 50}

event: character_decision
data: {"character_id": "jovani_vazquez", "decision": "engage", "score": 0.85}

event: analysis_complete
data: {"message": "All character analyses complete", "total_engaged": 1, "total_analyzed": 2}
```

### POST /api/custom-news

**Purpose:** Submit custom news content for analysis (alternative to predefined scenarios)
**Parameters:** Custom news content in request body
**Response:** Formatted news object ready for character analysis
**Errors:** 400 for invalid content, 422 for content processing failures

**Request Body:**
```json
{
  "title": "Custom news headline",
  "content": "Full news article content...",
  "source_url": "https://example.com/news", 
  "category": "local_news"
}
```

**Response:**
```json
{
  "news_id": "custom_uuid",
  "formatted_content": {
    "title": "Custom news headline",
    "content": "Full news article content...",
    "detected_topics": ["local_politics", "community"],
    "sentiment": "neutral",
    "cultural_relevance": 0.6,
    "processing_metadata": {
      "word_count": 150,
      "reading_time": "1 min",
      "language": "es-pr"
    }
  }
}
```

## Controllers

### CharacterAnalysisController

**Actions:**
- `list_characters()`: Return available characters with metadata
- `analyze_engagement()`: Process character engagement analysis
- `stream_analysis()`: Handle SSE streaming for real-time updates

**Business Logic:**
- Load character configurations from JSON files
- Calculate engagement scores using existing personality logic
- Generate topic analysis and reasoning explanations
- Manage analysis sessions and cleanup

**Error Handling:**
- Validate character IDs against available configurations
- Handle character loading failures gracefully
- Manage concurrent analysis requests with rate limiting

### NewsScenarioController

**Actions:**
- `list_scenarios()`: Return predefined demo scenarios
- `process_custom_news()`: Handle user-provided news content
- `validate_news_content()`: Ensure content meets analysis requirements

**Business Logic:**
- Load scenarios from `configs/demo_news.json`
- Process custom news content for topic detection
- Calculate cultural relevance scores
- Format content for character analysis

**Error Handling:**
- Validate news content format and length
- Handle scenario loading failures
- Sanitize user-provided content for security

### DemoSessionController

**Actions:**
- `create_session()`: Initialize analysis session for SSE streaming
- `update_session()`: Send progress updates to connected clients
- `cleanup_session()`: Remove expired sessions and close connections

**Business Logic:**
- Generate unique session IDs for tracking
- Manage SSE connection lifecycle
- Buffer and queue real-time updates
- Implement session timeout and cleanup

**Error Handling:**
- Handle client disconnections gracefully
- Manage session expiration and memory cleanup
- Provide fallback for failed SSE connections

## Integration Points

### Existing Service Integration
- **CharacterAnalysisController** integrates with existing `personality_config_loader.py`
- **NewsScenarioController** leverages existing demo orchestration logic
- **DemoSessionController** reuses session management patterns from N8N integration

### Database Integration
- **Session Storage**: Temporary session data stored in Redis with expiration
- **Analysis Caching**: Frequent analysis results cached for performance
- **Character Metadata**: Character configurations loaded from JSON files as existing

### External Service Integration
- **Character Decision Engine**: Reuses existing LangGraph workflow logic
- **Topic Analysis**: Leverages existing news processing capabilities
- **Cultural Validation**: Integrates with personality consistency validation