# AI Character Twitter Platform - Cursor Development Setup

## Project Overview

**Project Name**: AI Character Twitter Orchestration Platform + N8N Visual Demo Layer  
**Target**: Apexive Hackathon - Fleek Job Opportunity  
**Developer**: Alexander Puga  
**Timeline**: 3 Days

### Executive Summary

Building an AI agent orchestration platform using LangGraph that creates and manages Puerto Rican celebrity AI characters who autonomously discover, respond to, and engage with local news on Twitter. The system demonstrates all three hackathon topics while directly addressing Fleek's platform needs for AI character creation and social media automation.

**NEW ADDITION**: N8N Visual Demonstration Layer for real-time workflow visualization that showcases the AI orchestration happening in the Python LangGraph system. This creates a powerful dual demo: visual workflows for stakeholders + technical depth showing actual AI architecture.

> **📋 Detailed N8N Implementation Plan**: See `n8n_integration_implementation_plan.md` for complete technical specifications, integration points, and development roadmap for the visual demonstration layer.

## Technology Stack (Updated)

```
✅ LangGraph (Open Source) - Agent Orchestration + Thread Management
✅ FastAPI - API Layer + WebSocket Real-time
✅ PostgreSQL - Data Persistence + Analytics
✅ Redis - State Management + Message Queue
✅ Anthropic Claude API - Character Personalities + Development
✅ Python 3.11+ - Core Development Language
🆕 N8N - Visual Workflow Demonstration Layer
```

## Architecture Overview

### Core System (Production Ready)

```
Python LangGraph Core System:
├── Character Agents (Jovani, Politician, Ciudadano, Historian)
├── News Monitor Agent
├── Interaction Manager
├── Twitter Connector
└── FastAPI API Layer
```

### N8N Demo Layer (Visual Showcase)

```
┌─────────────────────────────────────────────┐
│                N8N DEMO LAYER               │
│        (Visual Workflow Display)            │
└─────────────────┬───────────────────────────┘
                  │ Real-time webhook events
┌─────────────────▼───────────────────────────┐
│       EXISTING PYTHON LANGGRAPH             │
│         (Real AI Orchestration)             │
└─────────────────────────────────────────────┘
```

## Cursor Development Context

### Primary Goals

1. **Agent Orchestration (Topic 1)**: Multi-agent coordination using LangGraph workflows
2. **Tool Building (Topic 2)**: Reusable Twitter connector and personality tools following DRY principles
3. **Roleplaying Agents (Topic 3)**: Authentic Puerto Rican character personalities with Claude API

### Key Business Alignment

- **Fleek Platform Needs**: Direct application to their AI character monetization platform
- **Technical Requirements**: Matches both frontend and backend engineering role requirements
- **Cultural Advantage**: Authentic Puerto Rican cultural knowledge impossible to replicate

## Development Environment Setup

### Required Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install core dependencies
pip install langgraph langchain-anthropic fastapi uvicorn
pip install asyncpg databases[postgresql] redis aioredis
pip install tweepy pydantic-settings python-multipart
pip install streamlit  # For quick dashboard prototyping
```

### Environment Variables (.env)

```env
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_characters
REDIS_URL=redis://localhost:6379/0

# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Application Settings
APP_NAME=AI Character Twitter Platform
DEBUG=True
LOG_LEVEL=INFO

