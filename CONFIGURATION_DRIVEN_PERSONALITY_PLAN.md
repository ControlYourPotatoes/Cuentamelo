# Configuration-Driven Personality System Implementation Plan

## Project Context

### Current Architecture Overview

This project is a Puerto Rican AI character system called "Cuentamelo" that creates AI-powered social media personalities. The system uses LangGraph for orchestration and has multiple AI agents with different personalities.

### Current Personality System Issues

- **Hardcoded Data**: Personality data is hardcoded in factory functions
- **Massive Data Structures**: `PersonalityData` contains all possible fields even when not needed
- **Poor Separation**: No clear separation between rich data source and minimal views
- **Difficult to Modify**: Changing personality requires code changes

### Current File Structure

```
app/
├── models/
│   ├── personality.py (legacy adapter with minimal factory)
│   ├── ai_personality_data.py (minimal AI data structure)
│   └── agent_personality_data.py (minimal agent data structure)
├── ports/
│   └── personality_port.py (interface for personality access)
├── agents/
│   ├── base_character.py (base agent class)
│   └── jovani_vazquez.py (Jovani agent implementation)
├── adapters/
│   └── claude_ai_adapter.py (AI provider using personality data)
└── services/
    └── dependency_container.py (service wiring)
```

### Current Data Flow

```
Factory Function → PersonalityData → PersonalityPort → AIPersonalityData/AgentPersonalityData
```

### Target Data Flow

```
JSON Config → ConfigLoader → PersonalityPort → AIPersonalityData/AgentPersonalityData
```

## Implementation Plan

### Phase 1: Directory Structure & JSON Schema

#### 1.1 Create Configuration Directory

```
configs/
├── personalities/
│   ├── jovani_vazquez.json
│   ├── politico_boricua.json (future)
│   └── schema.json (for validation)
└── __init__.py
```

#### 1.2 JSON Schema Design

```json
{
  "character_id": "string (required)",
  "character_name": "string (required)",
  "character_type": "string (required)",
  "personality": {
    "traits": "string (required)",
    "background": "string (required)",
    "language_style": "enum (spanglish, formal_spanish, etc.)",
    "interaction_style": "string (required)",
    "cultural_context": "string (required)"
  },
  "engagement": {
    "threshold": "float (0.0-1.0)",
    "cooldown_minutes": "integer",
    "max_daily_interactions": "integer",
    "max_replies_per_thread": "integer"
  },
  "topics": {
    "of_interest": ["string array"],
    "weights": { "topic": "float (0.0-1.0)" },
    "preferred": ["string array"],
    "avoided": ["string array"]
  },
  "language": {
    "signature_phrases": ["string array"],
    "common_expressions": ["string array"],
    "emoji_preferences": ["string array"],
    "patterns": { "context": "string" }
  },
  "responses": {
    "examples": { "topic": ["string array"] },
    "templates": { "type": "string" }
  },
  "energy": {
    "base_level": "float (0.0-1.0)",
    "tone_preferences": { "context": "enum" },
    "emotional_triggers": { "topic": "float" }
  },
  "cultural": {
    "puerto_rico_references": ["string array"],
    "local_places": ["string array"],
    "cultural_events": ["string array"],
    "local_foods": ["string array"]
  },
  "behavior": {
    "hashtag_style": "string",
    "mention_behavior": "string",
    "retweet_preferences": ["string array"],
    "thread_behavior": "string"
  },
  "validation": {
    "personality_consistency_rules": ["string array"],
    "content_guidelines": ["string array"]
  }
}
```

### Phase 2: Configuration Loader Service

#### 2.1 Create `app/services/personality_config_loader.py`

```python
class PersonalityConfigLoader:
    def __init__(self, config_dir: str = "configs/personalities"):
        self.config_dir = config_dir
        self._cache = {}

    def load_personality(self, character_id: str) -> Dict:
        """Load personality configuration from JSON file."""

    def load_all_personalities(self) -> Dict[str, Dict]:
        """Load all personality configurations."""

    def validate_config(self, config: Dict) -> bool:
        """Validate configuration against schema."""

    def get_config_path(self, character_id: str) -> str:
        """Get file path for character configuration."""
```

#### 2.2 Features Required

- JSON file loading with error handling
- Caching for performance
- Validation against schema
- Fallback to default values
- Logging for debugging
- Type hints and documentation

### Phase 3: Update Data Models

#### 3.1 Modify `app/models/ai_personality_data.py`

Add factory method:

```python
@classmethod
def create_from_config(cls, config: Dict) -> 'AIPersonalityData':
    """Create AIPersonalityData from configuration dictionary."""
    personality = config.get('personality', {})
    language = config.get('language', {})
    responses = config.get('responses', {})
    energy = config.get('energy', {})
    cultural = config.get('cultural', {})
    validation = config.get('validation', {})

    return cls(
        character_id=config['character_id'],
        character_name=config['character_name'],
        character_type=config['character_type'],
        personality_traits=personality.get('traits', ''),
        background=personality.get('background', ''),
        language_style=personality.get('language_style', 'spanglish'),
        interaction_style=personality.get('interaction_style', ''),
        cultural_context=personality.get('cultural_context', ''),
        signature_phrases=language.get('signature_phrases', []),
        common_expressions=language.get('common_expressions', []),
        emoji_preferences=language.get('emoji_preferences', []),
        topics_of_interest=config.get('topics', {}).get('of_interest', []),
        example_responses=responses.get('examples', {}),
        response_templates=responses.get('templates', {}),
        base_energy_level=energy.get('base_level', 0.5),
        puerto_rico_references=cultural.get('puerto_rico_references', []),
        personality_consistency_rules=validation.get('personality_consistency_rules', [])
    )
```

