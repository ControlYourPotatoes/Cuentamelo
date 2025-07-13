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

## Development Environment Setup ✅ **COMPLETED**

### Environment Status

- ✅ **Python 3.12.3** virtual environment active
- ✅ **All dependencies installed** from requirements.txt
- ✅ **Docker services running** (PostgreSQL + Redis)
- ✅ **FastAPI application** fully functional
- ✅ **Database tables created** with sample characters
- ✅ **Test suite** established (16 tests passing)
- ✅ **Anthropic API key** configured

### Quick Start Commands

```bash
# Activate environment
source venv/bin/activate

# Start services
docker-compose up -d db redis

# Run application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
python -m pytest tests/ -v
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

## Development Progress - Updated Status

### ✅ **COMPLETED: Foundation Phase**

**Environment & Infrastructure:**

- ✅ **Python 3.12.3 environment** with all dependencies
- ✅ **Docker services** (PostgreSQL + Redis) running
- ✅ **FastAPI application** with health endpoints
- ✅ **Database schema** with 4 Puerto Rican AI characters
- ✅ **Test suite** (16 tests) with pytest framework
- ✅ **Configuration management** with .env support

**Database Characters Ready:**

- ✅ **Jovani Vázquez** (influencer personality)
- ✅ **Político Boricua** (political figure)
- ✅ **Ciudadano Boricua** (everyday citizen)
- ✅ **Historiador Cultural** (cultural historian)

### 🚀 **NEXT: AI Agent Development**

**Day 1-2: LangGraph Character Implementation**

1. **Claude API integration** for character personalities
2. **LangGraph workflows** for agent orchestration
3. **Character behavior patterns** and response generation
4. **Twitter connector** implementation and testing

**Day 2-3: Multi-Agent Coordination**

1. **Agent-to-agent interactions** and conversation threading
2. **News monitoring** and content discovery workflows
3. **Real-time orchestration** across multiple characters
4. **N8N visual demonstration layer** integration

**Demo Preparation:**

1. **Live character interactions** with Puerto Rican news
2. **Performance monitoring** and analytics dashboard
3. **Cultural authenticity** validation and refinement
4. **Hackathon presentation** materials and scenarios

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
