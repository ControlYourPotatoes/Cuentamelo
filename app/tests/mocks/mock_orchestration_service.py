"""
Mock Orchestration Service for testing.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.ports.orchestration_service import (
    OrchestrationServicePort, 
    OrchestrationRequest, 
    OrchestrationResult,
    SystemStatus,
    CharacterStatus
)
from app.models.conversation import NewsItem, ConversationThread, CharacterReaction


class MockOrchestrationService(OrchestrationServicePort):
    async def process_content(self, request: OrchestrationRequest) -> OrchestrationResult:
        return OrchestrationResult(
            success=True,
            execution_time_ms=1000,
            characters_processed=["jovani_vazquez"],
            reactions_generated=[],
            conversations_created=[],
            performance_metrics={"mock": True}
        )
    
    async def get_system_status(self) -> SystemStatus:
        return SystemStatus(
            active=True,
            active_characters=["jovani_vazquez", "politico_boricua"],
            pending_news_count=0,
            active_conversations_count=0,
            api_calls_this_hour=0,
            last_activity=datetime.now(timezone.utc),
            health_score=1.0
        )
    
    async def get_character_status(self, character_id: str) -> Optional[CharacterStatus]:
        return CharacterStatus(
            character_id=character_id,
            character_name=character_id.replace("_", " ").title(),
            available=True,
            last_interaction=datetime.now(timezone.utc),
            interaction_count_today=0,
            current_cooldown_seconds=0,
            engagement_rate=0.8
        )
    
    async def get_all_characters_status(self) -> List[CharacterStatus]:
        return [
            await self.get_character_status("jovani_vazquez"),
            await self.get_character_status("politico_boricua")
        ]
    
    async def add_news_item(self, news_item: NewsItem) -> bool:
        return True
    
    async def force_character_interaction(
        self, 
        character_id: str, 
        context: str,
        bypass_cooldown: bool = False
    ) -> OrchestrationResult:
        return OrchestrationResult(
            success=True,
            execution_time_ms=500,
            characters_processed=[character_id],
            reactions_generated=[],
            conversations_created=[],
            performance_metrics={"mock": True}
        )
    
    async def pause_character(self, character_id: str) -> bool:
        return True
    
    async def resume_character(self, character_id: str) -> bool:
        return True
    
    async def get_active_conversations(self) -> List[ConversationThread]:
        return []
    
    async def get_recent_reactions(
        self, 
        character_id: Optional[str] = None,
        limit: int = 10
    ) -> List[CharacterReaction]:
        return []
    
    async def health_check(self) -> bool:
        return True
    
    async def shutdown_gracefully(self) -> bool:
        return True
    
    async def trigger_scenario(self, scenario_name, speed=1.0):
        return {"scenario": scenario_name, "status": "triggered", "speed": speed} 