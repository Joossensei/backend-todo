# Test Suite for Todo API

This directory contains comprehensive tests for the Todo API using pytest.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_main.py             # Tests for main application endpoints
├── test_todos.py            # Tests for todos API endpoints
├── test_priorities.py       # Tests for priorities API endpoints
└── README.md               # This file
```

## Test Categories

### 1. Main Endpoints (`test_main.py`)

- Root endpoint (`/`)
- Health check endpoint (`/health`)
- API documentation endpoints (`/docs`, `/openapi.json`)

### 2. Todos API (`test_todos.py`)

- GET `/api/v1/todos/` - List todos with pagination
- GET `/api/v1/todos/{key}` - Get todo by key
- POST `/api/v1/todos/` - Create new todo
- PUT `/api/v1/todos/{key}` - Update todo
- PATCH `/api/v1/todos/{key}` - Partial update todo
- DELETE `/api/v1/todos/{key}` - Delete todo

### 3. Priorities API (`test_priorities.py`)

- GET `/api/v1/priorities/` - List priorities with pagination
- GET `/api/v1/priorities/{key}` - Get priority by key
- POST `/api/v1/priorities/` - Create new priority
- PUT `/api/v1/priorities/{key}` - Update priority
- PATCH `/api/v1/priorities/{key}` - Partial update priority
- DELETE `/api/v1/priorities/{key}` - Delete priority

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

### Basic Test Commands

1. **Run all tests:**

   ```bash
   pytest
   ```

2. **Run tests with coverage:**

   ```bash
   pytest --cov=app --cov-report=term-missing --cov-report=html
   ```

3. **Run specific test file:**

   ```bash
   pytest tests/test_todos.py
   ```

4. **Run tests with verbose output:**

   ```bash
   pytest -v
   ```

5. **Run tests and stop on first failure:**
   ```bash
   pytest -x
   ```

### Using the Test Runner Script

The `run_tests.py` script provides a convenient way to run tests:

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose

# Run specific test file
python run_tests.py tests/test_todos.py
```

## Test Fixtures

The test suite includes several fixtures defined in `conftest.py`:

- `client`: FastAPI TestClient instance
- `db_session`: Database session for each test
- `sample_todo_data`: Sample todo data for testing
- `sample_priority_data`: Sample priority data for testing
- `sample_todo_update_data`: Sample todo update data
- `sample_priority_update_data`: Sample priority update data

## Test Database

Tests use an in-memory SQLite database to ensure:

- Tests are isolated from each other
- No external database dependencies
- Fast test execution
- Clean state for each test

## Coverage Reports

When running with coverage, reports are generated in:

- Terminal output (missing lines)
- HTML report (`htmlcov/index.html`)
- XML report (`coverage.xml`)

## Test Categories

### Unit Tests

- Test individual functions and methods
- Mock external dependencies
- Fast execution

### Integration Tests

- Test API endpoints end-to-end
- Use test database
- Test complete workflows

## Best Practices

1. **Test Isolation**: Each test runs in isolation with a fresh database
2. **Descriptive Names**: Test methods have clear, descriptive names
3. **Comprehensive Coverage**: Tests cover success and error cases
4. **Data Validation**: Tests verify both response status and data structure
5. **Error Handling**: Tests verify proper error responses

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_*.py`
2. Use descriptive test method names
3. Include both success and error cases
4. Use the provided fixtures for consistent test data
5. Add appropriate docstrings

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Tests use in-memory SQLite, no external DB needed
3. **Test Failures**: Check that the API is running and accessible

### Debugging Tests

Run tests with increased verbosity:

```bash
pytest -vvv --tb=long
```

This will show detailed output and full tracebacks for failures.
