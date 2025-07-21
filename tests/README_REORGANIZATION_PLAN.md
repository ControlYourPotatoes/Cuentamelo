# Test Directory Reorganization Plan

## Current Issues

1. **Mixed organization**: Some tests in subdirectories, others in root
2. **Duplicate files**: `test_dependency_container.py` and `test_dependency_container_revamp.py`
3. **Inconsistent naming**: Some files have `_revamp` suffix
4. **Scattered API tests**: API endpoint tests mixed with service tests
5. **Unclear categorization**: Hard to find specific types of tests

## Proposed New Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── run_tests.py                         # Main test runner (keep the revamp version)
├── README.md                           # Updated documentation
├── pytest.ini                          # Pytest configuration
│
├── unit/                               # Unit tests (fast, isolated)
│   ├── models/                         # Data model tests
│   │   ├── test_personality.py
│   │   ├── test_thread_engagement.py
│   │   └── test_news_processing.py
│   ├── agents/                         # Agent tests
│   │   ├── test_character_agents.py
│   │   └── test_agent_factory.py
│   ├── graphs/                         # Workflow/Graph tests
│   │   ├── test_character_workflow.py
│   │   └── test_orchestrator.py
│   ├── services/                       # Service layer tests
│   │   ├── test_command_broker_service.py
│   │   ├── test_frontend_event_bus.py
│   │   ├── test_n8n_frontend_service.py
│   │   ├── test_dependency_container.py
│   │   ├── test_database_service.py
│   │   └── test_personality_config_loader.py
│   └── tools/                          # Tool tests
│       └── [tool test files]
│
├── integration/                        # Integration tests (component interaction)
│   ├── test_command_flow_integration.py
│   ├── test_langgraph_integration.py
│   ├── test_real_integration.py
│   └── test_config_driven_personality.py
│
├── api/                               # API endpoint tests
│   ├── test_command_api_endpoints.py
│   ├── test_news_api_endpoints.py
│   ├── test_frontend_api_endpoints.py
│   └── test_api_endpoints.py
│
└── infrastructure/                    # Infrastructure and configuration tests
    ├── test_config.py
    └── test_configurable_personality.py
```

## Migration Steps

### Step 1: Create New Directory Structure

1. Create `unit/`, `api/`, and `infrastructure/` directories
2. Move existing subdirectories into `unit/`
3. Create `unit/services/` directory

### Step 2: Move and Rename Files

1. **Unit Tests** → `unit/`:

   - `test_models/` → `unit/models/`
   - `test_agents/` → `unit/agents/`
   - `test_graphs/` → `unit/graphs/`
   - `test_tools/` → `unit/tools/`

2. **Service Tests** → `unit/services/`:

   - `test_command_broker_service.py` → `unit/services/`
   - `test_frontend_event_bus.py` → `unit/services/`
   - `test_n8n_frontend_service.py` → `unit/services/`
   - `test_dependency_container_revamp.py` → `unit/services/test_dependency_container.py` (keep the revamp version)
   - `test_database_service.py` → `unit/services/`
   - `test_personality_config_loader.py` → `unit/services/`

3. **API Tests** → `api/`:

   - `test_command_api_endpoints.py` → `api/`
   - `test_news_api_endpoints.py` → `api/`
   - `test_frontend_api_endpoints.py` → `api/`
   - `test_api_endpoints.py` → `api/`

4. **Infrastructure Tests** → `infrastructure/`:
   - `test_config.py` → `infrastructure/`
   - `test_configurable_personality.py` → `infrastructure/`

### Step 3: Clean Up Duplicates

1. Remove `test_dependency_container.py` (keep the revamp version)
2. Remove `test_event_bus.py` (keep `test_frontend_event_bus.py`)
3. Remove `test_frontend_service.py` (keep `test_n8n_frontend_service.py`)
4. Remove `test_command_broker.py` (keep `test_command_broker_service.py`)

### Step 4: Update Imports

1. Update all import statements in moved files
2. Update `conftest.py` imports if needed
3. Update test runner scripts

### Step 5: Update Configuration

1. Update `pytest.ini` or `pytest_revamp.ini` with new paths
2. Update test runner scripts with new directory structure
3. Update documentation

## Benefits of New Structure

1. **Clear categorization**: Easy to find specific types of tests
2. **Logical grouping**: Related tests are together
3. **Scalable**: Easy to add new test categories
4. **CI/CD friendly**: Can run specific test categories
5. **Maintainable**: Clear separation of concerns

## Test Categories

### Unit Tests (`unit/`)

- **Purpose**: Test individual components in isolation
- **Speed**: Fast execution
- **Dependencies**: Mocked external dependencies
- **Coverage**: High coverage of individual functions/methods

### Integration Tests (`integration/`)

- **Purpose**: Test component interactions
- **Speed**: Medium execution time
- **Dependencies**: Real services, mocked external APIs
- **Coverage**: End-to-end workflows

### API Tests (`api/`)

- **Purpose**: Test HTTP endpoints and API contracts
- **Speed**: Medium execution time
- **Dependencies**: FastAPI test client, mocked services
- **Coverage**: API behavior and response formats

### Infrastructure Tests (`infrastructure/`)

- **Purpose**: Test configuration and infrastructure setup
- **Speed**: Fast execution
- **Dependencies**: Minimal dependencies
- **Coverage**: Configuration validation and setup

## Running Tests by Category

```bash
# Run all unit tests
pytest tests/unit/

# Run specific unit test categories
pytest tests/unit/models/
pytest tests/unit/services/
pytest tests/unit/agents/

# Run integration tests
pytest tests/integration/

# Run API tests
pytest tests/api/

# Run infrastructure tests
pytest tests/infrastructure/

# Run all tests
pytest tests/
```

## Migration Checklist

- [ ] Create new directory structure
- [ ] Move files to appropriate directories
- [ ] Remove duplicate files
- [ ] Update import statements
- [ ] Update test runner scripts
- [ ] Update pytest configuration
- [ ] Update documentation
- [ ] Verify all tests still pass
- [ ] Update CI/CD configuration if needed
