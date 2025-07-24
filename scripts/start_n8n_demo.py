#!/usr/bin/env python3
"""
Start N8N Demo Environment

This script helps you start the complete N8N demo environment:
1. Check environment configuration
2. Start the API server
3. Provide instructions for N8N setup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with the following settings:")
        print()
        print("N8N_WEBHOOK_URL=http://localhost:5678")
        print("DEMO_MODE_ENABLED=true")
        print("N8N_WEBHOOK_TIMEOUT=5")
        print("DEMO_SPEED_MULTIPLIER=1.0")
        return False
    
    # Check key settings
    required_settings = [
        "N8N_WEBHOOK_URL",
        "DEMO_MODE_ENABLED"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not os.getenv(setting):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"❌ Missing environment settings: {', '.join(missing_settings)}")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import aiohttp
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")

def print_n8n_instructions():
    """Print instructions for N8N setup"""
    print("\n" + "=" * 60)
    print("📋 N8N Setup Instructions")
    print("=" * 60)
    
    print("\n1. 🚀 Start N8N (if not already running):")
    print("   - Open N8N at: http://localhost:5678")
    print("   - Or start with Docker: docker-compose up n8n")
    
    print("\n2. 📥 Import your workflow:")
    print("   - In N8N, go to Workflows → Import from File")
    print("   - Select: configs/fixed_n8n_workflow (28).json")
    print("   - Activate the workflow")
    
    print("\n3. 🧪 Test the integration:")
    print("   - Run: python scripts/test_n8n_integration.py")
    print("   - This will verify everything is working")
    
    print("\n4. 🎯 Start the demo:")
    print("   - Click 'Start Demo' in your N8N workflow")
    print("   - Watch the events flow through the system!")
    
    print("\n5. 📊 Monitor the demo:")
    print("   - API status: http://localhost:8000/demo/status")
    print("   - API docs: http://localhost:8000/docs")
    
    print("\n" + "=" * 60)
    print("🎉 Your N8N integration is ready to go!")
    print("=" * 60)

def main():
    """Main function"""
    print("🎭 Cuentamelo N8N Demo Environment")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        return
    
    # Print N8N instructions
    print_n8n_instructions()
    
    # Ask if user wants to start the API
    print("\n🤔 Do you want to start the API server now? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        start_api_server()
    else:
        print("\n👋 To start the API later, run:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main() 