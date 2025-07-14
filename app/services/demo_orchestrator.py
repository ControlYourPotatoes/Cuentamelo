import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.models.demo_scenarios import DemoScenario, DEMO_SCENARIOS, DemoTriggerRequest
from app.services.n8n_integration import n8n_service
from app.config import settings

logger = logging.getLogger(__name__)

class DemoOrchestrator:
    """Service for orchestrating demo scenarios and N8N integration"""

    def __init__(self):
        self.running_scenarios: Dict[str, Dict[str, Any]] = {}
        self.scenario_results: Dict[str, Dict[str, Any]] = {}
        self.event_count = 0
        self.demo_mode = settings.DEMO_MODE_ENABLED

    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available demo scenarios"""
        scenarios = []
        for scenario_id, scenario in DEMO_SCENARIOS.items():
            scenarios.append({
                "id": scenario.id,
                "title": scenario.title,
                "topics": scenario.topics,
                "expected_characters": scenario.expected_characters,
                "estimated_duration": scenario.estimated_duration,
                "complexity_level": scenario.complexity_level,
                "cultural_authenticity_score": scenario.cultural_authenticity_score,
                "demo_talking_points": scenario.demo_talking_points
            })
        return scenarios

    def get_scenario_info(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific scenario"""
        if scenario_id not in DEMO_SCENARIOS:
            return None
        
        scenario = DEMO_SCENARIOS[scenario_id]
        return {
            "id": scenario.id,
            "title": scenario.title,
            "content": scenario.content,
            "topics": scenario.topics,
            "expected_characters": scenario.expected_characters,
            "cultural_context": scenario.cultural_context,
            "engagement_predictions": {
                char: {
                    "probability": pred.probability,
                    "tone": pred.tone,
                    "expected_response_type": pred.expected_response_type,
                    "cultural_factors": pred.cultural_factors
                }
                for char, pred in scenario.engagement_predictions.items()
            },
            "demo_talking_points": scenario.demo_talking_points,
            "estimated_duration": scenario.estimated_duration,
            "complexity_level": scenario.complexity_level,
            "cultural_authenticity_score": scenario.cultural_authenticity_score
        }

    def get_scenario_title(self, scenario_id: str) -> str:
        """Get scenario title"""
        if scenario_id in DEMO_SCENARIOS:
            return DEMO_SCENARIOS[scenario_id].title
        return "Unknown Scenario"

    def get_estimated_duration(self, scenario_id: str) -> int:
        """Get estimated duration for scenario"""
        if scenario_id in DEMO_SCENARIOS:
            return DEMO_SCENARIOS[scenario_id].estimated_duration
        return 120

    async def run_scenario(self, scenario_id: str, speed_multiplier: float = 1.0):
        """Run a demo scenario with N8N event emission"""
        if scenario_id not in DEMO_SCENARIOS:
            logger.error(f"Scenario {scenario_id} not found")
            return

        scenario = DEMO_SCENARIOS[scenario_id]
        start_time = datetime.utcnow()
        
        # Mark scenario as running
        self.running_scenarios[scenario_id] = {
            "start_time": start_time,
            "speed_multiplier": speed_multiplier,
            "status": "running",
            "events_processed": 0
        }

        logger.info(f"Starting demo scenario: {scenario.title}")

        try:
            # Emit demo started event
            await n8n_service.emit_event("demo_started", {
                "scenario_id": scenario_id,
                "scenario_title": scenario.title,
                "expected_duration": scenario.estimated_duration,
                "speed_multiplier": speed_multiplier
            })

            # Simulate news discovery
            await self._simulate_news_discovery(scenario, speed_multiplier)

            # Simulate character responses
            await self._simulate_character_responses(scenario, speed_multiplier)

            # Simulate character interactions
            await self._simulate_character_interactions(scenario, speed_multiplier)

            # Mark scenario as completed
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.scenario_results[scenario_id] = {
                "scenario_id": scenario_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "events_processed": self.running_scenarios[scenario_id]["events_processed"],
                "characters_engaged": scenario.expected_characters,
                "posts_published": len(scenario.expected_characters),
                "interactions_generated": len(scenario.expected_characters) - 1,
                "success_rate": 1.0,
                "cultural_authenticity_score": scenario.cultural_authenticity_score,
                "performance_metrics": {
                    "avg_response_time": duration / len(scenario.expected_characters),
                    "events_per_second": self.running_scenarios[scenario_id]["events_processed"] / duration
                }
            }

            # Emit demo completed event
            await n8n_service.emit_event("demo_stopped", {
                "reason": "completed",
                "duration": duration,
                "events_processed": self.running_scenarios[scenario_id]["events_processed"]
            })

            logger.info(f"Demo scenario completed: {scenario.title} in {duration:.2f}s")

        except Exception as e:
            logger.error(f"Error running demo scenario {scenario_id}: {e}")
            await n8n_service.emit_event("demo_stopped", {
                "reason": "error",
                "error": str(e)
            })
        finally:
            # Remove from running scenarios
            if scenario_id in self.running_scenarios:
                del self.running_scenarios[scenario_id]

    async def _simulate_news_discovery(self, scenario: DemoScenario, speed_multiplier: float):
        """Simulate news discovery event"""
        await asyncio.sleep(2 / speed_multiplier)  # Simulate processing time
        
        await n8n_service.emit_event("news_discovered", {
            "title": scenario.title,
            "source": "Demo News Source",
            "topics": scenario.topics,
            "urgency_score": 0.8,
            "cultural_relevance": scenario.cultural_authenticity_score,
            "content_preview": scenario.content[:100] + "..." if len(scenario.content) > 100 else scenario.content
        })
        
        self.running_scenarios[scenario.id]["events_processed"] += 1

    async def _simulate_character_responses(self, scenario: DemoScenario, speed_multiplier: float):
        """Simulate character responses to news"""
        for character_id in scenario.expected_characters:
            # Simulate character analysis
            await asyncio.sleep(1 / speed_multiplier)
            
            await n8n_service.emit_event("character_analyzing", {
                "character_id": character_id,
                "character_name": character_id.replace("_", " ").title(),
                "news_id": f"demo_news_{scenario.id}",
                "thinking_process": [
                    "Evaluating cultural relevance",
                    "Checking personality alignment",
                    "Assessing engagement potential"
                ],
                "analysis_stage": "completed",
                "processing_time": 1.0
            })
            
            self.running_scenarios[scenario.id]["events_processed"] += 1

            # Simulate engagement decision
            await asyncio.sleep(0.5 / speed_multiplier)
            
            prediction = scenario.engagement_predictions.get(character_id)
            decision = prediction.probability > 0.5 if prediction else True
            
            await n8n_service.emit_event("engagement_decision", {
                "character_id": character_id,
                "decision": decision,
                "confidence_score": prediction.probability if prediction else 0.8,
                "reasoning": f"Character {character_id} decides to engage based on cultural relevance",
                "cultural_context": scenario.cultural_context,
                "personality_factors": prediction.cultural_factors if prediction else []
            })
            
            self.running_scenarios[scenario.id]["events_processed"] += 1

            if decision:
                # Simulate response generation
                await asyncio.sleep(2 / speed_multiplier)
                
                await n8n_service.emit_event("response_generating", {
                    "character_id": character_id,
                    "prompt_context": f"Generate response to: {scenario.title}",
                    "generation_progress": 100,
                    "language_mix": "spanish" if character_id == "political_figure" else "spanglish",
                    "tone_indicators": [prediction.tone] if prediction else ["neutral"],
                    "cultural_elements": prediction.cultural_factors if prediction else []
                })
                
                self.running_scenarios[scenario.id]["events_processed"] += 1

                # Simulate personality validation
                await asyncio.sleep(0.5 / speed_multiplier)
                
                await n8n_service.emit_event("personality_validation", {
                    "character_id": character_id,
                    "consistency_score": 0.95,
                    "adjustments_made": [],
                    "voice_characteristics": {
                        "formality": 0.8 if character_id == "political_figure" else 0.3,
                        "energy": 0.9 if character_id == "jovani_vazquez" else 0.6,
                        "cultural_authenticity": scenario.cultural_authenticity_score
                    },
                    "cultural_authenticity": scenario.cultural_authenticity_score
                })
                
                self.running_scenarios[scenario.id]["events_processed"] += 1

                # Simulate post publication
                await asyncio.sleep(1 / speed_multiplier)
                
                sample_content = f"Demo response from {character_id} about {scenario.title}"
                
                await n8n_service.emit_event("post_published", {
                    "character_id": character_id,
                    "content": sample_content,
                    "tweet_url": f"https://twitter.com/CuentameloAgent/status/demo_{character_id}_{scenario.id}",
                    "character_voice_sample": sample_content,
                    "cultural_elements_used": prediction.cultural_factors if prediction else [],
                    "post_metrics": {
                        "character_count": len(sample_content),
                        "hashtag_count": 2,
                        "mention_count": 0
                    }
                })
                
                self.running_scenarios[scenario.id]["events_processed"] += 1

    async def _simulate_character_interactions(self, scenario: DemoScenario, speed_multiplier: float):
        """Simulate character-to-character interactions"""
        if len(scenario.expected_characters) < 2:
            return

        # Simulate conversation threading
        await asyncio.sleep(1 / speed_multiplier)
        
        await n8n_service.emit_event("conversation_threading", {
            "thread_id": f"demo_thread_{scenario.id}",
            "participants": scenario.expected_characters,
            "turn_count": len(scenario.expected_characters),
            "topic_evolution": scenario.topics,
            "cultural_dynamics": scenario.cultural_context,
            "engagement_level": 0.85
        })
        
        self.running_scenarios[scenario.id]["events_processed"] += 1

        # Simulate character interactions
        for i, responder in enumerate(scenario.expected_characters[1:], 1):
            await asyncio.sleep(1 / speed_multiplier)
            
            original_poster = scenario.expected_characters[i-1]
            
            await n8n_service.emit_event("interaction_triggered", {
                "responder": responder,
                "original_poster": original_poster,
                "interaction_type": "agreement" if i % 2 == 0 else "addition",
                "conversation_context": f"Response to {original_poster}'s post about {scenario.title}",
                "relationship_dynamic": "supportive"
            })
            
            self.running_scenarios[scenario.id]["events_processed"] += 1

    async def process_custom_news(self, title: str, content: str, topics: List[str]):
        """Process custom news for real-time demonstration"""
        logger.info(f"Processing custom news: {title}")
        
        # Emit news discovered event
        await n8n_service.emit_event("news_discovered", {
            "title": title,
            "source": "Custom Demo News",
            "topics": topics,
            "urgency_score": 0.7,
            "cultural_relevance": 0.8,
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        })

    def stop_all_scenarios(self):
        """Stop all running demo scenarios"""
        for scenario_id in list(self.running_scenarios.keys()):
            self.running_scenarios[scenario_id]["status"] = "stopped"
            logger.info(f"Stopped demo scenario: {scenario_id}")

    def get_running_scenarios(self) -> List[str]:
        """Get list of currently running scenario IDs"""
        return list(self.running_scenarios.keys())

    def get_event_count(self) -> int:
        """Get total event count"""
        return n8n_service.event_count

    async def check_n8n_connection(self) -> bool:
        """Check if N8N is connected"""
        return await n8n_service.test_connection()

    def get_demo_status(self) -> Dict[str, Any]:
        """Get current demo status"""
        return {
            "demo_mode_enabled": self.demo_mode,
            "n8n_connected": False,  # Will be updated by async call
            "running_scenarios": self.get_running_scenarios(),
            "total_events_sent": self.get_event_count(),
            "last_event_time": n8n_service.last_event_time.isoformat() if n8n_service.last_event_time else None,
            "active_session_id": settings.DEMO_SESSION_ID
        }

# Global instance
demo_orchestrator = DemoOrchestrator() 