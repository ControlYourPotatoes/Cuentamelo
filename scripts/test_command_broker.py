#!/usr/bin/env python3
"""
Test Command Broker - Verify command broker implementation.

This script tests the command broker system to ensure it works correctly
with both CLI and web interfaces.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dependency_container import get_container
from app.ports.command_broker_port import CommandRequest, CommandType, CommandStatus


async def test_command_broker():
    """Test the command broker system"""
    print("🧪 Testing Command Broker System")
    print("=" * 50)
    
    # Get the container and command broker
    container = get_container()
    command_broker = container.get_command_broker()
    
    # Test session ID
    session_id = f"test_session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📋 Test Session ID: {session_id}")
    print()
    
    # Test 1: System Status Command
    print("1️⃣ Testing System Status Command")
    try:
        command = CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id=f"test_status_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            parameters={},
            timestamp=datetime.utcnow(),
            source="test"
        )
        
        response = await command_broker.submit_command(command)
        
        if response.status == CommandStatus.COMPLETED:
            print(f"✅ System Status: {response.result['system_status']['status']}")
            print(f"   Characters: {response.result['character_count']}")
            print(f"   Active Scenarios: {len(response.result['active_scenarios'])}")
        else:
            print(f"❌ System Status Failed: {response.error}")
            
    except Exception as e:
        print(f"❌ System Status Error: {e}")
    
    print()
    
    # Test 2: News Injection Command
    print("2️⃣ Testing News Injection Command")
    try:
        command = CommandRequest(
            command_type=CommandType.NEWS_INJECTION,
            command_id=f"test_news_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            parameters={
                "news": {
                    "title": "Test News from Command Broker",
                    "content": "This is a test news item injected via the command broker system.",
                    "source": "test_script",
                    "category": "test",
                    "priority": 1
                }
            },
            timestamp=datetime.utcnow(),
            source="test"
        )
        
        response = await command_broker.submit_command(command)
        
        if response.status == CommandStatus.COMPLETED:
            print(f"✅ News Injected: {response.result['news_id']}")
            print(f"   Status: {response.result['status']}")
        else:
            print(f"❌ News Injection Failed: {response.error}")
            
    except Exception as e:
        print(f"❌ News Injection Error: {e}")
    
    print()
    
    # Test 3: Scenario Trigger Command
    print("3️⃣ Testing Scenario Trigger Command")
    try:
        command = CommandRequest(
            command_type=CommandType.SCENARIO_TRIGGER,
            command_id=f"test_scenario_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            parameters={
                "scenario_name": "political_announcement",
                "speed": 1.0
            },
            timestamp=datetime.utcnow(),
            source="test"
        )
        
        response = await command_broker.submit_command(command)
        
        if response.status == CommandStatus.COMPLETED:
            print(f"✅ Scenario Triggered: {response.result['scenario_name']}")
            print(f"   Result: {response.result['result']}")
        else:
            print(f"❌ Scenario Trigger Failed: {response.error}")
            
    except Exception as e:
        print(f"❌ Scenario Trigger Error: {e}")
    
    print()
    
    # Test 4: Character Chat Command
    print("4️⃣ Testing Character Chat Command")
    try:
        command = CommandRequest(
            command_type=CommandType.CHARACTER_CHAT,
            command_id=f"test_chat_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            parameters={
                "character_id": "jovani_vazquez",
                "message": "Hello! This is a test message from the command broker."
            },
            timestamp=datetime.utcnow(),
            source="test"
        )
        
        response = await command_broker.submit_command(command)
        
        if response.status == CommandStatus.COMPLETED:
            print(f"✅ Chat Response: {response.result['message'][:100]}...")
            print(f"   Character: {response.result['character_id']}")
        else:
            print(f"❌ Chat Failed: {response.error}")
            
    except Exception as e:
        print(f"❌ Chat Error: {e}")
    
    print()
    
    # Test 5: Command Status Tracking
    print("5️⃣ Testing Command Status Tracking")
    try:
        # Submit a command
        command = CommandRequest(
            command_type=CommandType.SYSTEM_STATUS,
            command_id=f"test_status_track_{datetime.utcnow().timestamp()}",
            session_id=session_id,
            parameters={},
            timestamp=datetime.utcnow(),
            source="test"
        )
        
        command_id = command.command_id
        print(f"   Command ID: {command_id}")
        
        # Submit the command
        response = await command_broker.submit_command(command)
        
        # Check status
        status_response = await command_broker.get_command_status(command_id)
        
        print(f"   Final Status: {status_response.status.value}")
        print(f"   Execution Time: {status_response.execution_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Status Tracking Error: {e}")
    
    print()
    print("🎉 Command Broker Test Complete!")
    print("=" * 50)


async def test_cli_integration():
    """Test CLI integration with command broker"""
    print("\n🔧 Testing CLI Integration")
    print("=" * 30)
    
    try:
        from scripts.cli import CuentameloCLI
        
        cli = CuentameloCLI()
        
        # Test CLI scenario trigger
        print("Testing CLI scenario trigger...")
        await cli.trigger_scenario("political_announcement")
        
        # Test CLI news injection
        print("\nTesting CLI news injection...")
        await cli.inject_news("CLI Test News", "This is a test news item from CLI", "CLI Test")
        
        # Test CLI system status
        print("\nTesting CLI system status...")
        await cli.get_system_status()
        
        print("✅ CLI Integration Test Complete!")
        
    except Exception as e:
        print(f"❌ CLI Integration Error: {e}")


async def main():
    """Run all tests"""
    print("🚀 Starting Command Broker Tests")
    print("=" * 60)
    
    # Test command broker directly
    await test_command_broker()
    
    # Test CLI integration
    await test_cli_integration()
    
    print("\n🎯 All Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 