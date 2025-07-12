# Cuentamelo - Environment Implementation Plan

## Python Environment Setup Strategy

### **IMPORTANT AGENT RULES**

🚨 **DO NOT PROCEED TO THE NEXT PHASE WITHOUT EXPLICIT USER APPROVAL**

- Complete current phase fully before requesting permission to continue
- Ask user to review and approve each phase completion
- Wait for user confirmation before starting next phase
- Suggest testing opportunities between phases

---

## **Project Overview**

**Objective**: Establish a robust, production-ready development environment for Cuentamelo within the 3-day hackathon timeline.

**Current Architecture Strengths**:

- Clean directory structure with clear separation of concerns
- Comprehensive requirements.txt with pinned versions
- Docker-compose setup for local development
- Modular architecture planning with clear interfaces
- WSL environment for cross-platform compatibility

**Migration/Implementation Goals**:

- **Primary Goal**: Functional Python environment with all dependencies
- **Secondary Goals**: Containerized services (PostgreSQL, Redis) running locally
- **Future Capabilities**: Real-time AI agent orchestration platform
- **Scalability**: Architecture that supports 4+ concurrent AI characters
- **Maintainability**: Clear module boundaries and dependency injection

---

## **Phase 1: Python Environment Foundation** ⏱️ **Hour 1-2**

### **Objectives**

- Establish Python 3.11+ virtual environment
- Install and verify core dependencies
- Configure environment variables
- Validate basic FastAPI functionality

### **Tasks**

#### **1.1 Python Environment Setup**

```bash
# Location: Project Root
# Verify Python version
python --version  # Must be 3.11+

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/WSL
# venv\Scripts\activate  # Windows (if needed)

# Upgrade pip
pip install --upgrade pip
```

#### **1.2 Dependency Installation**

```bash
# Location: Project Root
# Install core dependencies
pip install -r requirements.txt

# Verify critical packages
python -c "import fastapi, uvicorn, langgraph, pydantic; print('Core packages imported successfully')"
```

#### **1.3 Environment Configuration**

```bash
# Location: Project Root
# Create environment file
cp .env.template .env

# Required API keys setup (to be filled by user)
# ANTHROPIC_API_KEY=your_key_here
# TWITTER_API_KEY=your_key_here
# (Other Twitter API credentials)
```

### **Phase 1 Acceptance Criteria**

- [ ] **Functional**: Python 3.11+ virtual environment activated
- [ ] **Technical**: All requirements.txt packages installed without errors
- [ ] **Integration**: FastAPI imports and basic app creation works
- [ ] **Architecture**: Clean dependency management with virtual environment
- [ ] **Testing**: Basic Python package imports successful

### **Testing Required Before Phase 2**

- **Smoke Test**: `python -c "import fastapi; print('FastAPI ready')"`
- **Environment Test**: Virtual environment activation and deactivation
- **Package Test**: Import all critical packages (fastapi, uvicorn, langgraph, pydantic)

**🛑 STOP: Request user approval before proceeding to Phase 2**

---

## **Phase 2: Docker Services Setup** ⏱️ **Hour 2-3**

### **Objectives**

- Launch PostgreSQL and Redis containers
- Verify database connectivity
- Establish persistent data volumes
- Configure service networking

### **Tasks**

#### **2.1 Docker Services Launch**

```bash
# Location: Project Root
# Start database and Redis services
docker-compose up -d db redis

# Verify services are running
docker-compose ps
```

#### **2.2 Service Connectivity Verification**

```python
# Location: scripts/verify_services.py
import asyncio
import asyncpg
import redis

async def test_postgres():
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/ai_characters")
    await conn.close()
    print("✅ PostgreSQL connection successful")

def test_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✅ Redis connection successful")

if __name__ == "__main__":
    asyncio.run(test_postgres())
    test_redis()
```

#### **2.3 Database Initialization**

```python
# Location: scripts/setup_database.py
import asyncio
import asyncpg

async def create_tables():
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/ai_characters")

    # Create basic tables for characters and conversations
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            personality_type VARCHAR(50) NOT NULL,
            language VARCHAR(10) DEFAULT 'es-pr',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            character_id INTEGER REFERENCES characters(id),
            tweet_id VARCHAR(50),
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    await conn.close()
    print("✅ Database tables created")

if __name__ == "__main__":
    asyncio.run(create_tables())
```

### **Phase 2 Acceptance Criteria**

