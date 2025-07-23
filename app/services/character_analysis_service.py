"""
Character Analysis Service

Provides character engagement analysis and decision-making functionality.
This service analyzes how characters would engage with news content based on their personalities.
"""
import logging
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from pydantic import BaseModel

from app.services.personality_config_loader import PersonalityConfigLoader
from app.models.character_analysis_models import (
    NewsContent, AnalysisOptions, TopicMatch, CharacterAnalysis,
    NewsSummary, EngagementAnalysisResponse
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisSession:
    """Represents an active analysis session."""
    session_id: str
    news_content: NewsContent
    characters: List[str]
    created_at: datetime
    status: str = "pending"  # pending, analyzing, complete, expired
    results: Optional[EngagementAnalysisResponse] = None


class CharacterAnalysisService:
    """
    Service for analyzing character engagement with news content.
    
    This service provides:
    - Character engagement analysis
    - Topic matching and scoring
    - Engagement decision reasoning
    - Streaming analysis sessions
    """
    
    def __init__(self):
        """Initialize the character analysis service."""
        self._sessions: Dict[str, AnalysisSession] = {}
        self._session_timeout = 300  # 5 minutes
        
    async def analyze_engagement(
        self, 
        news_content: NewsContent, 
        characters: List[str], 
        options: AnalysisOptions
    ) -> EngagementAnalysisResponse:
        """
        Analyze character engagement for given news content.
        
        Args:
            news_content: The news content to analyze
            characters: List of character IDs to analyze
            options: Analysis options
            
        Returns:
            EngagementAnalysisResponse with analysis results
        """
        try:
            # Get personality configurations
            from app.services.dependency_container import get_container
            container = get_container()
            personality_loader = container.get_personality_config_loader()
            
            # Analyze news content
            news_summary = await self._analyze_news_content(news_content)
            
            # Analyze each character
            character_analyses = []
            for character_id in characters:
                try:
                    character_config = personality_loader.load_personality(character_id)
                    analysis = await self._analyze_character_engagement(
                        character_id, character_config, news_content, news_summary, options
                    )
                    character_analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Error analyzing character {character_id}: {e}")
                    # Create error analysis
                    analysis = CharacterAnalysis(
                        character_id=character_id,
                        character_name=character_id,
                        engagement_decision="ignore",
                        engagement_score=0.0,
                        reasoning=f"Error analyzing character: {str(e)}",
                        topic_matches=[],
                        predicted_response_tone=None,
                        confidence=0.0
                    )
                    character_analyses.append(analysis)
            
            # Create response
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
            return EngagementAnalysisResponse(
                analysis_id=analysis_id,
                news_summary=news_summary,
                character_analyses=character_analyses
            )
            
        except Exception as e:
            logger.error(f"Error in engagement analysis: {e}")
            raise
    
    async def create_analysis_session(
        self, 
        news_content: NewsContent, 
        characters: List[str]
    ) -> str:
        """
        Create a new analysis session for streaming.
        
        Args:
            news_content: The news content to analyze
            characters: List of character IDs to analyze
            
        Returns:
            Session ID for tracking
        """
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        session = AnalysisSession(
            session_id=session_id,
            news_content=news_content,
            characters=characters,
            created_at=datetime.now(timezone.utc)
        )
        
        self._sessions[session_id] = session
        
        # Start analysis in background
        asyncio.create_task(self._run_session_analysis(session_id))
        
        logger.info(f"Created analysis session: {session_id}")
        return session_id
    
    async def get_analysis_stream(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get streaming analysis updates for a session.
        
        Args:
            session_id: The session ID to get updates for
            
        Returns:
            List of streaming updates
            
        Raises:
            ValueError: If session not found or expired
        """
        if session_id not in self._sessions:
            raise ValueError("Session not found")
        
        session = self._sessions[session_id]
        
        # Check if session has expired
        if (datetime.now(timezone.utc) - session.created_at).total_seconds() > self._session_timeout:
            session.status = "expired"
            raise ValueError("Session expired")
        
        # Generate streaming updates based on session status
        updates = []
        
        if session.status == "pending":
            updates.append({
                "event": "analysis_started",
                "data": {
                    "message": "Starting character analysis",
                    "characters": session.characters,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            })
        
        elif session.status == "analyzing":
            updates.append({
                "event": "character_analyzing",
                "data": {
                    "message": "Analyzing character engagement",
                    "progress": 50,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            })
        
        elif session.status == "complete" and session.results:
            updates.append({
                "event": "analysis_complete",
                "data": {
                    "message": "Analysis complete",
                    "results": session.results.dict(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            })
        
        return updates
    
    async def _analyze_news_content(self, news_content: NewsContent) -> NewsSummary:
        """
        Analyze news content to extract topics, sentiment, and cultural relevance.
        
        Args:
            news_content: The news content to analyze
            
        Returns:
            NewsSummary with analysis results
        """
        # Simple topic detection based on keywords
        detected_topics = self._detect_topics(news_content.title + " " + news_content.content)
        
        # Simple sentiment analysis
        sentiment = self._analyze_sentiment(news_content.title + " " + news_content.content)
        
        # Cultural relevance based on Puerto Rican context
        cultural_relevance = self._calculate_cultural_relevance(
            news_content.title + " " + news_content.content
        )
        
        return NewsSummary(
            title=news_content.title,
            detected_topics=detected_topics,
            sentiment=sentiment,
            cultural_relevance=cultural_relevance
        )
    
    async def _analyze_character_engagement(
        self,
        character_id: str,
        character_config: Dict[str, Any],
        news_content: NewsContent,
        news_summary: NewsSummary,
        options: AnalysisOptions
    ) -> CharacterAnalysis:
        """
        Analyze how a specific character would engage with the news.
        
        Args:
            character_id: The character ID
            character_config: The character's personality configuration
            news_content: The news content
            news_summary: The news analysis summary
            options: Analysis options
            
        Returns:
            CharacterAnalysis with engagement results
        """
        # Get character topics of interest
        character_topics = character_config.get("topics_of_interest", [])
        
        # Calculate topic matches
        topic_matches = []
        total_topic_score = 0.0
        
        for topic in character_topics:
            weight = self._calculate_topic_weight(topic, character_config)
            matched = topic in news_summary.detected_topics
            score = weight if matched else 0.0
            total_topic_score += score
            
            topic_matches.append(TopicMatch(
                topic=topic,
                weight=weight,
                matched=matched
            ))
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(
            total_topic_score,
            news_summary.cultural_relevance,
            character_config
        )
        
        # Make engagement decision
        engagement_decision = "engage" if engagement_score > 0.6 else "ignore"
        
        # Generate reasoning if requested
        reasoning = None
        if options.include_reasoning:
            reasoning = self._generate_engagement_reasoning(
                character_config,
                topic_matches,
                engagement_score,
                news_summary
            )
        
        # Predict response tone if requested
        predicted_response_tone = None
        if options.generate_responses and engagement_decision == "engage":
            predicted_response_tone = self._predict_response_tone(
                character_config,
                engagement_score,
                news_summary
            )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            topic_matches,
            engagement_score,
            character_config
        )
        
        return CharacterAnalysis(
            character_id=character_id,
            character_name=character_config.get("character_name", character_id),
            engagement_decision=engagement_decision,
            engagement_score=engagement_score,
            reasoning=reasoning,
            topic_matches=topic_matches if options.include_topic_analysis else [],
            predicted_response_tone=predicted_response_tone,
            confidence=confidence
        )
    
    async def _run_session_analysis(self, session_id: str):
        """Run analysis for a session in the background."""
        try:
            session = self._sessions[session_id]
            session.status = "analyzing"
            
            # Perform analysis
            options = AnalysisOptions(include_reasoning=True, include_topic_analysis=True)
            results = await self.analyze_engagement(
                session.news_content,
                session.characters,
                options
            )
            
            session.results = results
            session.status = "complete"
            
            logger.info(f"Completed analysis for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error in session analysis {session_id}: {e}")
            session.status = "error"
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics in text based on keywords."""
        text_lower = text.lower()
        topics = []
        
        # Define topic keywords
        topic_keywords = {
            "music": ["música", "concierto", "artista", "cantante", "bad bunny", "reggaeton"],
            "sports": ["deportes", "basketball", "vaqueros", "bsn", "campeonato", "equipo"],
            "politics": ["política", "gobierno", "elecciones", "candidato", "partido"],
            "family": ["familia", "hijos", "padres", "casa", "hogar"],
            "work_life": ["trabajo", "empleo", "oficina", "negocio", "empresa"],
            "puerto_rico": ["puerto rico", "isla", "boricua", "san juan", "bayamón"],
            "entertainment": ["entretenimiento", "película", "televisión", "show"],
            "local_news": ["local", "comunidad", "barrio", "municipio"],
            "vaqueros_basketball": ["vaqueros", "bayamón", "basketball", "bsn", "campeonato"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis."""
        text_lower = text.lower()
        
        positive_words = ["ganó", "éxito", "victoria", "feliz", "bueno", "excelente", "mejor"]
        negative_words = ["perdió", "fracaso", "problema", "triste", "malo", "terrible", "peor"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_cultural_relevance(self, text: str) -> float:
        """Calculate cultural relevance to Puerto Rican context."""
        text_lower = text.lower()
        
        pr_keywords = [
            "puerto rico", "boricua", "san juan", "bayamón", "vaqueros", 
            "bsn", "reggaeton", "bad bunny", "isla", "caribe"
        ]
        
        relevance_score = 0.0
        for keyword in pr_keywords:
            if keyword in text_lower:
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _calculate_topic_weight(self, topic: str, character_config: Dict[str, Any]) -> float:
        """Calculate the weight of a topic for a character."""
        # Base weight from character configuration
        base_weight = character_config.get("topic_weights", {}).get(topic, 0.5)
        
        # Adjust based on character type
        character_type = character_config.get("character_type", "unknown")
        if character_type == "influencer" and topic in ["music", "entertainment"]:
            base_weight *= 1.2
        elif character_type == "citizen" and topic in ["local_news", "family"]:
            base_weight *= 1.2
        
        return min(base_weight, 1.0)
    
    def _calculate_engagement_score(
        self,
        topic_score: float,
        cultural_relevance: float,
        character_config: Dict[str, Any]
    ) -> float:
        """Calculate overall engagement score."""
        # Base engagement from topic matching
        engagement = topic_score * 0.6
        
        # Add cultural relevance bonus
        engagement += cultural_relevance * 0.3
        
        # Add character energy bonus
        base_energy = character_config.get("base_energy", 0.5)
        engagement += base_energy * 0.1
        
        return min(engagement, 1.0)
    
    def _generate_engagement_reasoning(
        self,
        character_config: Dict[str, Any],
        topic_matches: List[TopicMatch],
        engagement_score: float,
        news_summary: NewsSummary
    ) -> str:
        """Generate reasoning for engagement decision."""
        character_name = character_config.get("character_name", "Character")
        
        if engagement_score > 0.6:
            matched_topics = [tm.topic for tm in topic_matches if tm.matched]
            if matched_topics:
                return f"High relevance to {', '.join(matched_topics)} topics, matches {character_name}'s interests"
            else:
                return f"High cultural relevance ({news_summary.cultural_relevance:.1f}), aligns with {character_name}'s background"
        else:
            return f"Low relevance to {character_name}'s interests, not engaging with this content"
    
    def _predict_response_tone(
        self,
        character_config: Dict[str, Any],
        engagement_score: float,
        news_summary: NewsSummary
    ) -> str:
        """Predict the tone of character's response."""
        character_type = character_config.get("character_type", "unknown")
        base_energy = character_config.get("base_energy", 0.5)
        
        if character_type == "influencer" and base_energy > 0.7:
            return "enthusiastic_performative"
        elif character_type == "citizen" and engagement_score > 0.8:
            return "passionate_community"
        else:
            return "neutral_observational"
    
    def _calculate_confidence(
        self,
        topic_matches: List[TopicMatch],
        engagement_score: float,
        character_config: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the analysis."""
        # Base confidence from topic matching strength
        matched_topics = [tm for tm in topic_matches if tm.matched]
        topic_confidence = sum(tm.weight for tm in matched_topics) / len(topic_matches) if topic_matches else 0.0
        
        # Adjust based on engagement score clarity
        score_confidence = 1.0 - abs(engagement_score - 0.5) * 2  # Higher confidence for extreme scores
        
        # Character configuration completeness
        config_confidence = 0.8 if character_config.get("topics_of_interest") else 0.5
        
        return (topic_confidence + score_confidence + config_confidence) / 3 