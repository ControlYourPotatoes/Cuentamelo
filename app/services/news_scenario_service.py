"""
News Scenario Service

Provides news scenario management and custom news processing functionality.
This service handles predefined scenarios and user-provided news content.
"""
import logging
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.models.character_analysis_models import CustomNewsRequest, CustomNewsResponse, ProcessingMetadata, FormattedContent

logger = logging.getLogger(__name__)


class NewsScenarioService:
    """
    Service for managing news scenarios and processing custom news content.
    
    This service provides:
    - Predefined news scenarios for analysis
    - Custom news content processing
    - Content validation and enrichment
    - Topic detection and sentiment analysis
    """
    
    def __init__(self):
        """Initialize the news scenario service."""
        self._scenarios = self._load_predefined_scenarios()
    
    async def get_scenarios(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available news scenarios for analysis.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of scenario dictionaries
        """
        scenarios = self._scenarios
        
        # Filter by category if specified
        if category:
            scenarios = [
                scenario for scenario in scenarios 
                if scenario.get("category") == category
            ]
        
        return scenarios
    
    async def process_custom_news(self, request: CustomNewsRequest) -> CustomNewsResponse:
        """
        Process custom news content for analysis.
        
        Args:
            request: Custom news request with title and content
            
        Returns:
            CustomNewsResponse with processed content
            
        Raises:
            ValueError: If content is invalid
        """
        try:
            # Validate content
            self._validate_news_content(request.title, request.content)
            
            # Process and enrich content
            processed_content = await self._process_news_content(request)
            
            # Generate unique ID
            news_id = f"custom_{uuid.uuid4().hex[:8]}"
            
            return CustomNewsResponse(
                news_id=news_id,
                formatted_content=processed_content
            )
            
        except Exception as e:
            logger.error(f"Error processing custom news: {e}")
            raise ValueError(f"Failed to process news content: {str(e)}")
    
    def _load_predefined_scenarios(self) -> List[Dict[str, Any]]:
        """Load predefined news scenarios."""
        return [
            {
                "scenario_id": "vaqueros_championship",
                "title": "Vaqueros Win BSN Championship",
                "content": "Los Vaqueros de Bayamón conquistaron su campeonato número 17 en la historia del Baloncesto Superior Nacional (BSN) tras vencer a los Leones de Ponce en una serie emocionante que llegó hasta el séptimo juego. El equipo dirigido por Nelson Colón logró la victoria definitiva con un marcador de 89-85 en el Coliseo Rubén Rodríguez de Bayamón, ante más de 12,000 aficionados que celebraron la conquista del título más importante del baloncesto puertorriqueño.",
                "category": "sports",
                "relevance_score": 0.95,
                "expected_engagement": {
                    "jovani_vazquez": 0.7,
                    "ciudadano_bayamon": 0.95
                },
                "tags": ["vaqueros", "bsn", "basketball", "championship", "bayamón"],
                "source": "predefined",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "scenario_id": "bad_bunny_concert",
                "title": "Bad Bunny Announces Surprise Concert in San Juan",
                "content": "El artista puertorriqueño Bad Bunny sorprendió a sus seguidores al anunciar un concierto sorpresa en el Coliseo de Puerto Rico José Miguel Agrelot en San Juan. El evento, programado para el próximo mes, será parte de su gira mundial y contará con invitados especiales de la música urbana latina. Las entradas se agotaron en menos de una hora, demostrando el enorme apoyo de los boricuas hacia el artista que ha puesto a Puerto Rico en el mapa de la música internacional.",
                "category": "entertainment",
                "relevance_score": 0.9,
                "expected_engagement": {
                    "jovani_vazquez": 0.95,
                    "ciudadano_bayamon": 0.3
                },
                "tags": ["bad bunny", "concierto", "música", "san juan", "entretenimiento"],
                "source": "predefined",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "scenario_id": "political_announcement",
                "title": "Nuevo Candidato Anuncia Campaña para Gobernador",
                "content": "Un nuevo candidato independiente anunció oficialmente su campaña para la gobernación de Puerto Rico durante un evento en el Viejo San Juan. El candidato, quien tiene experiencia en el sector privado y comunitario, presentó su plataforma enfocada en la economía local, la educación y la transparencia gubernamental. El anuncio generó expectativa en la población, especialmente entre los votantes que buscan alternativas a los partidos tradicionales.",
                "category": "politics",
                "relevance_score": 0.85,
                "expected_engagement": {
                    "jovani_vazquez": 0.4,
                    "ciudadano_bayamon": 0.8
                },
                "tags": ["política", "elecciones", "gobernador", "campaña", "puerto rico"],
                "source": "predefined",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "scenario_id": "community_festival",
                "title": "Festival Cultural Celebra Tradiciones Boricuas",
                "content": "El Festival Cultural de Bayamón celebró exitosamente su décima edición, reuniendo a miles de familias para celebrar las tradiciones puertorriqueñas. El evento incluyó presentaciones de música típica, artesanías locales, gastronomía tradicional y actividades para niños. Los organizadores destacaron la importancia de preservar la cultura boricua y fortalecer los lazos comunitarios en tiempos de cambio.",
                "category": "local_news",
                "relevance_score": 0.75,
                "expected_engagement": {
                    "jovani_vazquez": 0.6,
                    "ciudadano_bayamon": 0.85
                },
                "tags": ["festival", "cultura", "bayamón", "tradiciones", "comunidad"],
                "source": "predefined",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "scenario_id": "economic_development",
                "title": "Nueva Empresa Tecnológica Se Establece en Puerto Rico",
                "content": "Una empresa tecnológica internacional anunció la apertura de su nueva sede en Puerto Rico, creando más de 200 empleos en el sector de la tecnología. La inversión de $50 millones incluye la construcción de un centro de innovación y programas de capacitación para estudiantes locales. El gobernador destacó que esta iniciativa fortalece la economía local y posiciona a Puerto Rico como un hub tecnológico en el Caribe.",
                "category": "business",
                "relevance_score": 0.8,
                "expected_engagement": {
                    "jovani_vazquez": 0.5,
                    "ciudadano_bayamon": 0.7
                },
                "tags": ["tecnología", "empleos", "economía", "inversión", "desarrollo"],
                "source": "predefined",
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    
    def _validate_news_content(self, title: str, content: str):
        """
        Validate news content for processing.
        
        Args:
            title: News headline
            content: News article content
            
        Raises:
            ValueError: If content is invalid
        """
        if not title or not title.strip():
            raise ValueError("News title cannot be empty")
        
        if not content or len(content.strip()) < 20:
            raise ValueError("News content must be at least 20 characters long")
        
        # Check for inappropriate content
        inappropriate_words = ["spam", "advertisement", "clickbait"]
        text_lower = (title + " " + content).lower()
        
        if any(word in text_lower for word in inappropriate_words):
            raise ValueError("Content appears to be inappropriate or spam")
    
    async def _process_news_content(self, request: CustomNewsRequest) -> FormattedContent:
        """
        Process and enrich news content.
        
        Args:
            request: Custom news request
            
        Returns:
            FormattedContent with enriched data
        """
        # Detect topics
        detected_topics = self._detect_topics(request.title + " " + request.content)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(request.title + " " + request.content)
        
        # Calculate cultural relevance
        cultural_relevance = self._calculate_cultural_relevance(
            request.title + " " + request.content
        )
        
        # Generate processing metadata
        processing_metadata = self._generate_processing_metadata(request.content)
        
        return FormattedContent(
            title=request.title.strip(),
            content=request.content.strip(),
            detected_topics=detected_topics,
            sentiment=sentiment,
            cultural_relevance=cultural_relevance,
            processing_metadata=processing_metadata
        )
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics in text based on keywords."""
        text_lower = text.lower()
        topics = []
        
        # Define topic keywords
        topic_keywords = {
            "music": ["música", "concierto", "artista", "cantante", "bad bunny", "reggaeton", "canción"],
            "sports": ["deportes", "basketball", "vaqueros", "bsn", "campeonato", "equipo", "jugador"],
            "politics": ["política", "gobierno", "elecciones", "candidato", "partido", "votar"],
            "family": ["familia", "hijos", "padres", "casa", "hogar", "niños"],
            "work_life": ["trabajo", "empleo", "oficina", "negocio", "empresa", "carrera"],
            "puerto_rico": ["puerto rico", "isla", "boricua", "san juan", "bayamón", "caribe"],
            "entertainment": ["entretenimiento", "película", "televisión", "show", "celebridad"],
            "local_news": ["local", "comunidad", "barrio", "municipio", "vecinos"],
            "vaqueros_basketball": ["vaqueros", "bayamón", "basketball", "bsn", "campeonato"],
            "business": ["negocio", "empresa", "economía", "inversión", "empleos", "tecnología"],
            "education": ["educación", "escuela", "universidad", "estudiantes", "maestros"],
            "health": ["salud", "médico", "hospital", "enfermedad", "vacuna"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis."""
        text_lower = text.lower()
        
        positive_words = [
            "ganó", "éxito", "victoria", "feliz", "bueno", "excelente", "mejor",
            "celebran", "logró", "avance", "progreso", "innovación", "crecimiento"
        ]
        negative_words = [
            "perdió", "fracaso", "problema", "triste", "malo", "terrible", "peor",
            "crisis", "conflicto", "controversia", "escándalo", "derrota"
        ]
        
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
            "bsn", "reggaeton", "bad bunny", "isla", "caribe", "viejo san juan",
            "coquí", "plena", "bomba", "salsa", "mofongo", "lechón"
        ]
        
        relevance_score = 0.0
        for keyword in pr_keywords:
            if keyword in text_lower:
                relevance_score += 0.08
        
        return min(relevance_score, 1.0)
    
    def _generate_processing_metadata(self, content: str) -> ProcessingMetadata:
        """Generate processing metadata for the content."""
        # Count words
        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)
        
        # Estimate reading time (average 200 words per minute)
        reading_time_minutes = max(1, word_count // 200)
        reading_time = f"{reading_time_minutes} min"
        
        # Detect language (simplified - assume Spanish for Puerto Rican context)
        language = "es-pr"
        
        return ProcessingMetadata(
            word_count=word_count,
            reading_time=reading_time,
            language=language
        ) 