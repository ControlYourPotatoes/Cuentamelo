#!/usr/bin/env python3
"""
Cuentamelo CLI - Command-line interface using command broker.

This CLI tool provides quick access to system operations through the command broker
for developers and automation purposes.
"""

import asyncio
import aiohttp
import json
import argparse
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"


class CuentameloCLI:
    """Command-line interface for Cuentamelo using command broker"""
    
    def __init__(self):
        self.session = None
        self.session_id = f"cli_session_{uuid.uuid4().hex[:8]}"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_session(self) -> str:
        """Create a new user session"""
        try:
            async with self.session.get(f"{API_BASE_URL}/api/frontend/session/create") as response:
                if response.status == 200:
                    data = await response.json()
                    self.session_id = data["session_id"]
                    return self.session_id
                else:
                    raise Exception(f"Failed to create session: {response.status}")
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return None
    
    async def trigger_scenario(self, scenario_type: str) -> bool:
        """Trigger a specific scenario using command broker"""
        try:
            async with self.session.post(
                f"{API_BASE_URL}/api/commands/trigger-scenario",
                params={
                    "scenario_name": scenario_type,
                    "speed": 1.0,
                    "session_id": self.session_id
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result["status"] == "completed":
                        print(f"✅ {scenario_type} scenario triggered successfully")
                        print(f"   Execution time: {result['execution_time']:.2f}s")
                        return True
                    else:
                        print(f"❌ Failed to trigger scenario: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error triggering scenario: {e}")
            return False
    
    async def inject_news(self, title: str, content: str, source: str = "cli", category: str = "test") -> bool:
        """Inject custom news using command broker"""
        try:
            async with self.session.post(
                f"{API_BASE_URL}/api/commands/inject-news",
                params={
                    "title": title,
                    "content": content,
                    "source": source,
                    "category": category,
                    "session_id": self.session_id
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result["status"] == "completed":
                        print(f"✅ News injected successfully: {result['result']['news_id']}")
                        return True
                    else:
                        print(f"❌ Failed to inject news: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error injecting news: {e}")
            return False
    
    async def chat_with_character(self, character_id: str, message: str) -> bool:
        """Chat with a character using command broker"""
        try:
            async with self.session.post(
                f"{API_BASE_URL}/api/commands/chat-with-character",
                params={
                    "character_id": character_id,
                    "message": message,
                    "session_id": self.session_id
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result["status"] == "completed":
                        print(f"🤖 {character_id}: {result['result']['message']}")
                        return True
                    else:
                        print(f"❌ Chat failed: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error chatting with character: {e}")
            return False
    
    async def get_status(self) -> bool:
        """Get system status using command broker"""
        try:
            async with self.session.get(
                f"{API_BASE_URL}/api/commands/system-status",
                params={"session_id": self.session_id}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result["status"] == "completed":
                        data = result["result"]
                        system = data["system_status"]
                        print("📊 System Status:")
                        print(f"   Health: {system['status']}")
                        print(f"   Active Characters: {data['character_count']}")
                        print(f"   Active Scenarios: {len(data['active_scenarios'])}")
                        return True
                    else:
                        print(f"❌ Failed to get status: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return False
    
    async def get_characters(self) -> bool:
        """Get character status"""
        try:
            async with self.session.get(f"{API_BASE_URL}/api/frontend/characters/status") as response:
                if response.status == 200:
                    characters = await response.json()
                    print("👥 Characters:")
                    for char in characters:
                        print(f"   {char['name']} ({char['id']}): {char['status']}")
                    return True
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error getting characters: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check frontend health"""
        try:
            async with self.session.get(f"{API_BASE_URL}/api/frontend/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print("🏥 Frontend Health:")
                    print(f"   Frontend Service: {health_data['frontend_service']}")
                    print(f"   Event Bus: {health_data['event_bus']}")
                    print(f"   Timestamp: {health_data['timestamp']}")
                    return True
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            return False


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Cuentamelo CLI - Command-line interface for frontend operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py trigger news_discovery
  python cli.py inject-news "Breaking News" "This is a test news item"
  python cli.py chat jovani_vazquez "Hello, how are you?"
  python cli.py status
  python cli.py health
  python cli.py characters
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Trigger scenario command
    trigger_parser = subparsers.add_parser('trigger', help='Trigger a scenario')
    trigger_parser.add_argument('scenario_type', choices=[
        'news_discovery', 'character_analysis', 'engagement_cycle', 'emergency_stop'
    ], help='Type of scenario to trigger')
    
    # Inject news command
    news_parser = subparsers.add_parser('inject-news', help='Inject custom news')
    news_parser.add_argument('title', help='News title')
    news_parser.add_argument('content', help='News content')
    news_parser.add_argument('--source', default='cli', help='News source (default: cli)')
    news_parser.add_argument('--category', default='test', choices=[
        'technology', 'politics', 'entertainment', 'sports', 'business', 'test'
    ], help='News category (default: test)')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with a character')
    chat_parser.add_argument('character_id', help='Character ID to chat with')
    chat_parser.add_argument('message', help='Message to send')
    
    # Status command
    subparsers.add_parser('status', help='Get system status')
    
    # Characters command
    subparsers.add_parser('characters', help='Get character status')
    
    # Health command
    subparsers.add_parser('health', help='Check frontend health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎭 Cuentamelo CLI")
    print("=" * 40)
    
    async with CuentameloCLI() as cli:
        if args.command == 'trigger':
            await cli.trigger_scenario(args.scenario_type)
        elif args.command == 'inject-news':
            await cli.inject_news(args.title, args.content, args.source, args.category)
        elif args.command == 'chat':
            await cli.chat_with_character(args.character_id, args.message)
        elif args.command == 'status':
            await cli.get_status()
        elif args.command == 'characters':
            await cli.get_characters()
        elif args.command == 'health':
            await cli.health_check()


if __name__ == "__main__":
    asyncio.run(main()) 