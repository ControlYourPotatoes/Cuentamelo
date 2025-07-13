#!/usr/bin/env python3
"""
Temporary test file for one-off testing.
Run with: python temp_test.py
Delete after use to keep repo clean.
"""

import asyncio
import sys
import os

# Add app to path so we can import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.database import get_db_health, get_connection
from app.services.redis_client import get_redis_health


async def test_full_system_integration():
    """One-off test to verify complete system integration"""
    print("🔍 Testing complete Cuentamelo system integration...")
    
    print(f"📋 App: {settings.app_name}")
    print(f"🗣️  Language: {settings.default_language}")
    print(f"⚡ Rate limit: {settings.posting_rate_limit} posts/hour")
    
    # Test database
    print("\n📊 Testing database...")
    db_health = await get_db_health()
    print(f"   Status: {db_health['status']}")
    if db_health['status'] == 'healthy':
        print("   ✅ Database connection successful")
        
        # Test database query
        try:
            conn = await get_connection()
            characters = await conn.fetch("SELECT name, personality_type FROM characters")
            print(f"   📝 Found {len(characters)} characters:")
            for char in characters:
                print(f"      - {char['name']} ({char['personality_type']})")
            await conn.close()
        except Exception as e:
            print(f"   ⚠️ Database query error: {e}")
    else:
        print(f"   ❌ Database issue: {db_health.get('error', 'Unknown')}")
    
    # Test Redis
    print("\n🔥 Testing Redis...")
    redis_health = await get_redis_health()
    print(f"   Status: {redis_health['status']}")
    if redis_health['status'] == 'healthy':
        print("   ✅ Redis connection successful")
    else:
        print(f"   ⚠️ Redis issue: {redis_health.get('error', 'Unknown')}")
    
    print("\n🎉 System integration test complete!")


if __name__ == "__main__":
    asyncio.run(test_full_system_integration()) 