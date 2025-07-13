# Personality Architecture

## Overview

This document explains the separation of concerns between **Agent Behavior** and **Personality Data** in the Puerto Rican AI character system.

## Architecture Components

### 1. Personality Port (`app/ports/personality_port.py`)

The `PersonalityPort` interface defines the contract that all personality implementations must follow:

```python
class PersonalityPort(ABC):
    @property
    def character_id(self) -> str: ...

    @property
    def character_name(self) -> str: ...

    @abstractmethod
    def get_topic_relevance(self, topics: List[str]) -> float: ...

    @abstractmethod
    def get_emotional_context(self, content: str) -> str: ...

    @abstractmethod
    def should_engage_in_controversy(self, content: str) -> bool: ...

    @abstractmethod
    def get_character_context(self, base_context: str) -> str: ...

    @abstractmethod
    def calculate_engagement_boost(self, content: str) -> Dict[str, float]: ...
```

### 2. Personality Data Models (`app/models/personality.py`)

Contains the static data structures (`PersonalityData`) that define character traits, preferences, and configuration:

- Basic identity (name, type, traits)
- Engagement configuration (thresholds, cooldowns)
- Topic preferences and weights
- Language patterns and signature phrases
- Cultural references and local knowledge

### 3. Personality Implementations (`app/models/personalities/`)

Concrete implementations of `PersonalityPort` for each character:

- `jovani_vazquez_personality.py` - Jovani's specific personality logic
- Future: `politico_boricua_personality.py`, `ciudadano_boricua_personality.py`, etc.

### 4. Agent Classes (`app/agents/`)

Agent classes focus on **behavior logic** and **orchestration**:

- `BaseCharacterAgent` - Common agent functionality
- `JovaniVazquezAgent` - Jovani-specific agent behavior

## Separation of Concerns

### Personality Port Responsibilities

✅ **What Personality Ports Handle:**

- Character identity and traits
- Topic relevance calculations
- Emotional context determination
- Controversy engagement decisions
- Response templates and examples
- Character-specific context generation
- Fallback responses
- Engagement boost calculations

❌ **What Personality Ports DON'T Handle:**

- AI provider interactions
- State management
- Rate limiting
- Conversation flow
- Decision orchestration

### Agent Responsibilities

✅ **What Agents Handle:**

- AI provider integration
- State management and tracking
- Rate limiting and cooldowns
- Decision orchestration
- Response generation workflow
- Error handling and fallbacks
- Performance monitoring

❌ **What Agents DON'T Handle:**

- Character personality logic
- Topic relevance calculations
- Emotional context analysis
- Response content generation

## Benefits of This Architecture

### 1. **Testability**

- Personality logic can be tested independently
- Agent behavior can be tested with mock personalities
- Clear interfaces make unit testing straightforward

### 2. **Maintainability**

- Personality changes don't affect agent logic
- Agent improvements don't require personality changes
- Clear separation makes debugging easier

### 3. **Extensibility**

- New characters only need a personality implementation
- Agent improvements benefit all characters
- Personality logic can be shared between characters

### 4. **Flexibility**

- Personalities can be swapped at runtime
- Multiple personality variants for the same character
- Easy to create personality hybrids or variations

## Usage Examples

### Creating a Character Agent

```python
# Using default personality
agent = create_jovani_vazquez(ai_provider=my_ai_provider)

# Using custom personality
custom_personality = JovaniVazquezPersonality()
agent = create_jovani_vazquez(
    ai_provider=my_ai_provider,
    personality=custom_personality
)
```

### Testing Personality Logic

```python
# Test personality logic independently
personality = create_jovani_personality()
relevance = personality.get_topic_relevance(["music", "entertainment"])
assert relevance > 0.8

emotional_context = personality.get_emotional_context("New music festival in PR!")
assert emotional_context == "excited"
```

### Testing Agent Behavior

```python
# Test agent with mock personality
mock_personality = MockPersonality()
agent = JovaniVazquezAgent(personality=mock_personality)

decision = await agent.make_engagement_decision(state, context)
assert decision == AgentDecision.ENGAGE
```

## Migration Guide

### From Old Architecture

**Before:**

```python
class JovaniVazquezAgent(BaseCharacterAgent):
    def calculate_engagement_probability(self, context, ...):
        # Direct access to self.personality_data
        topic_weights = self.personality_data.topic_weights
        # Complex logic mixed with personality data
```

**After:**

```python
class JovaniVazquezAgent(BaseCharacterAgent):
    def calculate_engagement_probability(self, context, ...):
        # Delegate to personality
        boosts = self.personality.calculate_engagement_boost(context)
        topic_boost = self.personality.get_topic_relevance(topics) * 0.3
        # Clean separation of concerns
```

### Adding New Characters

1. **Create Personality Data** in `app/models/personality.py`
2. **Implement Personality Port** in `app/models/personalities/`
3. **Create Agent Class** in `app/agents/`
4. **Add to Factory** in `app/models/personalities/personality_factory.py`

## Future Enhancements

### 1. **Personality Composition**

```python
# Mix personality traits
base_personality = BasePuertoRicanPersonality()
influencer_traits = InfluencerPersonalityTraits()
jovani_personality = CompositePersonality([base_personality, influencer_traits])
```

### 2. **Dynamic Personality Adaptation**

```python
# Personality that adapts based on context
adaptive_personality = AdaptivePersonality(
    base_personality=create_jovani_personality(),
    adaptation_rules=personality_adaptation_rules
)
```

### 3. **Personality Validation**

```python
# Validate personality consistency
validator = PersonalityValidator()
issues = validator.validate(jovani_personality)
assert len(issues) == 0
```

## Conclusion

This architecture provides a clean separation between **what** a character is (personality) and **how** they behave (agent), making the system more maintainable, testable, and extensible.
