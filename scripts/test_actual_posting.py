#!/usr/bin/env python3
"""
Test Actual Twitter Posting
Posts a real tweet to test the Twitter integration.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.adapters.twitter_adapter import TwitterAdapter
from app.ports.twitter_provider import TwitterPostType


async def test_actual_posting():
    """Test posting a real tweet."""
    print("🐦 TESTING ACTUAL TWITTER POSTING")
    print("=" * 50)
    
    try:
        # Initialize adapter
        adapter = TwitterAdapter()
        print("✅ Twitter adapter initialized")
        
        # Test tweet content
        test_content = "¡Hola Puerto Rico! 🎉 This is a test tweet from our AI character platform. Testing the integration with @CuentameloAgent! 🇵🇷 #PuertoRico #AITest"
        
        print(f"\n📝 Test tweet content:")
        print(f"   {test_content}")
        print(f"   Length: {len(test_content)}/280")
        
        # Ask for confirmation
        print(f"\n🤔 Ready to post this tweet to @CuentameloAgent?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Posting cancelled")
            return
        
        print("\n🚀 Posting tweet...")
        
        # Post the tweet
        result = await adapter.post_tweet(
            content=test_content,
            character_id="test_character",
            character_name="Test Character"
        )
        
        if result.success:
            print(f"✅ Tweet posted successfully!")
            print(f"   Tweet ID: {result.twitter_tweet_id}")
            print(f"   Posted at: {result.post.posted_at}")
            print(f"   URL: https://twitter.com/CuentameloAgent/status/{result.twitter_tweet_id}")
            
            if result.rate_limit_info:
                print(f"   Rate limit: {result.rate_limit_info.remaining}/{result.rate_limit_info.limit} remaining")
        else:
            print(f"❌ Failed to post tweet: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_character_posting():
    """Test posting with character signatures."""
    print("\n🎭 TESTING CHARACTER SIGNATURE POSTING")
    print("=" * 50)
    
    try:
        adapter = TwitterAdapter()
        
        # Test with Jovani character
        jovani_content = "¡Wepa! Just testing our AI character platform! 🔥 The integration is working perfectly and I'm ready to share some amazing Puerto Rican content! 💯"
        
        print(f"\n📝 Jovani test tweet:")
        print(f"   Original: {jovani_content}")
        
        # Enhance with character context
        enhanced_content = adapter._enhance_content_with_character_context(
            jovani_content,
            "jovani_vazquez",
            "Jovani Vázquez"
        )
        
        print(f"   Enhanced: {enhanced_content}")
        print(f"   Length: {len(enhanced_content)}/280")
        
        # Ask for confirmation
        print(f"\n🤔 Ready to post Jovani's tweet to @CuentameloAgent?")
        response = input("   Type 'yes' to continue, anything else to cancel: ")
        
        if response.lower() != 'yes':
            print("❌ Posting cancelled")
            return
        
        print("\n🚀 Posting Jovani's tweet...")
        
        # Post the tweet
        result = await adapter.post_tweet(
            content=jovani_content,  # Use original content, adapter will enhance it
            character_id="jovani_vazquez",
            character_name="Jovani Vázquez"
        )
        
        if result.success:
            print(f"✅ Jovani's tweet posted successfully!")
            print(f"   Tweet ID: {result.twitter_tweet_id}")
            print(f"   URL: https://twitter.com/CuentameloAgent/status/{result.twitter_tweet_id}")
        else:
            print(f"❌ Failed to post Jovani's tweet: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error posting Jovani's tweet: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("🐦 TWITTER ACTUAL POSTING TEST")
    print("=" * 50)
    print("Testing real tweet posting to @CuentameloAgent...")
    
    # Test basic posting
    await test_actual_posting()
    
    # Test character posting
    await test_character_posting()
    
    print("\n🎉 Posting tests completed!")
    print("\nCheck your @CuentameloAgent account to see the results!")


if __name__ == "__main__":
    asyncio.run(main()) 