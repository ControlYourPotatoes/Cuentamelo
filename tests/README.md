# Cuentamelo LangGraph Test Suite

This directory contains a comprehensive test suite for the Cuentamelo LangGraph system, following test-driven design principles and best practices.

## Test Structure

The test suite is organized into logical categories that mirror the application architecture:

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── run_tests.py                         # Test runner script
├── README.md                           # This file
├── test_models/                        # Model tests
│   ├── test_personality.py             # Personality system tests
│   ├── test_thread_engagement.py       # Thread engagement state tests
│   └── test_news_processing.py         # News processing tests
├── test_agents/                        # Agent tests
│   └── test_character_agents.py        # Character agent tests
├── test_graphs/                        # Graph/workflow tests
│   ├── test_character_workflow.py      # Character workflow tests
│   └── test_orchestrator.py            # Orchestration tests
├── integration/                        # Integration tests
│   └── test_langgraph_integration.py   # System integration tests
└── [existing test files]               # Legacy test files
```

## Test Categories

### Unit Tests (`test_models/`, `test_agents/`, `test_graphs/`)

**Personality System Tests** (`test_personality.py`)

- Personality data creation and validation
- Character type differentiation
- Tone preferences and topic weights
- Personality consistency validation

**Thread Engagement Tests** (`test_thread_engagement.py`)

- Thread state creation and management
- Character reply tracking and rate limiting
- Thread context generation
- Multi-character conversation handling

**News Processing Tests** (`test_news_processing.py`)

- News item creation and validation
- Topic categorization and relevance scoring
- Source handling and timestamp management
- News item builder pattern usage

**Character Agent Tests** (`test_character_agents.py`)

- Agent creation and configuration
- Engagement probability calculations
- Topic relevance assessment
- AI provider integration
- Response generation with dependency injection

**Character Workflow Tests** (`test_character_workflow.py`)

- New thread workflow execution
- Thread reply workflow handling
- Context generation and management
- Error handling and edge cases
- Rate limiting integration

**Orchestration Tests** (`test_orchestrator.py`)

- Orchestration state management
- News processing cycles
- Character reaction generation
- State persistence and recovery
- Multi-character coordination

### Integration Tests (`integration/`)

**LangGraph System Integration** (`test_langgraph_integration.py`)

- End-to-end news discovery and engagement flow
- Character workflow integration with orchestration
- Thread engagement system integration
- Personality data integration throughout the system
- Realistic news discovery sequences
- Thread-based conversation flows
- System error handling and recovery
- Performance and scalability testing

## Test Design Principles

### Test-Driven Design

- Tests serve as executable specifications
- Tests document expected behavior
- Tests catch regressions and validate changes

### Builder Pattern

- `NewsItemBuilder` for creating test news items
- `ThreadEngagementStateBuilder` for creating thread states
- Fluent interface for easy test data construction

### Dependency Injection

- Mock AI providers for isolated testing
- Configurable character agents
- Testable component boundaries

### Comprehensive Coverage

- Happy path scenarios
- Error conditions and edge cases
- Boundary value testing
- Performance and scalability validation

## Running Tests

### Using the Test Runner Script

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py models
python tests/run_tests.py agents
python tests/run_tests.py graphs

# Run specific test files
python tests/run_tests.py personality
python tests/run_tests.py thread
python tests/run_tests.py news
python tests/run_tests.py character
python tests/run_tests.py workflow
python tests/run_tests.py orchestrator

# Verbose output
python tests/run_tests.py all -v

# With coverage reporting
python tests/run_tests.py all -c
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_models/test_personality.py
pytest tests/integration/test_langgraph_integration.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test classes
pytest tests/test_models/test_personality.py::TestPersonalityDataSystem

# Run specific test methods
pytest tests/test_models/test_personality.py::TestPersonalityDataSystem::test_jovani_vazquez_personality_creation
```

### Using pytest Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only async tests
pytest -m asyncio

# Run slow tests
pytest -m slow
```

## Test Fixtures

The test suite provides several shared fixtures in `conftest.py`:

### Data Builders

- `news_item_builder`: Creates test news items
- `thread_state_builder`: Creates thread engagement states

### Sample Data

- `sample_news_items`: Pre-built news items for testing
- `jovani_personality`: Jovani Vázquez personality data
- `politico_personality`: Político Boricua personality data
- `ciudadano_personality`: Ciudadano Boricua personality data
- `historiador_personality`: Historiador Cultural personality data
- `sample_thread_state`: Sample thread engagement state

### Test Constants

- `MUSIC_FESTIVAL_NEWS`: Music festival news data
- `TRAFFIC_NEWS`: Traffic news data
- `CULTURAL_NEWS`: Cultural news data

## Test Data Patterns

### Builder Pattern Usage

```python
def test_news_item_creation(self, news_item_builder):
    news_item = news_item_builder\
        .with_id("test_001")\
        .with_headline("Test Headline")\
        .with_content("Test content")\
        .with_topics(["music", "entertainment"])\
        .with_relevance_score(0.8)\
        .build()

    assert news_item.id == "test_001"
    assert news_item.headline == "Test Headline"
```

### Mock AI Provider Usage

```python
@pytest.mark.asyncio
async def test_character_response_generation(self):
    mock_ai_provider = Mock()
    mock_response = Mock()
    mock_response.content = "Test response"
    mock_response.confidence_score = 0.8
    mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)

    jovani_agent = create_jovani_vazquez(ai_provider=mock_ai_provider)
    # ... test logic
```

## Best Practices

### Test Naming

- Test classes: `Test[ComponentName][Aspect]`
- Test methods: `test_[scenario]_[expected_behavior]`
- Descriptive names that explain the test scenario

### Test Organization

- Group related tests in classes
- Use descriptive docstrings
- Follow AAA pattern (Arrange, Act, Assert)

### Error Handling

- Test both success and failure scenarios
- Validate error messages and types
- Test edge cases and boundary conditions

### Async Testing

- Use `@pytest.mark.asyncio` for async tests
- Properly mock async dependencies
- Test async error handling

## Coverage Goals

The test suite aims for comprehensive coverage:

- **Unit Tests**: 90%+ line coverage for core components
- **Integration Tests**: End-to-end workflow validation
- **Error Handling**: All error paths tested
- **Edge Cases**: Boundary conditions and invalid inputs
- **Performance**: Scalability and performance validation

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

- Fast execution for unit tests
- Comprehensive integration tests
- Coverage reporting
- Clear failure messages
- Parallel execution support

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use the provided fixtures and builders
3. Add appropriate markers for test categorization
4. Include both positive and negative test cases
5. Update this README if adding new test categories
6. Ensure tests are deterministic and fast

## Troubleshooting

### Common Issues

**Import Errors**: Ensure you're running from the project root directory

```bash
cd /path/to/cuentamelo
python tests/run_tests.py
```

**Async Test Failures**: Make sure to use `@pytest.mark.asyncio` for async tests

```python
@pytest.mark.asyncio
async def test_async_function():
    # test logic
```

**Mock Issues**: Ensure mocks are properly configured for async functions

```python
mock_ai_provider.generate_character_response = AsyncMock(return_value=mock_response)
```

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=long
```

### Test Isolation

Run tests in isolation to identify issues:

```bash
pytest tests/test_models/test_personality.py -v
```
