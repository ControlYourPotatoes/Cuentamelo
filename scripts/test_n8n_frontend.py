#!/usr/bin/env python3
"""
Test script for N8N Frontend Dashboard functionality

This script demonstrates how N8N can serve as the main frontend interface
for the Cuentamelo AI character orchestration system.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
N8N_BASE_URL = "http://localhost:5678"

class N8NFrontendTester:
    """Test the N8N frontend dashboard functionality"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test an API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
            elif method == "PUT":
                async with self.session.put(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
        except Exception as e:
            return {
                "status": "error",
                "data": str(e)
            }
    
    async def test_dashboard_overview(self):
        """Test dashboard overview endpoint"""
        print("🔍 Testing Dashboard Overview...")
        result = await self.test_api_endpoint("/api/dashboard/overview")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Dashboard Overview - Status: {data['system']['status']}")
            print(f"   Active Characters: {data['system']['active_characters']}")
            print(f"   Total Events: {data['system']['total_events']}")
            print(f"   Demo Mode: {data['system']['demo_mode']}")
            print(f"   Characters: {len(data['characters'])}")
        else:
            print(f"❌ Dashboard Overview failed: {result['data']}")
        
        return result
    
    async def test_character_status(self):
        """Test character status endpoint"""
        print("\n👥 Testing Character Status...")
        result = await self.test_api_endpoint("/api/dashboard/characters/status")
        
        if result["status"] == 200:
            characters = result["data"]
            print(f"✅ Character Status - Found {len(characters)} characters:")
            for char in characters:
                print(f"   - {char['name']} ({char['id']}): {char['status']}")
        else:
            print(f"❌ Character Status failed: {result['data']}")
        
        return result
    
    async def test_scenario_templates(self):
        """Test scenario templates endpoint"""
        print("\n📋 Testing Scenario Templates...")
        result = await self.test_api_endpoint("/api/dashboard/scenarios/templates")
        
        if result["status"] == 200:
            templates = result["data"]
            print(f"✅ Scenario Templates - Found {len(templates)} templates:")
            for template in templates:
                print(f"   - {template['name']}: {template['description']}")
                print(f"     Characters: {', '.join(template['characters'])}")
                print(f"     Duration: {template['estimated_duration']}s")
        else:
            print(f"❌ Scenario Templates failed: {result['data']}")
        
        return result
    
    async def test_create_custom_scenario(self):
        """Test custom scenario creation"""
        print("\n🎬 Testing Custom Scenario Creation...")
        
        scenario_data = {
            "name": "Test Custom Scenario",
            "description": "A test scenario created via N8N frontend",
            "news_content": "Nuevo parque recreativo se inaugura en Bayamón con atracciones para toda la familia.",
            "characters": ["jovani_vazquez", "ciudadano_boricua"],
            "speed_multiplier": 2.0
        }
        
        result = await self.test_api_endpoint("/api/dashboard/scenarios/custom", "POST", scenario_data)
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Custom Scenario Created:")
            print(f"   Scenario ID: {data['scenario_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Custom Scenario Creation failed: {result['data']}")
        
        return result
    
    async def test_inject_custom_news(self):
        """Test custom news injection"""
        print("\n📰 Testing Custom News Injection...")
        
        news_data = {
            "title": "Festival de Comida Puertorriqueña en Plaza Las Américas",
            "content": "Este fin de semana se celebra el festival anual de comida puertorriqueña con más de 50 restaurantes locales participando.",
            "source": "custom_test",
            "topics": ["cultura", "comida", "turismo", "eventos"],
            "urgency_score": 0.7
        }
        
        result = await self.test_api_endpoint("/api/dashboard/news/inject", "POST", news_data)
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Custom News Injected:")
            print(f"   News ID: {data['news_id']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Custom News Injection failed: {result['data']}")
        
        return result
    
    async def test_user_interaction(self):
        """Test user interaction with characters"""
        print("\n💬 Testing User Interaction...")
        
        interaction_data = {
            "character_id": "jovani_vazquez",
            "message": "¿Qué opinas sobre el nuevo festival de comida?",
            "context": "User asking about food festival"
        }
        
        result = await self.test_api_endpoint("/api/dashboard/user/interact", "POST", interaction_data)
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ User Interaction Successful:")
            print(f"   Character: {data['character_id']}")
            print(f"   User Message: {data['user_message']}")
            print(f"   Character Response: {data['character_response']}")
        else:
            print(f"❌ User Interaction failed: {result['data']}")
        
        return result
    
    async def test_analytics_metrics(self):
        """Test analytics metrics endpoint"""
        print("\n📊 Testing Analytics Metrics...")
        result = await self.test_api_endpoint("/api/dashboard/analytics/metrics")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Analytics Metrics Retrieved:")
            print(f"   Engagement Data: {data['engagement_data']['total_engagements']} total engagements")
            print(f"   Performance Data: {data['performance_data']['avg_response_time']}s avg response time")
            print(f"   Cultural Data: {data['cultural_data']['cultural_relevance_score']} cultural relevance score")
        else:
            print(f"❌ Analytics Metrics failed: {result['data']}")
        
        return result
    
    async def test_n8n_webhook_endpoints(self):
        """Test N8N webhook endpoints"""
        print("\n🔗 Testing N8N Webhook Endpoints...")
        
        # Test the main event webhook
        webhook_url = f"{N8N_BASE_URL}/webhook/cuentamelo-event"
        
        test_event = {
            "event_type": "test_event",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "test": True,
                "message": "Testing N8N frontend integration"
            },
            "source": "test_script"
        }
        
        try:
            async with self.session.post(webhook_url, json=test_event) as response:
                if response.status == 200:
                    print(f"✅ N8N Webhook Test Successful - Status: {response.status}")
                else:
                    print(f"⚠️ N8N Webhook Test - Status: {response.status}")
        except Exception as e:
            print(f"❌ N8N Webhook Test failed: {str(e)}")
    
    async def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Starting N8N Frontend Dashboard Tests")
        print("=" * 50)
        
        # Test all dashboard endpoints
        await self.test_dashboard_overview()
        await self.test_character_status()
        await self.test_scenario_templates()
        await self.test_create_custom_scenario()
        await self.test_inject_custom_news()
        await self.test_user_interaction()
        await self.test_analytics_metrics()
        
        # Test N8N webhook integration
        await self.test_n8n_webhook_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ N8N Frontend Dashboard Tests Completed!")
        print("\n📋 Next Steps:")
        print("1. Import the workflow JSON into N8N: configs/n8n_frontend_workflow.json")
        print("2. Access N8N at http://localhost:5678")
        print("3. Use the webhook endpoints to interact with the dashboard")
        print("4. Monitor real-time events from the Cuentamelo system")

async def main():
    """Main test function"""
    async with N8NFrontendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 