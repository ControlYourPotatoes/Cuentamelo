#!/usr/bin/env python3
"""
Test N8N with the correct webhook URL
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_n8n_webhook():
    """Test the correct N8N webhook URL"""
    print("🎯 Testing N8N Webhook with Correct URL...")
    
    # Use the URL that N8N is showing you
    webhook_url = "http://localhost:5678/webhook-test/cuentamelo-event"
    
    # Test payload with our AI character event format
    test_payload = {
        "event_type": "news_discovered",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "title": "Gobernador anuncia nueva inversión en infraestructura",
            "source": "El Nuevo Día",
            "topics": ["gobierno", "infraestructura", "economia"],
            "urgency_score": 0.8,
            "cultural_relevance": 0.9
        },
        "source": "cuentamelo_langgraph",
        "demo_session_id": "test-session-123"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 Sending to: {webhook_url}")
            print(f"📦 Payload preview: {test_payload['event_type']} - {test_payload['data']['title']}")
            
            async with session.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"📥 Status: {response.status}")
                response_text = await response.text()
                print(f"📥 Response: {response_text}")
                
                if response.status == 200:
                    print("✅ Webhook test successful!")
                    print("🎉 You should see this event in your N8N workflow!")
                    return True
                else:
                    print(f"❌ Webhook test failed with status {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def send_multiple_events():
    """Send multiple events to simulate AI character workflow"""
    print("\n🚀 Sending Multiple AI Character Events...")
    
    webhook_url = "http://localhost:5678/webhook-test/cuentamelo-event"
    
    events = [
        {
            "event_type": "news_discovered",
            "data": {
                "title": "Festival de música puertorriqueña atrae miles",
                "source": "El Nuevo Día",
                "topics": ["cultura", "musica", "turismo"],
                "urgency_score": 0.7,
                "cultural_relevance": 0.95
            }
        },
        {
            "event_type": "character_analyzing",
            "data": {
                "character_id": "jovani_vazquez",
                "character_name": "Jovani Vázquez",
                "news_id": "festival_001",
                "thinking_process": ["Evaluating cultural relevance", "Checking personality alignment"],
                "analysis_stage": "engagement_decision",
                "processing_time": 2.1
            }
        },
        {
            "event_type": "engagement_decision",
            "data": {
                "character_id": "jovani_vazquez",
                "decision": True,
                "confidence_score": 0.88,
                "reasoning": "High cultural relevance to Puerto Rican music traditions",
                "cultural_context": "Music festivals are central to PR cultural identity"
            }
        },
        {
            "event_type": "response_generating",
            "data": {
                "character_id": "jovani_vazquez",
                "prompt_context": "Puerto Rican music festival announcement",
                "generation_progress": 75,
                "language_mix": "spanglish",
                "tone_indicators": ["excited", "cultural_pride", "community_minded"]
            }
        },
        {
            "event_type": "post_published",
            "data": {
                "character_id": "jovani_vazquez",
                "content": "¡Wepa! 🎵 Festival de música puertorriqueña pa' celebrar nuestra cultura! ¡Esto es lo que nos hace únicos! 🇵🇷 #MusicaPR #CulturaPuertorriquena",
                "tweet_url": "https://twitter.com/jovani_vazquez/status/123456789",
                "cultural_elements_used": ["wepa", "pa'", "🇵🇷", "cultura"]
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, event in enumerate(events, 1):
            payload = {
                **event,
                "timestamp": datetime.now().isoformat(),
                "source": "cuentamelo_langgraph",
                "demo_session_id": "test-session-123"
            }
            
            print(f"\n📤 Event {i}/5: {event['event_type']}")
            
            try:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print(f"   ✅ Sent successfully")
                    else:
                        print(f"   ❌ Failed: {response.status}")
                
                # Wait a bit between events
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")

async def main():
    """Main test function"""
    print("🚀 N8N AI Character Workflow Test")
    print("=" * 50)
    
    # Test single event
    success = await test_n8n_webhook()
    
    if success:
        print("\n🎉 Single event test successful!")
        print("Now let's send a full AI character workflow...")
        
        # Send multiple events
        await send_multiple_events()
        
        print("\n🎭 Full AI Character Workflow Complete!")
        print("Check your N8N interface to see the events flowing through!")
    else:
        print("\n❌ Test failed. Please check your N8N workflow configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 