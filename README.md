# Cuentamelo - AI Character Twitter Orchestration Platform

> **Puerto Rican AI Characters that Discover, React, and Post to Twitter** 🇵🇷

A sophisticated AI agent orchestration platform using LangGraph that creates and manages Puerto Rican celebrity AI characters who autonomously discover, respond to, and engage with local news on Twitter.

## 🎯 **What This Does**

- **📰 News Discovery**: Automatically finds relevant Puerto Rican news
- **🤖 AI Characters**: 4 distinct Puerto Rican personalities (Jovani Vázquez, Political Figure, Citizen, Cultural Historian)
- **💬 Smart Reactions**: Characters decide whether to engage and generate authentic responses
- **🐦 Real Twitter Posting**: Actually posts to Twitter with character signatures
- **🔄 Full Orchestration**: Complete end-to-end workflow from news to social media

# Video Description

https://www.loom.com/share/94af3be4fc5b402099c42847f51298f4

## 🚀 **Quick Start - Run the Demo**

### 1. **Prerequisites**

```bash
# Python 3.12+ required
python --version

# Docker (for database and Redis)
docker --version
```

### 2. **Clone and Setup**

```bash
git clone <your-repo-url>
cd Cuentamelo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Environment Configuration**

Create a `.env` file in the root directory:

```env
# Anthropic API (Required for AI responses)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Twitter API (Required for posting)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Database (Optional - uses SQLite by default)
DATABASE_URL=postgresql://postgres:password@localhost:5432/cuentamelo
REDIS_URL=redis://localhost:6379/0
```

### 4. **Start Services**

```bash
# Start database and Redis (optional - demo works without them)
docker-compose up -d db redis
```

### 5. **Run the Demo**

```bash
# Full orchestration demo (real Twitter posting)
python scripts/demo_full_orchestration.py

# Interactive demo (you input custom news)
python scripts/demo_full_orchestration.py --interactive
```

## 🎭 **Demo Features**

### **Full Orchestration Demo**

- Discovers 3 simulated Puerto Rican news items
- Jovani Vázquez analyzes each with AI
- Generates authentic Puerto Rican responses
- Posts real tweets to Twitter
- Shows complete workflow with timing and confidence scores

### **Interactive Demo**

- Input your own news headlines and content
- See Jovani's AI reactions in real-time
- Choose whether to post to Twitter
- Perfect for testing different scenarios

## 🤖 **AI Characters**

### **Jovani Vázquez** 🔥

- **Personality**: Energetic Puerto Rican influencer
- **Language**: Spanglish with local expressions
- **Signature**: "¡WEPAAA! Esto está BRUTAL! 🇵🇷"
- **Topics**: Entertainment, lifestyle, youth culture

### **Ciudadano Boricua** 💪

- **Personality**: Everyday Puerto Rican citizen
- **Language**: Casual Puerto Rican Spanish
- **Signature**: "Esto del tráfico es un relajo"
- **Topics**: Economy, transportation, daily life

## 🏗️ **Architecture**

```
News Discovery → AI Analysis → Character Decision → Response Generation → Twitter Posting
                ↓
            LangGraph Workflows + Clean Architecture + Dependency Injection
