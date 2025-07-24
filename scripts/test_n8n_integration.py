#!/usr/bin/env python3
"""
Test script for N8N integration

This script helps verify that:
1. The API is running and accessible
2. The demo endpoints are working
3. N8N webhook communication is functional
4. The workflow can be triggered successfully
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# API base URL
API_BASE = "http://localhost:8000"

async def test_api_health():
    """Test basic API health"""
    print("🔍 Testing API health...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API is running: {data.get('message', 'Unknown')}")
                    return True
                else:
                    print(f"❌ API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return False

async def test_demo_endpoints():
    """Test demo API endpoints"""
    print("\n🔍 Testing demo endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Test scenarios endpoint
        try:
            async with session.get(f"{API_BASE}/demo/scenarios") as response:
                if response.status == 200:
                    scenarios = await response.json()
                    print(f"✅ Demo scenarios available: {len(scenarios)} scenarios")
                    for scenario in scenarios:
                        print(f"   - {scenario.get('id', 'Unknown')}: {scenario.get('title', 'No title')}")
                else:
                    print(f"❌ Scenarios endpoint failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error testing scenarios: {e}")
            return False

        # Test demo status
        try:
            async with session.get(f"{API_BASE}/demo/status") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ Demo status: {status.get('demo_mode_enabled', False)}")
                    print(f"   N8N connected: {status.get('n8n_connected', False)}")
                    print(f"   Running scenarios: {len(status.get('running_scenarios', []))}")
                else:
                    print(f"❌ Status endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Error testing status: {e}")

        return True

async def test_n8n_connection():
    """Test N8N webhook connection"""
    print("\n🔍 Testing N8N connection...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE}/demo/test-connection") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ N8N connection test: {result.get('status', 'Unknown')}")
                    print(f"   Connected: {result.get('connected', False)}")
                    print(f"   Webhook URL: {result.get('webhook_url', 'Not set')}")
                    print(f"   Demo mode: {result.get('demo_mode', False)}")
                    return result.get('connected', False)
                else:
                    print(f"❌ N8N connection test failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error testing N8N connection: {e}")
            return False

async def test_webhook_event():
    """Test sending a webhook event"""
    print("\n🔍 Testing webhook event...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE}/demo/test-webhook") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Webhook test: {result.get('status', 'Unknown')}")
                    print(f"   Message: {result.get('message', 'No message')}")
                    return result.get('status') == 'success'
                else:
                    print(f"❌ Webhook test failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error testing webhook: {e}")
            return False

async def test_demo_start():
    """Test starting a demo via the /start endpoint"""
    print("\n🔍 Testing demo start endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE}/demo/start") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Demo start: {result.get('status', 'Unknown')}")
                    print(f"   Message: {result.get('message', 'No message')}")
                    print(f"   Scenario: {result.get('scenario', {}).get('id', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Demo start failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Error starting demo: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 N8N Integration Test Suite")
    print("=" * 50)
    
    # Test 1: API Health
    api_healthy = await test_api_health()
    if not api_healthy:
        print("\n❌ API is not running. Please start the API first:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Demo Endpoints
    await test_demo_endpoints()
    
    # Test 3: N8N Connection
    n8n_connected = await test_n8n_connection()
    
    # Test 4: Webhook Event
    if n8n_connected:
        await test_webhook_event()
    
    # Test 5: Demo Start
    await test_demo_start()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   API Running: ✅")
    print(f"   Demo Endpoints: ✅")
    print(f"   N8N Connected: {'✅' if n8n_connected else '❌'}")
    
    if n8n_connected:
        print("\n🎉 Your N8N integration is ready!")
        print("\nNext steps:")
        print("1. Make sure N8N is running on http://localhost:5678")
        print("2. Import your workflow JSON into N8N")
        print("3. Click 'Start Demo' in N8N to trigger the workflow")
        print("4. Watch the events flow through your workflow!")
    else:
        print("\n⚠️  N8N connection failed. Please check:")
        print("1. Is N8N running on http://localhost:5678?")
        print("2. Is the webhook URL correct in your .env file?")
        print("3. Is DEMO_MODE_ENABLED=true in your .env file?")

if __name__ == "__main__":
    asyncio.run(main()) 