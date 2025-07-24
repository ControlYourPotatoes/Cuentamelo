"""
Mock AI Provider for testing.
"""
from typing import List, Dict, Any, Optional
from app.ports.ai_provider import AIProviderPort, AIResponse
from app.models.ai_personality_data import AIPersonalityData
from app.models.conversation import ConversationMessage


class MockAIProvider(AIProviderPort):
    async def generate_character_response(
        self,
        personality_data: AIPersonalityData,
        context: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        target_topic: Optional[str] = None,
        thread_context: Optional[str] = None,
        is_new_thread: bool = True
    ) -> AIResponse:
        return AIResponse(
            content="This is a mock character response.",
            confidence_score=0.8,
            character_consistency=True,
            metadata={"mock": True}
        )
    
    async def generate_news_reaction(
        self,
        personality_data: AIPersonalityData,
        news_headline: str,
        news_content: str,
        emotional_context: str = "neutral"
    ) -> AIResponse:
        return AIResponse(
            content=f"Mock reaction to: {news_headline}",
            confidence_score=0.7,
            character_consistency=True,
            metadata={"mock": True, "emotional_context": emotional_context}
        )
    
    async def validate_personality_consistency(
        self,
        personality_data: AIPersonalityData,
        generated_content: str
    ) -> bool:
        return True
    
    async def health_check(self) -> bool:
        return True 