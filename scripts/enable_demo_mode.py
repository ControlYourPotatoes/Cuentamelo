#!/usr/bin/env python3
"""
Script to enable demo mode and test N8N connection
"""

import os
import sys
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def enable_demo_mode():
    """Enable demo mode by setting environment variable"""
    os.environ['DEMO_MODE_ENABLED'] = 'true'
    print("✅ Demo mode enabled")

async def test_n8n_connection():
    """Test N8N connection with demo mode enabled"""
    from app.services.n8n_integration import n8n_service
    
    print("🔗 Testing N8N Connection...")
    print(f"   - Webhook URL: {n8n_service.n8n_webhook_url}")
    print(f"   - Demo mode: {n8n_service.demo_mode}")
    
    # Test connection
    connected = await n8n_service.test_connection()
    print(f"✅ N8N Connection: {'Connected' if connected else 'Not Connected'}")
    
    if connected:
        print("🎉 N8N is ready to receive events!")
        print("📡 Webhook endpoint: http://localhost:5678/webhook/cuentamelo-event")
    else:
        print("⚠️  N8N is not running or not accessible")
        print("💡 Start N8N with: docker-compose up n8n")
    
    return connected

async def test_event_sending():
    """Test sending a sample event"""
    from app.services.n8n_integration import n8n_service
    
    print("\n📡 Testing Event Sending...")
    
    test_data = {
        "test": True,
        "message": "Test event from Cuentamelo",
        "character_id": "test_character",
        "content": "This is a test event to verify N8N integration"
    }
    
    success = await n8n_service.emit_event("test_event", test_data)
    print(f"✅ Event sent: {'Success' if success else 'Failed'}")
    
    # Show status
    status = n8n_service.get_status()
    print(f"📊 Total events sent: {status['total_events_sent']}")
    
    return success

async def main():
    """Main function"""
    print("🚀 Enabling Demo Mode and Testing N8N Connection...")
    print("=" * 60)
    
    # Enable demo mode
    enable_demo_mode()
    
    # Test connection
    connected = await test_n8n_connection()
    
    if connected:
        # Test event sending
        await test_event_sending()
        
        print("\n🎯 Next Steps:")
        print("1. Create N8N workflow with webhook trigger")
        print("2. Set webhook path to: cuentamelo-event")
        print("3. Run demo scenarios: python scripts/test_n8n_demo_workflow.py")
        print("4. Monitor events in N8N dashboard")
    else:
        print("\n💡 To enable N8N integration:")
        print("1. Start N8N: docker-compose up n8n")
        print("2. Access N8N at: http://localhost:5678")
        print("3. Create workflow with webhook trigger")
        print("4. Re-run this script")
    
    # Cleanup
    await n8n_service.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 