#### 3.2 Modify `app/models/agent_personality_data.py`

Add factory method:

```python
@classmethod
def create_from_config(cls, config: Dict) -> 'AgentPersonalityData':
    """Create AgentPersonalityData from configuration dictionary."""
    engagement = config.get('engagement', {})
    topics = config.get('topics', {})
    personality = config.get('personality', {})
    language = config.get('language', {})

    return cls(
        character_id=config['character_id'],
        character_name=config['character_name'],
        character_type=config['character_type'],
        engagement_threshold=engagement.get('threshold', 0.5),
        cooldown_minutes=engagement.get('cooldown_minutes', 15),
        max_daily_interactions=engagement.get('max_daily_interactions', 50),
        max_replies_per_thread=engagement.get('max_replies_per_thread', 2),
        topics_of_interest=topics.get('of_interest', []),
        topic_weights=topics.get('weights', {}),
        preferred_topics=topics.get('preferred', []),
        avoided_topics=topics.get('avoided', []),
        personality_traits=personality.get('traits', ''),
        signature_phrases=language.get('signature_phrases', [])
    )
```

#### 3.3 Update `app/models/personality.py`

Add factory method for backward compatibility:

```python
@classmethod
def create_from_config(cls, config: Dict) -> 'PersonalityData':
    """Create PersonalityData from configuration dictionary for backward compatibility."""
    # Map all config fields to PersonalityData structure
    # This ensures existing code continues to work
```

### Phase 4: Update Personality Port Implementation

#### 4.1 Modify `app/agents/jovani_vazquez_personality.py`

Update to use config loader:

```python
class JovaniVazquezPersonality(PersonalityPort):
    def __init__(self, config_loader: PersonalityConfigLoader):
        self.config_loader = config_loader
        self._config = config_loader.load_personality("jovani_vazquez")
        self._ai_data = AIPersonalityData.create_from_config(self._config)
        self._agent_data = AgentPersonalityData.create_from_config(self._config)

    # Implement all port methods using self._config data
```

#### 4.2 Update factory function in `app/models/personality.py`

Replace hardcoded data:

```python
def create_jovani_vazquez_personality() -> PersonalityData:
    """Create Jovani Vázquez personality configuration from JSON config."""
    config_loader = PersonalityConfigLoader()
    config = config_loader.load_personality("jovani_vazquez")
    return PersonalityData.create_from_config(config)
```

### Phase 5: Dependency Injection Updates

#### 5.1 Update `app/services/dependency_container.py`

```python
class DependencyContainer:
    def __init__(self):
        # Register configuration loader
        self.personality_config_loader = PersonalityConfigLoader()

        # Update personality factory
        self.personality_factory = lambda: self.personality_config_loader

        # Register with existing services
        # ... existing registrations
```

### Phase 6: Testing & Validation

#### 6.1 Create test files

- `tests/test_personality_config_loader.py`
- `tests/test_config_validation.py`
- `tests/integration/test_config_driven_personality.py`

#### 6.2 Test scenarios

- Valid config loading
- Invalid config handling
- Missing config fallback
- Performance with caching
- Backward compatibility
- AI provider integration
- Agent behavior integration

### Phase 7: Migration Strategy

#### 7.1 Backward Compatibility

- Keep existing factory functions working
- Gradual migration to config-driven approach
- Deprecation warnings for old approach

#### 7.2 Configuration Migration

- Move existing hardcoded data to JSON
- Validate all existing functionality works
- Update documentation

## Key Implementation Details

### Error Handling

- Graceful fallback if config file missing
- Validation errors with clear messages
- Logging for debugging configuration issues

### Performance Considerations

- Cache loaded configurations
- Lazy loading of config data
- Efficient JSON parsing

### Security

- Validate JSON structure
- Sanitize loaded data
- Prevent path traversal attacks

### Testing Strategy

- Unit tests for config loader
- Integration tests with existing components
- Performance tests for caching
- Error handling tests

## Success Criteria

✅ **No Hard Coupling** - Data is external to code
✅ **Easy Modification** - Edit JSON files without code changes  
✅ **Rich Data Source** - Can store comprehensive personality data
✅ **Minimal Views** - Extract only what each component needs
✅ **Testable** - Can mock different configs easily
✅ **Scalable** - Easy to add new characters
✅ **Backward Compatible** - Existing code continues to work
✅ **Performance** - No significant performance degradation
✅ **Error Resilient** - Graceful handling of config errors

## Files to Create/Modify

### New Files

- `configs/personalities/jovani_vazquez.json`
- `configs/personalities/schema.json`
- `app/services/personality_config_loader.py`

### Modified Files

- `app/models/ai_personality_data.py`
- `app/models/agent_personality_data.py`
- `app/models/personality.py`
- `app/agents/jovani_vazquez_personality.py`
- `app/services/dependency_container.py`

### Test Files

- `tests/test_personality_config_loader.py`
- `tests/test_config_validation.py`
- `tests/integration/test_config_driven_personality.py`

## Context for Implementation

### Current Personality Data Structure

The current system has these key data structures:

- `PersonalityData`: Complete personality configuration (legacy)
- `AIPersonalityData`: Minimal data for AI providers
- `AgentPersonalityData`: Minimal data for agent behavior

### Current Usage Patterns

- AI providers use `AIPersonalityData` for generation
- Agents use `AgentPersonalityData` for behavior decisions
- Legacy code uses `PersonalityData` for backward compatibility

### Integration Points

- `claude_ai_adapter.py` uses personality data for AI generation
- `jovani_vazquez.py` agent uses personality for behavior
- `dependency_container.py` wires everything together
- Tests verify personality functionality

This plan provides a clean, flexible system where personality data can be easily modified in JSON files while maintaining the minimal data approach for different components.
