# Requirements and Quick Setup Guide

## requirements.txt
```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.2
pydantic-settings==2.1.0

# LangGraph and LangChain
langgraph==0.0.69
langchain==0.1.0
langchain-anthropic==0.1.1
langchain-community==0.0.13

# Database and State Management
asyncpg==0.29.0
databases[postgresql]==0.8.0
redis==5.0.1
aioredis==2.0.1

# Social Media APIs
tweepy==4.14.0

# HTTP and WebSocket
httpx==0.25.2
websockets==12.0

# Data Processing
pydantic==2.5.2
python-multipart==0.0.6

# Environment and Configuration
python-dotenv==1.0.0

# Development and Testing
pytest==7.4.3
pytest-asyncio==0.21.1
streamlit==1.28.1  # For quick dashboard prototyping

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_characters
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_characters
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # Optional: Dashboard for monitoring
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_characters
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: streamlit run dashboard/main.py --server.port=8501 --server.address=0.0.0.0

volumes:
  postgres_data:
  redis_data:
```

## .env.template
```env
# Copy this to .env and fill in your actual values

# Anthropic API (Required)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_characters
REDIS_URL=redis://localhost:6379/0

# Twitter API Credentials (Required for full functionality)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Application Settings
APP_NAME=AI Character Twitter Platform
DEBUG=True
LOG_LEVEL=INFO

# Character Configuration
DEFAULT_LANGUAGE=es-pr
POSTING_RATE_LIMIT=10
INTERACTION_COOLDOWN=900
MAX_CONVERSATION_TURNS=6

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
API_TIMEOUT=30
RETRY_ATTEMPTS=3
```

## Quick Start Script (start.sh)
```bash
#!/bin/bash

echo "🚀 Starting AI Character Twitter Platform Setup..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+' || echo "0.0")
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "⬇️ Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "⚠️ Please edit .env file with your API keys before continuing"
fi

# Start services with Docker
echo "🐳 Starting database and Redis..."
docker-compose up -d db redis

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Initialize database
echo "🗄️ Setting up database..."
python scripts/setup_database.py

# Start the application
echo "🎯 Starting FastAPI application..."
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "🔧 API docs will be available at: http://localhost:8000/docs"
echo ""
echo "🎉 Setup complete! Press Ctrl+C to stop the application."

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Project Initialization Script (init_project.py)
```python
#!/usr/bin/env python3
"""
Project initialization script for AI Character Twitter Platform
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directory_structure():
    """Create the project directory structure"""
    
    directories = [
        "app",
        "app/graphs",
        "app/agents", 
        "app/tools",
        "app/models",
        "app/api",
        "app/services",
        "tests",
        "tests/test_graphs",
        "tests/test_agents", 
        "tests/test_tools",
        "tests/integration",
        "scripts",
        "docs",
        "dashboard"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("app") or directory.startswith("tests"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created")

def create_basic_files():
    """Create basic configuration files"""
    
    # Create basic main.py
    main_py_content = '''"""
AI Character Twitter Platform - FastAPI Application
"""

from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="AI Character Twitter Platform",
    description="LangGraph-powered AI character orchestration for social media",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "AI Character Twitter Platform", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # Create basic config.py
    config_py_content = '''"""
Application configuration management
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "AI Character Twitter Platform"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    
    # APIs
    anthropic_api_key: str
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
'''
    
    files_to_create = {