- [ ] **Functional**: PostgreSQL and Redis containers running
- [ ] **Technical**: Database tables created successfully
- [ ] **Integration**: Python can connect to both services
- [ ] **Architecture**: Service isolation with Docker networking
- [ ] **Testing**: Connection verification scripts pass

### **Testing Required Before Phase 3**

- **Service Test**: `docker-compose ps` shows healthy services
- **Connectivity Test**: Python scripts connect to both PostgreSQL and Redis
- **Persistence Test**: Restart containers and verify data persistence

**🛑 STOP: Request user approval before proceeding to Phase 3**

---

## **Phase 3: Project Structure & FastAPI Core** ⏱️ **Hour 3-4**

### **Objectives**

- Create modular project directory structure
- Implement basic FastAPI application
- Establish configuration management
- Set up health check endpoints

### **Tasks**

#### **3.1 Directory Structure Creation**

```bash
# Location: Project Root
# Create directory structure
mkdir -p app/{graphs,agents,tools,models,api,services}
mkdir -p tests/{test_graphs,test_agents,test_tools,integration}
mkdir -p scripts docs dashboard

# Create __init__.py files
touch app/__init__.py
touch app/{graphs,agents,tools,models,api,services}/__init__.py
touch tests/__init__.py
touch tests/{test_graphs,test_agents,test_tools,integration}/__init__.py
```

#### **3.2 FastAPI Application Core**

```python
# Location: app/main.py
from fastapi import FastAPI
from app.config import settings
from app.api import health

app = FastAPI(
    title="Cuentamelo",
    description="LangGraph-powered AI character orchestration for social media",
    version="1.0.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Cuentamelo",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **3.3 Configuration Management**

```python
# Location: app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Cuentamelo"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/ai_characters"
    redis_url: str = "redis://localhost:6379/0"

    # APIs
    anthropic_api_key: str = ""
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # Character settings
    default_language: str = "es-pr"
    posting_rate_limit: int = 10
    interaction_cooldown: int = 900
    max_conversation_turns: int = 6

    class Config:
        env_file = ".env"

settings = Settings()
```

#### **3.4 Health Check Endpoints**

```python
# Location: app/api/health.py
from fastapi import APIRouter, HTTPException
from app.services.database import get_db_health
from app.services.redis_client import get_redis_health
import asyncio

router = APIRouter()

@router.get("/")
async def basic_health():
    return {"status": "healthy", "service": "AI Character Platform"}

