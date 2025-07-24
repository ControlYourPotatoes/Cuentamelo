#!/usr/bin/env python3
"""
Twitter Signature Demo Script
Tests the Twitter adapter with character signatures.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.adapters.twitter_adapter import TwitterAdapter
from app.tools.twitter_connector import TwitterConnector
from app.ports.twitter_provider import TwitterPostType


async def test_character_signatures():
    """Test character signature functionality."""
    print("\n🐦 TESTING CHARACTER SIGNATURES")
    print("=" * 50)
    
    try:
        # Initialize adapter
        adapter = TwitterAdapter()
        print("✅ Twitter adapter initialized")
        
        # Test content enhancement with different characters
        test_cases = [
            {
                "character_id": "jovani_vazquez",
                "character_name": "Jovani Vázquez",
                "content": "¡Wepa! This new restaurant in Santurce is absolutely 🔥🔥🔥 The mofongo is to die for! #FoodieLife"
            },
            {
                "character_id": "politico_boricua", 
                "character_name": "Político Boricua",
                "content": "Es fundamental que trabajemos unidos para mejorar la infraestructura de Puerto Rico. Nuestra administración está comprometida con el progreso."
            },
            {
                "character_id": "ciudadano_boricua",
                "character_name": "Ciudadano Boricua", 
                "content": "Los precios están por las nubes otra vez. ¿Cuándo vamos a ver algún alivio real para la gente trabajadora?"
            },
            {
                "character_id": "historiador_cultural",
                "character_name": "Historiador Cultural",
                "content": "Este evento nos recuerda la rica tradición musical de Puerto Rico. La historia de nuestra música es una historia de resistencia y alegría."
            }
        ]
        
        print("\n📝 Testing character signatures:")
        print("-" * 30)
        
        for i, test_case in enumerate(test_cases, 1):
            enhanced_content = adapter._enhance_content_with_character_context(
                test_case["content"],
                test_case["character_id"], 
                test_case["character_name"]
            )
            
            print(f"\n{i}. {test_case['character_name']}:")
            print(f"   Original: {test_case['content']}")
            print(f"   Enhanced: {enhanced_content}")
            print(f"   Length: {len(enhanced_content)}/280")
            
            # Validate length
            if len(enhanced_content) <= 280:
                print("   ✅ Length OK")
            else:
                print(f"   ❌ Too long: {len(enhanced_content)} characters")
        
        print("\n🎯 Signature Summary:")
        print("-" * 20)
        for test_case in test_cases:
            signature = adapter._get_character_signature(
                test_case["character_id"],
                test_case["character_name"]
            )
            print(f"   {test_case['character_name']}: {signature}")
        
        print("\n✅ Character signature test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing character signatures: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_twitter_health():
    """Test Twitter API health check."""
    print("\n🏥 TESTING TWITTER API HEALTH")
    print("=" * 40)
    
    try:
        adapter = TwitterAdapter()
        
        # Test health check
        is_healthy = await adapter.health_check()
        
        if is_healthy:
            print("✅ Twitter API is healthy")
        else:
            print("⚠️  Twitter API health check failed")
            print("   (This is normal if API keys aren't configured yet)")
        
    except Exception as e:
        print(f"❌ Error checking Twitter health: {str(e)}")
        print("   (This is expected if API keys aren't configured)")


async def main():
    """Main test function."""
    print("🐦 TWITTER SIGNATURE DEMO")
    print("=" * 50)
    print("Testing Twitter adapter with character signatures...")
    
    await test_character_signatures()
    await test_twitter_health()
    
    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Create @Cuentamelo Twitter account")
    print("2. Configure Twitter API credentials in .env")
    print("3. Test actual posting with character signatures")


if __name__ == "__main__":
    asyncio.run(main()) 