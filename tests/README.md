# Cuentamelo LangGraph Test Suite

This directory contains a comprehensive test suite for the Cuentamelo LangGraph system, following test-driven design principles and best practices.

## Test Structure

The test suite is organized into logical categories that mirror the application architecture:

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── run_tests.py                         # Test runner script
├── run_tests_revamp.py                  # Advanced test runner
├── README.md                            # This file
├── api/                                 # API endpoint tests
│   ├── test_command_api_endpoints.py
│   ├── test_news_api_endpoints.py
│   ├── test_frontend_api_endpoints.py
│   └── test_api_endpoints.py
├── infrastructure/                      # Infrastructure/configuration tests
│   ├── test_config.py
│   └── test_configurable_personality.py
├── integration/                         # Integration tests
│   ├── test_command_flow_integration.py
│   ├── test_langgraph_integration.py
│   ├── test_real_integration.py
│   └── test_config_driven_personality.py
├── unit/                                # Unit tests (fast, isolated)
│   ├── models/                          # Data model tests
│   │   ├── test_personality.py
│   │   ├── test_thread_engagement.py
│   │   └── test_news_processing.py
│   ├── agents/                          # Agent tests
│   │   └── test_character_agents.py
│   ├── graphs/                          # Workflow/Graph tests
│   │   ├── test_character_workflow.py
│   │   └── test_orchestrator.py
│   ├── services/                        # Service layer tests
│   │   ├── test_command_broker_service.py
│   │   ├── test_frontend_event_bus.py
│   │   ├── test_n8n_frontend_service.py
│   │   ├── test_dependency_container.py
│   │   ├── test_database_service.py
│   │   └── test_personality_config_loader.py
│   └── tools/                           # Tool tests
│       └── [tool test files]
```

## Test Categories

### Unit Tests (`unit/`)

- `unit/models/`: Data model tests
- `unit/agents/`: Agent tests
- `unit/graphs/`: Workflow/graph tests
- `unit/services/`: Service layer tests
- `unit/tools/`: Tool tests

### Integration Tests (`integration/`)

- Component and workflow integration

### API Tests (`api/`)

- HTTP endpoint and contract tests

### Infrastructure Tests (`infrastructure/`)

- Configuration and infrastructure validation

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
python tests/run_tests.py services
python tests/run_tests.py tools

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
pytest tests/unit/models/test_personality.py
pytest tests/integration/test_langgraph_integration.py
pytest tests/api/test_api_endpoints.py
pytest tests/unit/services/test_command_broker_service.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test classes
pytest tests/unit/models/test_personality.py::TestPersonalityDataSystem

# Run specific test methods
pytest tests/unit/models/test_personality.py::TestPersonalityDataSystem::test_jovani_vazquez_personality_creation
```

### Using pytest Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only infrastructure tests
pytest -m infrastructure

# Run async tests
pytest -m async

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
pytest tests/unit/models/test_personality.py -v
```
