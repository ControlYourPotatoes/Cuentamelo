"""
Mock Analytics Engine for testing.
"""

from typing import Optional, Dict, Any, List
from app.ports.frontend_port import AnalyticsEngine, AnalyticsSummary, FrontendEvent


class MockAnalyticsEngine(AnalyticsEngine):
    """Mock analytics engine for testing"""
    
    def __init__(self):
        self.events: List[FrontendEvent] = []
    
    async def get_user_analytics(self, user_id: Optional[str]) -> AnalyticsSummary:
        """Get mock user analytics"""
        return AnalyticsSummary(
            total_interactions=100,
            favorite_characters=["jovani_vazquez"],
            engagement_rate=0.85,
            session_duration=1800.0
        )
    
    async def track_event(self, event: FrontendEvent) -> None:
        """Track mock event"""
        self.events.append(event) 