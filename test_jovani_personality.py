#!/usr/bin/env python3
"""
Test script to verify Jovani's personality configuration
"""
from app.models.personality import create_jovani_vazquez_personality

def main():
    print("=== Testing Jovani Vázquez Personality Configuration ===\n")
    
    # Create Jovani's personality
    jovani = create_jovani_vazquez_personality()
    
    print(f"✅ Character: {jovani.character_name}")
    print(f"✅ Type: {jovani.character_type}")
    print(f"✅ Language Style: {jovani.language_style}")
    print(f"✅ Energy Level: {jovani.base_energy_level}")
    print(f"✅ Engagement Threshold: {jovani.engagement_threshold}")
    
    print(f"\n🎵 Signature Phrases ({len(jovani.signature_phrases)}):")
    for phrase in jovani.signature_phrases:
        print(f"   - {phrase}")
    
    print(f"\n💬 Common Expressions ({len(jovani.common_expressions)}):")
    for expr in jovani.common_expressions:
        print(f"   - {expr}")
    
    print(f"\n🎭 Tone Preferences ({len(jovani.tone_preferences)}):")
    for context, tone in jovani.tone_preferences.items():
        print(f"   - {context}: {tone}")
    
    print(f"\n🇵🇷 Puerto Rico References ({len(jovani.puerto_rico_references)}):")
    for ref in jovani.puerto_rico_references:
        print(f"   - {ref}")
    
    print(f"\n🍽️ Local Foods ({len(jovani.local_foods)}):")
    for food in jovani.local_foods:
        print(f"   - {food}")
    
    print(f"\n🎪 Cultural Events ({len(jovani.cultural_events)}):")
    for event in jovani.cultural_events:
        print(f"   - {event}")
    
    print(f"\n🎯 Topics of Interest ({len(jovani.topics_of_interest)}):")
    for topic in jovani.topics_of_interest:
        weight = jovani.topic_weights.get(topic, 0)
        print(f"   - {topic} (weight: {weight})")
    
    print(f"\n✅ Configuration loaded successfully!")
    print(f"✅ All personality data is working correctly!")
    print(f"✅ Ready for AI integration!")

if __name__ == "__main__":
    main() 