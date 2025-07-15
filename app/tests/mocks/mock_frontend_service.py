"""
Mock Frontend Service for testing.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from app.ports.frontend_port import (
    FrontendPort, DashboardOverview, SystemStatus, CharacterStatus,
    ScenarioCreate, ScenarioResult, CustomNews, NewsInjectionResult,
    UserInteraction, CharacterResponse, AnalyticsSummary
)


class MockFrontendService(FrontendPort):
    """Mock frontend service for testing"""
    
    async def get_dashboard_overview(self) -> DashboardOverview:
        """Get mock dashboard overview"""
        system_status = SystemStatus(
            status="healthy",
            uptime=3600.0,
            active_characters=2,
            total_events=100,
            last_event_time=datetime.now(timezone.utc),
            demo_mode=True
        )
        
        characters = [
            CharacterStatus(
                id="jovani_vazquez",
                name="Jovani Vázquez",
                status="active",
                last_activity=datetime.now(timezone.utc),
                engagement_count=50,
                response_count=45,
                personality_traits=["analytical", "engaging"]
            )
        ]
        
        return DashboardOverview(
            system=system_status,
            characters=characters,
            recent_events=[],
            active_scenarios=["demo_scenario"],
            analytics=AnalyticsSummary()
        )
    
    async def get_character_status(self) -> List[CharacterStatus]:
        """Get mock character statuses"""
        return [
            CharacterStatus(
                id="jovani_vazquez",
                name="Jovani Vázquez",
                status="active",
                last_activity=datetime.now(timezone.utc),
                engagement_count=50,
                response_count=45,
                personality_traits=["analytical", "engaging"]
            )
        ]
    
    async def create_custom_scenario(self, scenario: ScenarioCreate) -> ScenarioResult:
        """Mock scenario creation"""
        return ScenarioResult(
            scenario_id="mock_scenario_id",
            status="success",
            result={"executed_at": datetime.now(timezone.utc).isoformat()}
        )
    
    async def inject_custom_news(self, news: CustomNews) -> NewsInjectionResult:
        """Mock news injection"""
        return NewsInjectionResult(
            news_id="mock_news_id",
            status="injected",
            injected_at=datetime.now(timezone.utc),
            processed_by=["jovani_vazquez"]
        )
    
    async def user_interact_with_character(self, interaction: UserInteraction) -> CharacterResponse:
        """Mock character interaction"""
        return CharacterResponse(
            character_id=interaction.character_id,
            message="This is a mock response from the character.",
            timestamp=datetime.now(timezone.utc),
            context=interaction.context
        ) 