# Character-specific settings
DEFAULT_LANGUAGE=es-pr
POSTING_RATE_LIMIT=10  # posts per hour per character
INTERACTION_COOLDOWN=900  # 15 minutes between same character interactions
```

## Project Structure

```
ai-character-twitter-platform/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── graphs/                    # LangGraph workflow definitions
│   │   ├── __init__.py
│   │   ├── character_workflow.py  # Main character agent workflows
│   │   ├── news_monitor.py       # News discovery workflow
│   │   ├── interaction_manager.py # Character interaction workflows
│   │   └── orchestrator.py       # Master orchestration workflow
│   │
│   ├── agents/                    # Character agent implementations
│   │   ├── __init__.py
│   │   ├── base_character.py     # Base character agent class
│   │   ├── jovani_vazquez.py     # Jovani Vázquez personality
│   │   ├── political_figure.py   # Political figure personality
│   │   ├── ciudadano_boricua.py  # Everyday citizen personality
│   │   └── cultural_historian.py # Cultural historian personality
│   │
│   ├── tools/                     # Reusable tool implementations
│   │   ├── __init__.py
│   │   ├── twitter_connector.py  # Generic Twitter API interface
│   │   ├── claude_client.py      # Anthropic Claude API client
│   │   ├── personality_engine.py # Character consistency validation
│   │   └── analytics_tracker.py  # Performance and engagement tracking
│   │
│   ├── models/                    # Data models and schemas
│   │   ├── __init__.py
│   │   ├── character.py          # Character profile models
│   │   ├── conversation.py       # Conversation thread models
│   │   ├── social_post.py        # Social media post models
│   │   ├── news_item.py          # News article models
│   │   ├── 🆕 demo_scenarios.py   # Demo scenario data models
│   │   └── 🆕 n8n_events.py      # Event schema definitions
│   │
│   ├── api/                       # FastAPI route definitions
│   │   ├── __init__.py
│   │   ├── characters.py         # Character management endpoints
│   │   ├── conversations.py      # Conversation monitoring endpoints
│   │   ├── analytics.py          # Analytics and performance endpoints
│   │   ├── websockets.py         # Real-time dashboard WebSocket
│   │   ├── 🆕 demo.py             # Demo control endpoints
│   │   └── 🆕 webhooks.py         # N8N webhook receivers
│   │
│   ├── utils/                     # 🆕 Utility functions
│   │   ├── __init__.py
│   │   ├── 🆕 event_decorators.py # Event emission decorators
│   │   └── 🆕 demo_helpers.py     # Demo utility functions
│   │
│   └── services/                  # Business logic services
│       ├── __init__.py
│       ├── state_manager.py      # Redis state management
│       ├── database.py           # PostgreSQL operations
│       ├── scheduler.py          # Background task scheduling
│       ├── 🆕 n8n_integration.py  # Webhook service and event management
│       └── 🆕 demo_orchestrator.py # Demo scenario management
│
├── tests/                         # Test suites
│   ├── __init__.py
│   ├── test_graphs/              # LangGraph workflow tests
│   ├── test_agents/              # Character agent tests
│   ├── test_tools/               # Tool functionality tests
│   └── integration/              # End-to-end integration tests
│
├── scripts/                       # Utility and setup scripts
│   ├── setup_database.py        # Database initialization
│   ├── create_test_data.py       # Generate test conversations
│   ├── run_demo.py               # Demo scenario runner
│   └── performance_test.py       # Load testing script
│
├── docs/                          # Documentation
│   ├── character_personalities.md # Character design specifications
│   ├── api_documentation.md       # API endpoint documentation
│   ├── langraph_workflows.md      # Workflow design documentation
│   └── demo_scenarios.md          # Hackathon demo planning
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Local development environment
├── README.md                     # Project overview and setup
└── pyproject.toml               # Python project configuration
```

## Character Personality Specifications

### Jovani Vázquez AI

- **Personality**: Energetic Puerto Rican influencer, slightly provocative but entertaining
- **Language**: Spanglish (Spanish/English mix) with local expressions
- **Engagement**: High (70% reply rate), quick responses (1-5 minutes)
- **Topics**: Entertainment, lifestyle, social issues, youth culture
- **Voice Examples**: "¡Ay, pero esto está buenísimo! 🔥", "Real talk - this is what PR needs 💯"

### Political Figure AI

- **Personality**: Professional Puerto Rican representative, diplomatic but passionate about local issues
- **Language**: Formal Spanish/English, measured responses
- **Engagement**: Medium (40% reply rate), thoughtful responses (5-15 minutes)
- **Topics**: Governance, policy, community issues, economic development
- **Voice Examples**: "Es fundamental que trabajemos unidos...", "Nuestra administración está comprometida..."

### Ciudadano Boricua AI

- **Personality**: Everyday Puerto Rican citizen, practical concerns, occasionally frustrated but hopeful
- **Language**: Casual Puerto Rican Spanish with local slang
- **Engagement**: High on daily life issues (60% reply rate), moderate timing (2-8 minutes)
- **Topics**: Economy, transportation, education, health, daily life struggles
- **Voice Examples**: "Esto del tráfico es un relajo...", "Los precios están por las nubes..."

### Cultural Historian AI

- **Personality**: Puerto Rican cultural expert, educational, bridges past and present
- **Language**: Formal Spanish, informative tone with passion for culture
- **Engagement**: Selective but high quality (25% reply rate), thoughtful responses (10-30 minutes)
- **Topics**: Culture, history, traditions, art, heritage preservation
- **Voice Examples**: "Este evento nos recuerda...", "La historia de Puerto Rico nos enseña..."

## LangGraph Workflow Design

### Master Orchestration Flow

```
News Discovery → Content Analysis → Character Routing → Response Generation → Interaction Management → Analytics Tracking
```

### Character Decision Flow

```
Content Received → Relevance Check → Engagement Decision → Response Generation → Personality Validation → Publication → Conversation Threading
```

### Interaction Management Flow

```
Post Published → Other Characters Notified → Interaction Probability Calculated → Response Generated → Thread Management → Cooldown Applied
```

## Development Priorities (Updated with N8N Integration)

### Day 1: Core System + N8N Foundation

1. **LangGraph setup** with basic character workflow
2. **Claude API integration** for personality generation
3. **Twitter connector** with rate limiting
4. **One working character** (Jovani) responding to news
5. **🆕 Event decorator system** for N8N integration
6. **🆕 Basic N8N workflow** for real-time visualization

### Day 2: Multi-Agent System + Visual Demo Layer

1. **All character personalities** implemented and distinct
2. **Character-to-character interactions** working
3. **Conversation threading** and state persistence
4. **Real-time orchestration** across multiple agents
5. **🆕 Complete N8N integration** with all event types
6. **🆕 Demo scenario system** for live demonstrations

### Day 3: Demo Excellence + Visual Polish

1. **FastAPI dashboard** with live activity monitoring
2. **Performance analytics** and engagement tracking
3. **🆕 N8N visual workflows** polished and stunning
4. **🆕 Demo scenarios** with cultural context explanations
5. **Error handling** and system robustness
6. **🆕 Backup demonstration plans** for live demo safety

## Cursor Development Guidelines

### AI-Assisted Development Strategy

- **Use Cursor for**: LangGraph workflow design, FastAPI endpoint creation, character personality refinement
- **Focus areas**: State management patterns, async/await patterns, error handling
- **Code quality**: Prioritize readable, modular code with clear separation of concerns

### Key Technical Challenges

1. **State synchronization** between Redis and PostgreSQL
2. **Rate limiting** across multiple characters and API endpoints
3. **Conversation threading** with proper context preservation
4. **Character personality consistency** across different conversation contexts

### Performance Considerations

- **Async operations**: All I/O operations should be async
- **Connection pooling**: Database and Redis connections
- **Caching strategy**: Frequently accessed character data
- **Rate limiting**: Twitter API and Claude API call management

## Testing Strategy

### Unit Tests

- Character personality consistency
- Tool functionality (Twitter, Claude API)
- State management operations
- Workflow node functionality

### Integration Tests

- End-to-end conversation flows
- Multi-character interaction scenarios
- API endpoint functionality
- Real-time WebSocket communication

### Demo Scenarios

1. **Breaking news response**: All characters respond to Puerto Rican news with distinct voices
2. **Character interaction**: Natural conversation between characters
3. **Real-time monitoring**: Dashboard showing agent decision-making process
4. **Personality consistency**: Same character maintaining voice across different topics

## Success Metrics

### Technical Achievement

- **4+ distinct character personalities** with consistent voices
- **Real-time multi-agent coordination** using LangGraph
- **Persistent conversation threading** across sessions
- **Sub-second response times** for agent decision-making

### Business Demonstration

- **Authentic Puerto Rican cultural representation** impossible to replicate
- **Scalable architecture** suitable for Fleek's platform needs
- **Cost-effective operation** with intelligent API usage
- **Engaging character interactions** that feel natural and entertaining

## Competitive Advantages

### Technical Differentiation

- **LangGraph workflows**: Advanced agent orchestration beyond simple scripting
- **Cultural authenticity**: Deep Puerto Rican cultural knowledge
- **Modern AI stack**: Cutting-edge tools demonstrating forward-thinking approach
- **Production readiness**: Architecture designed for scale and reliability

### Business Alignment

- **Direct applicability**: Solves exact problems Fleek faces
- **Technical skill demonstration**: Shows capabilities for both available roles
- **Innovation showcase**: Advanced AI engineering with practical application
- **Cultural market advantage**: Authentic representation of Puerto Rican personalities

This setup provides Cursor with comprehensive context for AI-assisted development while maintaining focus on the core hackathon objectives and business goals.
