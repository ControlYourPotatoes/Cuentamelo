"""
Mock AI Provider for testing.
"""
from app.ports.ai_provider import AIProviderPort

class MockAIProvider(AIProviderPort):
    async def generate_response(self, prompt, context=None):
        return "This is a mock AI response." 