```

### **Key Components**

- **LangGraph**: Agent orchestration and workflow management
- **Anthropic Claude**: AI character personality and response generation
- **Twitter API**: Real social media posting
- **Clean Architecture**: Ports and adapters pattern
- **Dependency Injection**: Flexible service configuration

## 📁 **Project Structure**

```
Cuentamelo/
├── app/
│   ├── ports/           # Interface definitions
│   ├── adapters/        # Interface implementations
│   ├── agents/          # AI character implementations
│   ├── graphs/          # LangGraph workflows
│   ├── tools/           # Twitter, Claude API tools
│   └── services/        # Dependency injection
├── scripts/
│   └── demo_full_orchestration.py  # Main demo script
├── configs/
│   ├── news_sources.json    # News discovery configuration
│   └── demo_news.json       # Demo scenarios
└── tests/                   # Comprehensive test suite
```

## 🔧 **Configuration**

### **News Sources** (`configs/news_sources.json`)

Configure Twitter accounts for news discovery:

```json
{
  "sources": ["elnuevodia", "primera_hora", "noticel"],
  "keywords": {
    "politics": ["gobierno", "política", "elecciones"],
    "entertainment": ["música", "arte", "cultura"]
  }
}
```

### **Demo Scenarios** (`configs/demo_news.json`)

Pre-configured news scenarios for demos:

```json
{
  "scenarios": [
    {
      "headline": "Bad Bunny Announces Surprise Concert in San Juan",
      "content": "Puerto Rican superstar Bad Bunny...",
      "relevance_score": 0.95
    }
  ]
}
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_graphs/
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🚀 **API Endpoints**

Start the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Key Endpoints**

- `GET /health` - System health check
- `GET /news/discover` - Discover latest news
- `POST /news/process` - Process news with characters
- `GET /characters` - List available characters

## 🎯 **Use Cases**

### **Hackathon Demo**

- Show real AI character interactions
- Demonstrate Twitter integration
- Highlight Puerto Rican cultural authenticity
- Showcase clean architecture and testing

### **Production Deployment**

- Scalable multi-character system
- Real-time news monitoring
- Automated social media engagement
- Cultural content generation

## 🔑 **API Keys Required**

### **Anthropic Claude** (Required)

- Get API key from [Anthropic Console](https://console.anthropic.com/)
- Used for AI character responses and personality

### **Twitter API** (Required for posting)

- Apply for Twitter API access
- Requires Elevated access for posting
- Used for real tweet publication

## 🐛 **Troubleshooting**

### **Common Issues**

**Rate Limiting**

```
Rate limit exceeded. Sleeping for 901 seconds.
```

- Normal behavior for real Twitter API
- Demo will continue after rate limit resets
- Consider using mock provider for testing

**Missing API Keys**

```
ANTHROPIC_API_KEY not found
```

- Ensure `.env` file is created
- Check API key format and permissions

**Database Connection**

```
Database connection failed
```

- Demo works without database
- Start Docker services: `docker-compose up -d db redis`

## 📚 **Documentation**

- **Architecture**: `docs/agent_architecture.md`
- **Character Personalities**: `docs/character_personalities.md`
- **API Documentation**: `docs/api_documentation.md`
- **Implementation Plans**: `context/` directory

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 **Success Story**

This project demonstrates:

- ✅ **Advanced AI Engineering**: LangGraph workflows with proper compilation
- ✅ **Clean Architecture**: Ports and adapters pattern with dependency injection
- ✅ **Cultural Authenticity**: Deep Puerto Rican cultural knowledge
- ✅ **Production Readiness**: Comprehensive testing and error handling
- ✅ **Real Integration**: Actual Twitter posting with character signatures

Perfect for showcasing technical skills while building something culturally meaningful and commercially viable!

---

**Built with ❤️ for Puerto Rico** 🇵🇷

## Signature Phrases: Optionality & Frequency

- Personality configs now support a `signature_phrases` field as an array of objects:
  ```json
  "signature_phrases": [
    {"text": "¡Vamos Vaqueros!", "frequency": "common"},
    {"text": "Pa'lante siempre, broki.", "frequency": "rare"}
  ]
  ```
- `frequency` can be `common` or `rare` (optional, defaults to `rare`).
- Agent logic uses signature phrases according to their frequency: "common" phrases are used more often, "rare" only occasionally.
- For details and rationale, see [context/SIGNATURE_PHRASES_OPTIONAL_AND_FREQUENCY.md](context/SIGNATURE_PHRASES_OPTIONAL_AND_FREQUENCY.md).
- Contributors: Please follow this structure for any new or updated personalities.
