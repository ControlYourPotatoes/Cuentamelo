# Agent Architecture Documentation

## Overview

The Cuentamelo project uses a hybrid agent architecture that supports both configuration-driven and custom character agents. This architecture provides flexibility for simple characters while allowing complex custom logic when needed.

## Architecture Components

### 1. Enhanced BaseCharacterAgent

The `BaseCharacterAgent` is no longer abstract and provides default implementations for all personality-driven behavior:

- **Default Engagement Logic**: Uses personality configuration for engagement probability calculation
- **Standard Conversation Momentum**: Implements basic conversation momentum detection
- **Personality Delegation**: Delegates most behavior to the personality implementation
- **Override Support**: Custom agents can override any method for specialized behavior

### 2. ConfigurablePersonality Adapter

The `ConfigurablePersonality` implements the `PersonalityPort` interface using JSON configuration:

- **JSON-Driven**: All personality data comes from configuration files
- **Ports and Adapters**: Clean separation between personality logic and agent behavior
- **Performance Optimized**: Caches personality data for better performance
- **Fallback Support**: Provides sensible defaults for missing configuration

### 3. Simple Agent Factory

The `create_agent()` function provides a unified interface for agent creation:

- **Automatic Detection**: Determines whether to use custom or configurable agents
- **Registry-Based**: Easy to add new custom agents
- **Error Handling**: Graceful fallback when configurations are missing
- **Dependency Injection**: Supports AI provider and personality injection

## Usage Examples

### Creating a Simple Character (Configurable)

For characters that can be fully defined by configuration:

```python
from app.agents.agent_factory import create_agent

# Creates a configurable agent automatically
agent = create_agent("simple_character_id")

# The agent uses enhanced BaseCharacterAgent with ConfigurablePersonality
print(f"Agent type: {type(agent)}")  # BaseCharacterAgent
print(f"Character: {agent.character_name}")
```

### Creating a Complex Character (Custom)

For characters that need custom logic:

```python
from app.agents.agent_factory import create_agent

# Creates a custom agent (like Jovani)
agent = create_agent("jovani_vazquez")

# The agent uses custom JovaniVazquezAgent
print(f"Agent type: {type(agent)}")  # JovaniVazquezAgent
print(f"Character: {agent.character_name}")
```

### Creating Agents with Dependencies

```python
from app.agents.agent_factory import create_agent
from app.adapters.claude_ai_adapter import ClaudeAIAdapter

# Create with AI provider
ai_provider = ClaudeAIAdapter()
agent = create_agent("character_id", ai_provider=ai_provider)

# Create with custom personality
from app.models.personalities.configurable_personality import create_configurable_personality
personality = create_configurable_personality("character_id")
agent = create_agent("character_id", personality=personality)
```

## Adding New Characters

### Simple Character (Configurable)

1. **Create JSON Configuration** in `configs/personalities/`:

   ```json
   {
     "character_id": "new_character",
     "character_name": "New Character",
     "character_type": "influencer",
     "personality": {
       "traits": "Friendly and engaging",
       "language_style": "spanglish"
     },
     "engagement": {
       "threshold": 0.5,
       "cooldown_minutes": 15
     }
   }
   ```

2. **Use the Factory**:
   ```python
   agent = create_agent("new_character")
   ```

### Complex Character (Custom)

1. **Create JSON Configuration** (same as above)

2. **Create Custom Personality** (if needed):

   ```python
   # app/models/personalities/custom_personality.py
   from app.ports.personality_port import PersonalityPort

   class CustomPersonality(PersonalityPort):
       # Implement custom personality logic
       pass
   ```

3. **Create Custom Agent**:

   ```python
   # app/agents/custom_agent.py
   from app.agents.base_character import BaseCharacterAgent

   class CustomAgent(BaseCharacterAgent):
       def calculate_engagement_probability(self, context, ...):
           # Custom engagement logic
           pass
   ```

4. **Register with Factory**:
   ```python
   # Update app/agents/agent_factory.py
   CUSTOM_AGENT_CREATORS = {
       "jovani_vazquez": create_jovani_vazquez,
       "custom_character": create_custom_agent,  # Add this
   }
   ```

## Architecture Benefits

### 1. **Scalability**

- 80% of characters can use the enhanced BaseCharacterAgent
- Only complex characters need custom implementations
- Easy to add new characters with just configuration

### 2. **Maintainability**

- Clean separation of concerns with Ports and Adapters
- Configuration-driven approach reduces code duplication
- Standard patterns for common behavior

### 3. **Flexibility**

- Custom agents can override any behavior
- Personality logic is separate from agent logic
- Easy to test and mock components

### 4. **Performance**

- Cached personality data
- Lightweight configurable agents
- Efficient factory pattern

## Testing

### Agent Factory Tests

```python
# tests/test_agent_factory.py
def test_create_jovani_agent():
    agent = create_agent("jovani_vazquez")
    assert isinstance(agent, JovaniVazquezAgent)

def test_create_configurable_agent():
    agent = create_agent("unknown_character")
    assert isinstance(agent, BaseCharacterAgent)
```

### Configurable Personality Tests

```python
# tests/test_configurable_personality.py
def test_personality_properties():
    personality = create_configurable_personality("jovani_vazquez")
    assert personality.character_name == "Jovani Vázquez"
```

## Migration Guide

### From Old Agent Classes

1. **Simple agents**: Replace with enhanced `BaseCharacterAgent`
2. **Complex agents**: Extend `BaseCharacterAgent` and override only custom methods
3. **Update imports**: Use `create_agent()` factory function

### Example Migration

**Before:**

```python
class OldCharacterAgent(BaseCharacterAgent):
    def calculate_engagement_probability(self, context, ...):
        # Simple delegation to personality
        return self.personality.calculate_engagement_boost(context)
```

**After:**

```python
# No custom class needed - use enhanced BaseCharacterAgent
agent = create_agent("character_id")
```

## Best Practices

1. **Start with Configuration**: Always try configuration-driven approach first
2. **Override Sparingly**: Only override methods that need custom logic
3. **Use Factory**: Always use `create_agent()` instead of direct instantiation
4. **Test Both Paths**: Test both configurable and custom agent creation
5. **Document Custom Logic**: Clearly document why custom logic is needed

## Future Enhancements

1. **Agent Registry**: Dynamic registration of custom agents
2. **Configuration Validation**: Enhanced schema validation
3. **Performance Monitoring**: Metrics for agent performance
4. **Plugin System**: Support for external personality plugins
