"""
Mock Orchestration Service for testing.
"""
from app.ports.orchestration_service import OrchestrationServicePort

class MockOrchestrationService(OrchestrationServicePort):
    async def trigger_scenario(self, scenario_name, speed=1.0):
        return {"scenario": scenario_name, "status": "triggered", "speed": speed} 