@router.get("/detailed")
async def detailed_health():
    try:
        db_health = await get_db_health()
        redis_health = await get_redis_health()

        return {
            "status": "healthy",
            "services": {
                "database": db_health,
                "redis": redis_health,
                "api": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
```

### **Phase 3 Acceptance Criteria**

- [ ] **Functional**: FastAPI application starts without errors
- [ ] **Technical**: All directories and modules created with proper **init**.py
- [ ] **Integration**: Health endpoints return valid responses
- [ ] **Architecture**: Modular structure with clear separation of concerns
- [ ] **Testing**: Basic API endpoints accessible via curl/browser

### **Testing Required Before Phase 4**

- **API Test**: `curl http://localhost:8000/` returns JSON response
- **Health Test**: `curl http://localhost:8000/health/detailed` shows all services
- **Module Test**: `python -c "from app.config import settings; print(settings.app_name)"`

**🛑 STOP: Request user approval before proceeding to Phase 4**

---

## **Phase 4: API Integration Verification** ⏱️ **Hour 4-5**

### **Objectives**

- Verify Anthropic Claude API connectivity
- Test Twitter API authentication
- Implement basic tool interfaces
- Validate configuration loading

### **Tasks**

#### **4.1 Anthropic API Integration**

```python
# Location: app/tools/claude_client.py
from anthropic import Anthropic
from app.config import settings

class ClaudeClient:
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    async def test_connection(self):
        """Test basic API connectivity"""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[{"role": "user", "content": "Hello, are you working?"}]
            )
            return {"status": "success", "response": response.content[0].text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Test script
if __name__ == "__main__":
    import asyncio
    client = ClaudeClient()
    result = asyncio.run(client.test_connection())
    print(f"Claude API Test: {result}")
```

#### **4.2 Twitter API Integration**

```python
# Location: app/tools/twitter_connector.py
import tweepy
from app.config import settings

class TwitterConnector:
    def __init__(self):
        if not all([settings.twitter_api_key, settings.twitter_api_secret]):
            raise ValueError("Twitter API credentials not configured")

        self.client = tweepy.Client(
            bearer_token=settings.twitter_bearer_token,
            consumer_key=settings.twitter_api_key,
            consumer_secret=settings.twitter_api_secret,
            access_token=settings.twitter_access_token,
            access_token_secret=settings.twitter_access_token_secret,
            wait_on_rate_limit=True
        )

    async def test_connection(self):
        """Test Twitter API connectivity"""
        try:
            me = self.client.get_me()
            return {"status": "success", "user": me.data.username}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Test script
if __name__ == "__main__":
    import asyncio
    connector = TwitterConnector()
    result = asyncio.run(connector.test_connection())
    print(f"Twitter API Test: {result}")
```

#### **4.3 Configuration Validation**

```python
# Location: scripts/validate_config.py
from app.config import settings

def validate_environment():
    """Validate all required environment variables"""
    issues = []

    # Check required API keys
    if not settings.anthropic_api_key:
        issues.append("❌ ANTHROPIC_API_KEY not set")
    else:
        issues.append("✅ ANTHROPIC_API_KEY configured")

    if not settings.twitter_api_key:
        issues.append("❌ TWITTER_API_KEY not set")
    else:
        issues.append("✅ TWITTER_API_KEY configured")

    # Check database URL
    if "localhost" not in settings.database_url:
        issues.append("⚠️ DATABASE_URL may not be configured for local development")
    else:
        issues.append("✅ DATABASE_URL configured for local development")

    return issues

if __name__ == "__main__":
    issues = validate_environment()
    for issue in issues:
        print(issue)
```

### **Phase 4 Acceptance Criteria**

- [ ] **Functional**: API clients instantiate without errors
- [ ] **Technical**: Configuration validation passes
- [ ] **Integration**: Test connections return success status
- [ ] **Architecture**: Clean tool interfaces with dependency injection
- [ ] **Testing**: API connectivity verification scripts pass

### **Testing Required Before Development**

- **API Test**: Anthropic and Twitter API test scripts return success
- **Config Test**: Environment validation shows all required keys
- **Integration Test**: FastAPI can import and use tool classes

**🛑 STOP: Request user approval before proceeding to Development Phase**

---

## **Architecture Compliance Checklist**

### **SOLID Principles**

- [ ] **Single Responsibility**: Each tool class handles one API integration
- [ ] **Open/Closed**: Tool interfaces allow extension without modification
- [ ] **Liskov Substitution**: All tool implementations follow common interface
- [ ] **Interface Segregation**: Separate interfaces for Twitter, Claude, and other tools
- [ ] **Dependency Inversion**: FastAPI depends on abstractions, not concrete implementations

### **Clean Architecture**

- [ ] Dependencies point inward (tools → services → domain)
- [ ] Business logic isolated from implementation details
- [ ] Framework-independent core domain models

### **Domain-Driven Design**

- [ ] Rich domain models for Characters, Conversations, Posts
- [ ] Ubiquitous language preserved (Character, Tweet, Personality)
- [ ] Bounded contexts respected (Social Media, AI Agents, Analytics)

---

## **Risk Mitigation**

1. **API Rate Limiting**: Implement tweepy's wait_on_rate_limit and custom retry logic
2. **Environment Issues**: Comprehensive validation scripts and clear error messages
3. **Dependency Conflicts**: Pinned versions in requirements.txt and virtual environment isolation
4. **Service Availability**: Health checks and graceful degradation patterns
5. **Configuration Errors**: Validation at startup and clear configuration documentation

---

## **Success Metrics**

- [ ] **Functional**: All services start without errors and respond to health checks
- [ ] **Performance**: FastAPI startup time < 5 seconds, API response time < 1 second
- [ ] **Compatibility**: Works on WSL, macOS, and Linux development environments
- [ ] **Feature Completeness**: All core APIs (Anthropic, Twitter) successfully authenticated
- [ ] **Quality**: 100% of configuration validation tests pass
- [ ] **Maintainability**: Clear separation of concerns and modular architecture

---

## **Notes for Future Agents**

- **Focus on modular design**: Each tool should be independently testable
- **Validate early and often**: Run validation scripts after each phase
- **Document configuration**: Keep .env.template up to date with all required variables
- **Test in isolation**: Each API integration should work independently
- **Prioritize error handling**: Provide clear error messages for common setup issues
- **Maintain backwards compatibility**: Changes should not break existing functionality

**Remember: Environment stability enables rapid AI character development**
