#!/usr/bin/env python3
"""
Test script for Frontend Infrastructure

This script demonstrates the new frontend infrastructure including:
- Dashboard overview API
- Character status API
- Custom scenario creation
- News injection
- User character interactions
- Real-time event communication
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
N8N_BASE_URL = "http://localhost:5678"

class FrontendInfrastructureTester:
    """Test the new frontend infrastructure functionality"""
    
    def __init__(self):
        self.session = None
        self.session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_session(self) -> str:
        """Create a new user session"""
        print("🔐 Creating user session...")
        
        async with self.session.get(f"{API_BASE_URL}/api/frontend/session/create") as response:
            if response.status == 200:
                data = await response.json()
                self.session_id = data["session_id"]
                print(f"✅ Session created: {self.session_id}")
                return self.session_id
            else:
                print(f"❌ Failed to create session: {response.status}")
                return None
    
    async def test_dashboard_overview(self):
        """Test dashboard overview API"""
        print("\n📊 Testing Dashboard Overview...")
        
        if not self.session_id:
            print("❌ No session ID available")
            return
        
        async with self.session.get(
            f"{API_BASE_URL}/api/frontend/dashboard/overview",
            params={"session_id": self.session_id}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Dashboard overview retrieved successfully")
                print(f"   System Status: {data['system']['status']}")
                print(f"   Active Characters: {data['system']['active_characters']}")
                print(f"   Total Events: {data['system']['total_events']}")
                print(f"   Demo Mode: {data['system']['demo_mode']}")
                print(f"   Characters: {len(data['characters'])}")
                print(f"   Active Scenarios: {len(data['active_scenarios'])}")
            else:
                print(f"❌ Failed to get dashboard overview: {response.status}")
    
    async def test_character_status(self):
        """Test character status API"""
        print("\n👥 Testing Character Status...")
        
        async with self.session.get(f"{API_BASE_URL}/api/frontend/characters/status") as response:
            if response.status == 200:
                characters = await response.json()
                print(f"✅ Retrieved {len(characters)} characters")
                for char in characters:
                    print(f"   {char['name']} ({char['id']}): {char['status']}")
            else:
                print(f"❌ Failed to get character status: {response.status}")
    
    async def test_custom_scenario(self):
        """Test custom scenario creation"""
        print("\n🎬 Testing Custom Scenario Creation...")
        
        scenario_data = {
            "name": "Test Scenario",
            "description": "A test scenario for frontend infrastructure",
            "character_ids": ["jovani_vazquez"],
            "news_items": [
                {
                    "title": "Test News Item",
                    "content": "This is a test news item for the scenario",
                    "source": "test",
                    "category": "test"
                }
            ],
            "execution_speed": 1.0,
            "custom_parameters": {
                "test_mode": True
            }
        }
        
        async with self.session.post(
            f"{API_BASE_URL}/api/frontend/scenarios/create",
            json=scenario_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Scenario created successfully: {result['scenario_id']}")
                print(f"   Status: {result['status']}")
                if result.get('result'):
                    print(f"   News Items Processed: {result['result']['news_items_processed']}")
            else:
                print(f"❌ Failed to create scenario: {response.status}")
    
    async def test_news_injection(self):
        """Test custom news injection"""
        print("\n📰 Testing News Injection...")
        
        news_data = {
            "title": "Breaking News: Frontend Infrastructure Test",
            "content": "The new frontend infrastructure is working perfectly!",
            "source": "test_script",
            "category": "technology",
            "priority": 1,
            "custom_metadata": {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        async with self.session.post(
            f"{API_BASE_URL}/api/frontend/news/inject",
            json=news_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ News injected successfully: {result['news_id']}")
                print(f"   Status: {result['status']}")
                print(f"   Injected at: {result['injected_at']}")
            else:
                print(f"❌ Failed to inject news: {response.status}")
    
    async def test_character_interaction(self):
        """Test user interaction with characters"""
        print("\n💬 Testing Character Interaction...")
        
        interaction_data = {
            "session_id": self.session_id,
            "character_id": "jovani_vazquez",
            "message": "Hello! How are you today?",
            "context": {
                "user_name": "Test User",
                "interaction_type": "greeting"
            }
        }
        
        async with self.session.post(
            f"{API_BASE_URL}/api/frontend/characters/interact",
            json=interaction_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Character interaction successful")
                print(f"   Character: {result['character_id']}")
                print(f"   Response: {result['message'][:100]}...")
                print(f"   Timestamp: {result['timestamp']}")
            else:
                print(f"❌ Failed to interact with character: {response.status}")
    
    async def test_health_check(self):
        """Test frontend health check"""
        print("\n🏥 Testing Frontend Health Check...")
        
        async with self.session.get(f"{API_BASE_URL}/api/frontend/health") as response:
            if response.status == 200:
                health_data = await response.json()
                print("✅ Frontend health check successful")
                print(f"   Frontend Service: {health_data['frontend_service']}")
                print(f"   Event Bus: {health_data['event_bus']}")
                print(f"   Timestamp: {health_data['timestamp']}")
            else:
                print(f"❌ Frontend health check failed: {response.status}")
    
    async def test_websocket_events(self):
        """Test WebSocket event communication"""
        print("\n🔌 Testing WebSocket Events...")
        
        if not self.session_id:
            print("❌ No session ID available for WebSocket test")
            return
        
        try:
            # Create WebSocket connection
            ws_url = f"{API_BASE_URL.replace('http', 'ws')}/api/frontend/ws/events/{self.session_id}"
            
            async with self.session.ws_connect(ws_url) as websocket:
                print("✅ WebSocket connected")
                
                # Listen for a few events
                event_count = 0
                max_events = 5
                
                async for msg in websocket:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        event_data = json.loads(msg.data)
                        print(f"📡 Received event: {event_data['event_type']}")
                        event_count += 1
                        
                        if event_count >= max_events:
                            print(f"✅ Received {event_count} events, closing connection")
                            break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ WebSocket error: {websocket.exception()}")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
    
    async def run_all_tests(self):
        """Run all frontend infrastructure tests"""
        print("🚀 Starting Frontend Infrastructure Tests")
        print("=" * 50)
        
        # Create session first
        await self.create_session()
        
        # Run all tests
        await self.test_health_check()
        await self.test_dashboard_overview()
        await self.test_character_status()
        await self.test_custom_scenario()
        await self.test_news_injection()
        await self.test_character_interaction()
        
        # WebSocket test (runs briefly)
        print("\n⏱️  Running WebSocket test for 10 seconds...")
        await asyncio.wait_for(self.test_websocket_events(), timeout=10)
        
        print("\n" + "=" * 50)
        print("✅ Frontend Infrastructure Tests Completed!")


async def main():
    """Main test function"""
    print("🧪 Frontend Infrastructure Test Script")
    print("This script tests the new N8N frontend infrastructure")
    print()
    
    async with FrontendInfrastructureTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 