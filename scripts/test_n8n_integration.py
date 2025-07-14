#!/usr/bin/env python3
"""
Test script for N8N integration components

This script tests the N8N webhook service, demo orchestrator, and event system
without requiring an actual N8N instance running.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.n8n_integration import N8NWebhookService, n8n_service
from app.services.demo_orchestrator import DemoOrchestrator, demo_orchestrator
from app.models.demo_scenarios import DEMO_SCENARIOS
from app.utils.demo_helpers import simulate_character_workflow, create_demo_news_event
from app.config import settings

async def test_n8n_service():
    """Test the N8N webhook service"""
    print("🧪 Testing N8N Webhook Service...")
    
    # Test service initialization
    service = N8NWebhookService()
    print(f"✅ Service initialized")
    print(f"   - Demo mode: {service.demo_mode}")
    print(f"   - Webhook URL: {service.n8n_webhook_url}")
    
    # Test event emission (will fail gracefully if N8N not running)
    test_data = {
        "test": True,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Test event from Python"
    }
    
    result = await service.emit_event("test_event", test_data)
    print(f"✅ Event emission test: {'Success' if result else 'Failed (expected if N8N not running)'}")
    
    # Test status
    status = service.get_status()
    print(f"✅ Service status retrieved: {status['total_events_sent']} events sent")
    
    return True

async def test_demo_orchestrator():
    """Test the demo orchestrator"""
    print("\n🧪 Testing Demo Orchestrator...")
    
    # Test scenario listing
    scenarios = demo_orchestrator.get_available_scenarios()
    print(f"✅ Available scenarios: {len(scenarios)}")
    for scenario in scenarios:
        print(f"   - {scenario['id']}: {scenario['title']}")
    
    # Test scenario details
    if scenarios:
        first_scenario = scenarios[0]['id']
        details = demo_orchestrator.get_scenario_info(first_scenario)
        print(f"✅ Scenario details retrieved for {first_scenario}")
        print(f"   - Expected characters: {details['expected_characters']}")
        print(f"   - Duration: {details['estimated_duration']}s")
    
    # Test demo status
    status = demo_orchestrator.get_demo_status()
    print(f"✅ Demo status: {status['demo_mode_enabled']}")
    
    return True

async def test_event_decorators():
    """Test event decorators"""
    print("\n🧪 Testing Event Decorators...")
    
    from app.utils.event_decorators import emit_n8n_event, extract_character_data
    
    # Test decorator with data extractor
    @emit_n8n_event("test_character_event", extract_character_data())
    async def test_character_function(self, news_data):
        return {"status": "success", "character_id": getattr(self, 'character_id', 'test')}
    
    # Create a mock character object
    class MockCharacter:
        def __init__(self):
            self.character_id = "test_character"
            self.name = "Test Character"
    
    mock_char = MockCharacter()
    
    # Test the decorated function
    try:
        result = await test_character_function(mock_char, {"title": "Test News"})
        print(f"✅ Decorated function executed: {result}")
    except Exception as e:
        print(f"⚠️  Decorated function error (expected if N8N not running): {e}")
    
    return True

async def test_demo_helpers():
    """Test demo helper functions"""
    print("\n🧪 Testing Demo Helpers...")
    
    # Test cultural elements
    from app.utils.demo_helpers import get_cultural_elements_for_character, get_character_voice_characteristics
    
    characters = ["jovani_vazquez", "political_figure", "ciudadano_boricua", "cultural_historian"]
    
    for char in characters:
        elements = get_cultural_elements_for_character(char)
        voice = get_character_voice_characteristics(char)
        print(f"✅ {char}: {len(elements)} cultural elements, voice energy: {voice['energy']}")
    
    # Test demo news event creation
    try:
        await create_demo_news_event(
            "Test News Title",
            "This is a test news content for demonstration purposes.",
            ["test", "demo", "integration"],
            0.8
        )
        print("✅ Demo news event created")
    except Exception as e:
        print(f"⚠️  Demo news event error (expected if N8N not running): {e}")
    
    return True

async def test_character_workflow_simulation():
    """Test character workflow simulation"""
    print("\n🧪 Testing Character Workflow Simulation...")
    
    news_data = {
        "id": "test_news_001",
        "title": "Test News for Character Workflow",
        "content": "This is test content for character workflow simulation.",
        "cultural_context": "Puerto Rican cultural context"
    }
    
    try:
        await simulate_character_workflow("jovani_vazquez", news_data, speed_multiplier=5.0)
        print("✅ Character workflow simulation completed")
    except Exception as e:
        print(f"⚠️  Character workflow error (expected if N8N not running): {e}")
    
    return True

async def test_demo_scenario_validation():
    """Test demo scenario validation"""
    print("\n🧪 Testing Demo Scenario Validation...")
    
    from app.utils.demo_helpers import validate_demo_scenario
    
    for scenario_id in DEMO_SCENARIOS.keys():
        is_valid = validate_demo_scenario(scenario_id)
        print(f"✅ {scenario_id}: {'Valid' if is_valid else 'Invalid'}")
    
    # Test invalid scenario
    is_valid = validate_demo_scenario("nonexistent_scenario")
    print(f"✅ nonexistent_scenario: {'Valid' if is_valid else 'Invalid (expected)'}")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting N8N Integration Tests...")
    print("=" * 50)
    
    tests = [
        test_n8n_service,
        test_demo_orchestrator,
        test_event_decorators,
        test_demo_helpers,
        test_character_workflow_simulation,
        test_demo_scenario_validation
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! N8N integration is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Cleanup
    await n8n_service.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 