# News System Implementation Plan

## 🎯 **PROJECT CONTEXT**

**Project**: Cuentamelo - AI Character Twitter Orchestration Platform  
**Target**: Apexive Hackathon - Fleek Job Opportunity  
**Current Status**: Production Ready - Core architecture complete, Twitter integration working  
**Next Phase**: News System Integration for Character Response Generation

### **Architecture Overview**

This project follows **Clean Architecture** with **Ports and Adapters** pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    PORTS LAYER                              │
│  (Interfaces: AIProviderPort, TwitterProviderPort, etc.)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   ADAPTERS LAYER                            │
│  (Implementations: ClaudeAIAdapter, TwitterAdapter, etc.)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                DEPENDENCY CONTAINER                         │
│  (Service wiring and configuration management)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 BUSINESS LOGIC                              │
│  (Character workflows, orchestration, etc.)                 │
└─────────────────────────────────────────────────────────────┘
```

### **Current System Status**

✅ **COMPLETED**:

- Clean architecture with ports and adapters
- Twitter integration (posting, rate limiting)
- Character personality system (JSON configuration)
- LangGraph workflows (character and orchestration)
- Claude API integration framework
- Comprehensive test suite (20+ tests)

🔄 **IN PROGRESS**: News system for character response generation

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: News Provider Port** (1 hour)

**Goal**: Create the interface that abstracts news discovery and ingestion, following existing port patterns.

**Files to Create**:

- `app/ports/news_provider.py` - News provider interface
- Update `app/ports/__init__.py` - Export new port

**Reference Existing Patterns**:

- See `app/ports/ai_provider.py` for interface structure
- See `app/ports/twitter_provider.py` for provider patterns
- Follow the same abstract base class and method signature patterns

**Key Features**:

- News discovery with filtering (categories, relevance scores)
- Trending topics extraction
- News ingestion for demos
- Health checks and provider info
- Search functionality

### **Phase 2: News Discovery Adapters** (2 hours)

**Goal**: Implement concrete news discovery adapters following clean architecture.

**Files to Create**:

- `app/adapters/twitter_news_adapter.py` - Twitter news discovery implementation
- `app/adapters/simulated_news_adapter.py` - Demo news adapter
- Update `app/adapters/__init__.py` - Export new adapters

**Reference Existing Patterns**:

- See `app/adapters/claude_ai_adapter.py` for adapter structure
- See `app/adapters/twitter_adapter.py` for Twitter integration patterns
- Use dependency injection for external services

**Key Features**:

- Configurable Twitter accounts (no hardcoded accounts)
- Smart caching to avoid rate limits
- Relevance scoring for Puerto Rican content
- Category-based filtering
- Error handling and fallbacks

### **Phase 3: Dependency Injection Integration** (30 minutes)

**Goal**: Wire news providers into the dependency container following existing patterns.

**Files to Update**:

- `app/services/dependency_container.py` - Add news provider registration
- `app/config.py` - Add news provider configuration

**Reference Existing Patterns**:

- See how `AIProviderPort` and `TwitterProviderPort` are registered
- Follow the same configuration and service registration patterns
- Add environment-based provider selection

**Key Features**:

- Configurable news provider selection
- Mock news provider for testing
- Environment-based configuration

### **Phase 4: API Layer Integration** (1 hour)

**Goal**: Create clean API endpoints for news discovery and processing.

**Files to Update**:

- `app/api/news.py` - Refactor to use news provider port
- `app/main.py` - Ensure news router is included

**Reference Existing Patterns**:

- See `app/api/health.py` for endpoint structure
- Follow FastAPI router patterns
- Use dependency injection for services

**Key Features**:

- News discovery endpoints
- News processing with character workflows
- Demo news injection endpoints
- Health checks and trending topics

### **Phase 5: Demo Integration** (1 hour)

**Goal**: Create demo scenarios with simulated news for hackathon presentation.

**Files to Create**:

- `scripts/demo_news_scenarios.py` - Demo news scenarios
- `configs/demo_news.json` - Demo news configuration
- `app/api/demo.py` - Demo control endpoints

**Key Features**:

- Pre-configured demo news scenarios
- Easy news injection for demos
- Character response testing
- Real-time demo control

### **Phase 6: Testing & Validation** (1 hour)

**Goal**: Comprehensive testing following existing test patterns.

**Files to Create**:

- `tests/test_news_provider.py` - News provider tests
- `tests/test_news_adapters.py` - Adapter tests
- `tests/integration/test_news_integration.py` - Integration tests

**Reference Existing Patterns**:

- See `tests/test_agent_factory.py` for test structure
- Follow pytest patterns with async testing
- Use mock services for external dependencies

## 🏗️ **DETAILED ARCHITECTURE DESIGN**

### **News Provider Port Interface**

```python
"""
News Provider Port - Interface for news discovery and ingestion.
This abstracts away the specific news source (Twitter, RSS, APIs, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.conversation import NewsItem


class NewsProviderPort(ABC):
    """
    Port interface for news discovery and ingestion.

    This defines the contract that news providers must implement,
    allowing us to swap between different news sources (Twitter, RSS, APIs, etc.)
    while maintaining clean architecture principles.
    """

    @abstractmethod
    async def discover_latest_news(
        self,
        max_results: int = 10,
        categories: Optional[List[str]] = None,
        min_relevance_score: float = 0.3
    ) -> List[NewsItem]:
        """
        Discover latest news items from the provider.

        Args:
            max_results: Maximum number of news items to return
            categories: Filter by news categories (e.g., ['politics', 'entertainment'])
            min_relevance_score: Minimum relevance score (0.0 to 1.0)

        Returns:
            List of NewsItem objects
        """
        pass

    @abstractmethod
    async def get_trending_topics(self, max_topics: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending topics from the news provider.

        Args:
            max_topics: Maximum number of trending topics to return

        Returns:
            List of trending topic dictionaries with keys:
            - term: str
            - count: int
            - relevance: float
            - category: str
        """
        pass

    @abstractmethod
    async def ingest_news_item(
        self,
        headline: str,
        content: str,
        source: str,
        url: Optional[str] = None,
        published_at: Optional[datetime] = None,
        relevance_score: Optional[float] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> NewsItem:
        """
        Ingest a single news item into the system.

        Args:
            headline: News headline
            content: News content
            source: News source name
            url: Optional URL to the full article
            published_at: Optional publication timestamp
            relevance_score: Optional relevance score (0.0 to 1.0)
            category: Optional news category
            tags: Optional list of tags

        Returns:
            Created NewsItem object
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the news provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the news provider.

        Returns:
            Dictionary with provider information:
            - name: str
            - type: str (e.g., 'twitter', 'rss', 'api')
            - description: str
            - capabilities: List[str]
            - rate_limits: Dict[str, Any]
        """
        pass
```

### **Adapter Implementations**

#### **1. TwitterNewsAdapter**

```python
"""
Twitter News Adapter - Implements NewsProviderPort using Twitter API.
This adapter discovers news from configured Twitter accounts with smart caching.
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timezone

from app.ports.news_provider import NewsProviderPort
from app.models.conversation import NewsItem
from app.tools.twitter_connector import TwitterConnector
from app.services.redis_client import RedisClient


class TwitterNewsAdapter(NewsProviderPort):
    """
    Adapter that implements NewsProviderPort using Twitter API.

    Features:
    - Configurable Twitter accounts (no hardcoded accounts)
    - Smart caching to avoid rate limits
    - Relevance scoring for Puerto Rican content
    - Category-based filtering
    """

    def __init__(
        self,
        twitter_connector: TwitterConnector,
        redis_client: RedisClient,
        news_sources_config: Dict[str, Any]
    ):
        self.twitter = twitter_connector
        self.redis = redis_client
        self.news_sources = news_sources_config.get("sources", [])
        self.cache_ttl = news_sources_config.get("cache_ttl", 3600)

    # Implementation of abstract methods...
```

#### **2. SimulatedNewsAdapter**

```python
"""
Simulated News Adapter - Implements NewsProviderPort for demos and testing.
This adapter provides pre-configured news scenarios for demonstrations.
"""
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime, timezone

from app.ports.news_provider import NewsProviderPort
from app.models.conversation import NewsItem


class SimulatedNewsAdapter(NewsProviderPort):
    """
    Adapter that implements NewsProviderPort for demos and testing.

    Features:
    - Pre-configured news scenarios
    - Easy news injection for demos
    - No external dependencies
    - Realistic news data for testing
    """

    def __init__(self, demo_scenarios_config: Dict[str, Any]):
        self.demo_scenarios = demo_scenarios_config.get("scenarios", [])
        self.current_scenario_index = 0

    # Implementation of abstract methods...
```

## 📁 **FILE STRUCTURE**

```
app/
├── ports/
│   └── news_provider.py              # 🆕 News provider interface
├── adapters/
│   ├── twitter_news_adapter.py       # 🆕 Twitter news discovery
│   └── simulated_news_adapter.py     # 🆕 Demo news adapter
├── services/
│   └── dependency_container.py       # 🔄 Add news provider registration
├── api/
│   └── news.py                       # 🔄 Refactor to use news provider port
└── config.py                         # 🔄 Add news provider config

configs/
├── news_sources.json                 # 🆕 Configurable news sources
└── demo_news.json                    # 🆕 Demo news scenarios

scripts/
└── demo_news_scenarios.py            # 🆕 Demo news runner

tests/
├── test_news_provider.py             # 🆕 News provider tests
├── test_news_adapters.py             # 🆕 Adapter tests
└── integration/
    └── test_news_integration.py      # 🆕 Integration tests
```

## 🎭 **DEMO SCENARIOS**

### **Configuration File: `configs/demo_news.json`**

```json
{
  "scenarios": [
    {
      "id": "bad_bunny_concert",
      "headline": "Bad Bunny Announces Surprise Concert in San Juan",
      "content": "Puerto Rican superstar Bad Bunny just announced a surprise concert in San Juan next month. The concert will take place at the Coliseo de Puerto Rico and is expected to draw thousands of fans. This marks his first performance in Puerto Rico since his record-breaking tour.",
      "source": "Music News",
      "category": "entertainment",
      "relevance_score": 0.95,
      "tags": ["bad bunny", "concert", "san juan", "music", "puerto rico"],
      "expected_characters": ["jovani_vazquez", "politico_boricua"]
    },
    {
      "id": "tourism_boom",
      "headline": "Puerto Rico Tourism Booms with Record Visitor Numbers",
      "content": "Puerto Rico's tourism sector is experiencing unprecedented growth, with record visitor numbers this year. The island welcomed over 3 million tourists, marking a 25% increase from last year. This growth is attributed to improved infrastructure and marketing campaigns.",
      "source": "Economic News",
      "category": "economy",
      "relevance_score": 0.85,
      "tags": ["tourism", "economy", "growth", "visitors", "puerto rico"],
      "expected_characters": ["politico_boricua", "ciudadano_boricua"]
    },
    {
      "id": "puerto_rican_restaurant",
      "headline": "New Puerto Rican Restaurant Opens in New York",
      "content": "A new Puerto Rican restaurant 'Sabor Boricua' has opened in Brooklyn, bringing authentic Puerto Rican cuisine to New York. The restaurant features traditional dishes like mofongo, arroz con gandules, and pasteles, and has already received rave reviews from the local community.",
      "source": "Food News",
      "category": "culture",
      "relevance_score": 0.8,
      "tags": ["restaurant", "puerto rican", "food", "culture", "new york"],
      "expected_characters": ["abuela_carmen", "ciudadano_boricua"]
    }
  ]
}
```

### **Configuration File: `configs/news_sources.json`**

```json
{
  "cache_ttl": 3600,
  "sources": [
    {
      "username": "ElNuevoDia",
      "display_name": "El Nuevo Día",
      "category": "news",
      "relevance_score": 0.9,
      "is_active": true
    },
    {
      "username": "PrimeraHora",
      "display_name": "Primera Hora",
      "category": "news",
      "relevance_score": 0.9,
      "is_active": true
    },
    {
      "username": "GobiernoPR",
      "display_name": "Gobierno de Puerto Rico",
      "category": "politics",
      "relevance_score": 0.9,
      "is_active": true
    },
    {
      "username": "BadBunnyPR",
      "display_name": "Bad Bunny",
      "category": "entertainment",
      "relevance_score": 0.95,
      "is_active": true
    }
  ],
  "keywords": {
    "breaking": 0.9,
    "última hora": 0.9,
    "noticia": 0.8,
    "anuncio": 0.8,
    "gobierno": 0.8,
    "política": 0.8,
    "economía": 0.8,
    "turismo": 0.7,
    "cultura": 0.7,
    "entretenimiento": 0.7,
    "música": 0.7
  },
  "hashtags": {
    "#PuertoRico": 0.9,
    "#PR": 0.8,
    "#Boricua": 0.8,
    "#Borinquen": 0.8,
    "#SanJuan": 0.7
  }
}
```

## 🚀 **IMPLEMENTATION STEPS**

### **Step 1: Create News Provider Port**

1. **Create `app/ports/news_provider.py`**

   - Follow the pattern from `app/ports/ai_provider.py`
   - Define abstract base class with required methods
   - Include proper type hints and documentation

2. **Update `app/ports/__init__.py`**
   - Import and export the new NewsProviderPort
   - Follow existing export patterns

### **Step 2: Implement Twitter News Adapter**

1. **Create `app/adapters/twitter_news_adapter.py`**

   - Follow the pattern from `app/adapters/claude_ai_adapter.py`
   - Use dependency injection for TwitterConnector and RedisClient
   - Implement smart caching and rate limiting
   - Add relevance scoring for Puerto Rican content

2. **Create `app/adapters/simulated_news_adapter.py`**

   - Follow the same adapter pattern
   - Load demo scenarios from configuration
   - Provide easy news injection for demos

3. **Update `app/adapters/__init__.py`**
   - Export new adapters

### **Step 3: Update Dependency Container**

1. **Update `app/services/dependency_container.py`**

   - Add news provider registration following existing patterns
   - Support environment-based provider selection
   - Add configuration loading for news sources

2. **Update `app/config.py`**
   - Add news provider configuration options
   - Support environment variables for provider selection

### **Step 4: Refactor API Layer**

1. **Update `app/api/news.py`**

   - Refactor to use NewsProviderPort interface
   - Remove direct Twitter API calls
   - Add demo endpoints for news injection
   - Follow existing API patterns

2. **Ensure `app/main.py` includes news router**
   - Verify news router is properly included

### **Step 5: Create Demo Integration**

1. **Create `scripts/demo_news_scenarios.py`**

   - Demo news scenario runner
   - Easy news injection for presentations
   - Character response testing

2. **Create `app/api/demo.py`**
   - Demo control endpoints
   - Real-time demo management
   - Character interaction testing

### **Step 6: Comprehensive Testing**

1. **Create `tests/test_news_provider.py`**

   - Unit tests for NewsProviderPort interface
   - Mock implementations for testing

2. **Create `tests/test_news_adapters.py`**

   - Unit tests for Twitter and Simulated adapters
   - Test caching, error handling, and filtering

3. **Create `tests/integration/test_news_integration.py`**
   - Integration tests with character workflows
   - End-to-end news processing tests

## ✅ **SUCCESS CRITERIA**

### **Technical Goals**

- ✅ Follows existing clean architecture patterns
- ✅ No hardcoded Twitter accounts
- ✅ Easy demo news injection
- ✅ Comprehensive test coverage
- ✅ Performance optimization with caching

### **Demo Goals**

- ✅ Easy news scenario creation
- ✅ Real-time demo control
- ✅ Character response testing
- ✅ No external dependencies for demos

### **Production Goals**

- ✅ Scalable news discovery
- ✅ Rate limit management
- ✅ Error handling and recovery
- ✅ Monitoring and health checks

## 🔧 **TESTING STRATEGY**

### **Unit Tests**

- Test NewsProviderPort interface compliance
- Test adapter implementations independently
- Test caching and rate limiting logic
- Test relevance scoring algorithms

### **Integration Tests**

- Test news discovery with character workflows
- Test end-to-end news processing pipeline
- Test demo scenario execution
- Test API endpoint functionality

### **Mock Services**

- Mock Twitter API for testing
- Mock Redis for caching tests
- Mock news sources for isolated testing

## 📚 **REFERENCES**

### **Existing Files to Study**

- `app/ports/ai_provider.py` - Port interface pattern
- `app/adapters/claude_ai_adapter.py` - Adapter implementation pattern
- `app/services/dependency_container.py` - Service registration pattern
- `app/api/health.py` - API endpoint pattern
- `tests/test_agent_factory.py` - Test structure pattern

### **Key Concepts**

- Clean Architecture with Ports and Adapters
- Dependency Injection patterns
- Async/await patterns for I/O operations
- Error handling and logging patterns
- Configuration management patterns

## 🎯 **NEXT STEPS AFTER IMPLEMENTATION**

1. **Integration Testing**: Test with existing character workflows
2. **Demo Preparation**: Create presentation scenarios
3. **Performance Optimization**: Monitor and optimize caching
4. **Documentation**: Update architecture documentation
5. **Deployment**: Prepare for hackathon demonstration

This implementation plan ensures the news system follows the project's established patterns while providing both production-ready Twitter integration and demo-friendly simulated news capabilities.
