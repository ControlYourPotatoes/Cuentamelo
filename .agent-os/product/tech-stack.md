# Technical Stack

> Last Updated: 2025-07-22
> Version: 1.0.0

## Application Framework
**Framework:** Python 3.12+ with FastAPI
**Version:** FastAPI >=0.104.0
**Language:** Python
**Architecture Pattern:** Clean Architecture with Ports & Adapters

## AI & Agent Framework
**Primary Framework:** LangGraph >=0.1.0
**Supporting Libraries:** LangChain >=0.1.0, LangChain-Anthropic >=0.1.0
**AI Provider:** Anthropic Claude (via API)
**Workflow Management:** LangGraph state machines and workflows

## Database System
**Primary Database:** PostgreSQL 15
**Caching Layer:** Redis 7
**Database Driver:** asyncpg >=0.29.0
**Migration Tool:** Alembic >=1.13.0
**Connection Management:** databases[postgresql] >=0.8.0

## Social Media Integration
**Twitter Integration:** Tweepy >=4.14.0
**API Access:** Twitter API v2 with Elevated access
**Posting Strategy:** Real-time posting with rate limiting

## Workflow Integration
**External Workflow:** N8N integration via webhooks
**HTTP Client:** aiohttp >=3.9.0 with CORS support
**Webhook Management:** FastAPI webhook endpoints

## Development & Testing
**Testing Framework:** Pytest >=7.4.0 with asyncio support
**Test Coverage:** pytest-cov >=4.1.0
**Parallel Testing:** pytest-xdist >=3.3.0
**HTTP Testing:** httpx >=0.25.0
**Mocking Strategy:** Comprehensive mock objects for external services

## Configuration Management
**Settings Management:** Pydantic Settings >=2.1.0 with .env support
**Validation:** Pydantic >=2.5.0 for data validation
**Environment Variables:** python-dotenv >=1.0.0
**Schema Validation:** jsonschema >=4.20.0

## Infrastructure & Deployment
**Containerization:** Docker & Docker Compose
**Application Hosting:** FastAPI with Uvicorn[standard] >=0.24.0
**Database Hosting:** PostgreSQL container with persistent volumes
**Caching Infrastructure:** Redis container with authentication
**Static Assets:** FastAPI StaticFiles for dashboard serving

## Development Tools
**Logging:** Loguru >=0.7.0 for structured logging
**Monitoring Dashboard:** Streamlit >=1.28.0 for development dashboards
**Code Quality:** Type hints with typing-extensions >=4.8.0
**UUID Management:** Built-in uuid module

## Architecture Patterns
**Primary Pattern:** Ports & Adapters (Hexagonal Architecture)
**Dependency Injection:** Custom dependency container implementation
**Separation of Concerns:** Clear boundaries between domains, adapters, and infrastructure
**Interface Abstractions:** Port interfaces for all external integrations
**Service Layer:** Business logic isolation with service classes