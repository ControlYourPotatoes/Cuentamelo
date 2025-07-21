"""
Personality Configuration Loader Service

Loads personality configurations from JSON files and provides validation.
This service implements the configuration-driven approach for personality data.
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import jsonschema
from jsonschema import ValidationError

logger = logging.getLogger(__name__)


class PersonalityConfigLoader:
    """
    Loads and validates personality configurations from JSON files.
    
    This service provides:
    - JSON file loading with error handling
    - Schema validation
    - Caching for performance
    - Fallback to default values
    - Logging for debugging
    """
    
    def __init__(self, config_dir: str = "configs/personalities"):
        """
        Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing personality configuration files
        """
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict] = {}
        self._schema: Optional[Dict] = None
        
        # Ensure config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Config directory {config_dir} does not exist. Creating it.")
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Personality config loader initialized with directory: {self.config_dir}")
    
    def _load_schema(self) -> Dict:
        """Load the JSON schema for validation."""
        if self._schema is None:
            schema_path = self.config_dir / "schema.json"
            if schema_path.exists():
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self._schema = json.load(f)
                    logger.info("JSON schema loaded successfully")
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Failed to load schema: {e}")
                    self._schema = {}
            else:
                logger.warning("Schema file not found, validation will be skipped")
                self._schema = {}
        
        return self._schema
    
    def _get_config_path(self, character_id: str) -> Path:
        """
        Get the file path for a character configuration.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Path to the configuration file
        """
        return self.config_dir / f"{character_id}.json"
    
    def load_personality(self, character_id: str) -> Dict:
        """
        Load personality configuration from JSON file.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Dictionary containing the personality configuration
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
        """
        # Check cache first
        if character_id in self._cache:
            logger.debug(f"Returning cached config for {character_id}")
            return self._cache[character_id]
        
        config_path = self._get_config_path(character_id)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration for {character_id}")
            
            # Validate configuration
            if not self.validate_config(config):
                raise ValueError(f"Invalid configuration for {character_id}")
            
            # Cache the configuration
            self._cache[character_id] = config
            
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            logger.error(f"Error loading configuration for {character_id}: {e}")
            raise
    
    def load_all_personalities(self) -> Dict[str, Dict]:
        """
        Load all personality configurations.
        
        Returns:
            Dictionary mapping character_id to configuration
        """
        personalities = {}
        
        if not self.config_dir.exists():
            logger.warning(f"Config directory {self.config_dir} does not exist")
            return personalities
        
        for config_file in self.config_dir.glob("*.json"):
            if config_file.name == "schema.json":
                continue
            
            character_id = config_file.stem
            try:
                config = self.load_personality(character_id)
                personalities[character_id] = config
            except Exception as e:
                logger.error(f"Failed to load {character_id}: {e}")
                continue
        
        logger.info(f"Loaded {len(personalities)} personality configurations")
        return personalities
    
    def validate_config(self, config: Dict) -> bool:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        schema = self._load_schema()
        
        if not schema:
            logger.warning("No schema available, skipping validation")
            return True
        
        try:
            jsonschema.validate(instance=config, schema=schema)
            logger.debug("Configuration validation passed")
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
        # Additional validation for signature_phrases
        language = config.get("language", {})
        sig_phrases = language.get("signature_phrases")
        char_type = config.get("character_type", "")
        if sig_phrases is not None:
            if not isinstance(sig_phrases, list):
                logger.error("signature_phrases must be a list if present.")
                return False
            for idx, phrase in enumerate(sig_phrases):
                if not isinstance(phrase, dict):
                    logger.error(f"signature_phrases[{idx}] must be an object.")
                    return False
                if "text" not in phrase or not isinstance(phrase["text"], str):
                    logger.error(f"signature_phrases[{idx}] must have a 'text' field of type string.")
                    return False
                freq = phrase.get("frequency")
                if freq is not None and freq not in ("common", "rare"):
                    logger.error(f"signature_phrases[{idx}] has invalid frequency: {freq}")
                    return False
        # Warn if influencer/entertainer omits signature_phrases
        if char_type in ("influencer", "entertainer") and (not sig_phrases or len(sig_phrases) == 0):
            logger.warning(f"Influencer/entertainer '{config.get('character_id','')}' has no signature_phrases.")
        return True
    
    def get_available_characters(self) -> List[str]:
        """
        Get list of available character IDs.
        
        Returns:
            List of character IDs that have configuration files
        """
        if not self.config_dir.exists():
            return []
        
        characters = []
        for config_file in self.config_dir.glob("*.json"):
            if config_file.name != "schema.json":
                characters.append(config_file.stem)
        
        return characters
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()
        logger.info("Configuration cache cleared")
    
    def reload_config(self, character_id: str) -> Dict:
        """
        Reload a specific configuration, bypassing cache.
        
        Args:
            character_id: The character's unique identifier
            
        Returns:
            Updated configuration dictionary
        """
        # Remove from cache to force reload
        self._cache.pop(character_id, None)
        return self.load_personality(character_id)
    
    def create_default_config(self, character_id: str, character_name: str, character_type: str) -> Dict:
        """
        Create a default configuration template.
        
        Args:
            character_id: The character's unique identifier
            character_name: The character's display name
            character_type: The character's type
            
        Returns:
            Default configuration dictionary
        """
        default_config = {
            "character_id": character_id,
            "character_name": character_name,
            "character_type": character_type,
            "personality": {
                "traits": f"Default personality traits for {character_name}",
                "background": f"Background information for {character_name}",
                "language_style": "spanglish",
                "interaction_style": "Default interaction style",
                "cultural_context": "Puerto Rican cultural context"
            },
            "engagement": {
                "threshold": 0.5,
                "cooldown_minutes": 15,
                "max_daily_interactions": 50,
                "max_replies_per_thread": 2
            },
            "topics": {
                "of_interest": [],
                "weights": {},
                "preferred": [],
                "avoided": []
            },
            "language": {
                "signature_phrases": [],
                "common_expressions": [],
                "emoji_preferences": [],
                "patterns": {}
            },
            "responses": {
                "examples": {},
                "templates": {}
            },
            "energy": {
                "base_level": 0.5,
                "tone_preferences": {},
                "emotional_triggers": {}
            },
            "cultural": {
                "puerto_rico_references": [],
                "local_places": [],
                "cultural_events": [],
                "local_foods": []
            },
            "behavior": {
                "hashtag_style": "natural",
                "mention_behavior": "selective",
                "retweet_preferences": [],
                "thread_behavior": "conversational"
            },
            "validation": {
                "personality_consistency_rules": [],
                "content_guidelines": []
            }
        }
        
        return default_config
    
    def save_config(self, character_id: str, config: Dict) -> bool:
        """
        Save a configuration to file.
        
        Args:
            character_id: The character's unique identifier
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate before saving
            if not self.validate_config(config):
                logger.error(f"Invalid configuration for {character_id}")
                return False
            
            config_path = self._get_config_path(character_id)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self._cache[character_id] = config
            
            logger.info(f"Configuration saved for {character_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration for {character_id}: {e}")
            return False 