# First1KGreek Test Suite

This directory contains the comprehensive test suite for the First1KGreek browser application, covering both the original HTTP server implementation and the new FastAPI implementation.

## Test Organization

The tests are organized into several categories:

- **Core Tests**: Basic test utilities, fixtures, and base classes (`tests/core/`)
- **API Tests**: Tests for the FastAPI implementation (`tests/api/`)
- **Unit Tests**: Tests for individual components (`tests/unit/`)
- **Integration Tests**: Tests for component interactions (`tests/integration/`)
- **Performance Tests**: Tests for performance benchmarks (`tests/performance/`)

## Running Tests

There are several ways to run the tests:

### Running All Tests

```bash
python -m pytest
```

### Running by Category

```bash
# Run only API tests
python -m pytest tests/api/

# Run only integration tests
python -m pytest tests/integration/

# Run only performance tests
python -m pytest tests/performance/
```

### Running by Test Class or Method

```bash
# Run a specific test file
python -m pytest tests/api/test_authors_api.py

# Run a specific test class
python -m pytest tests/api/test_authors_api.py::AuthorsAPITests

# Run a specific test method
python -m pytest tests/api/test_authors_api.py::AuthorsAPITests::test_list_authors
```

## Test Configuration

The test configuration is managed through several files:

- **conftest.py**: Shared fixtures and test setup
- **test_base.py**: Base test class with common utilities
- **pytest.ini**: Pytest configuration and markers

## Test Dependencies

The tests have the following dependencies:

- **pytest**: Core testing framework
- **pytest-cov**: Coverage reporting
- **fastapi**: FastAPI framework (for API tests)
- **httpx**: HTTP client for FastAPI testing
- **requests**: HTTP client for integration tests

## Writing Tests

When writing tests for the First1KGreek browser, follow these guidelines:

1. **Test Isolation**: Tests should not depend on the state of other tests
2. **Mocking**: Use mock objects to isolate tests from external dependencies
3. **Clear Assertions**: Use descriptive assertion messages
4. **Follow Patterns**: Use existing test patterns for consistency
5. **Test Both Implementations**: Test both HTTP and FastAPI implementations

## Testing Approach for Dual Server Implementation

During the transition period, First1KGreek supports both the original HTTP server and the new FastAPI implementation. The test suite is designed to test both implementations:

### HTTP Server Tests

Legacy tests in `tests/unit/` and other directories test the original HTTP server implementation. These tests:

- Use `browse_texts_fixed.CustomHTTPRequestHandler` as the primary test target
- Mock requests and responses using `unittest.mock`
- Verify that the correct HTML content is generated

### FastAPI Tests

Modern tests in `tests/api/` test the new FastAPI implementation. These tests:

- Use FastAPI's `TestClient` to make requests to the API
- Verify that the correct JSON responses are returned
- Follow FastAPI's testing patterns and best practices

### Hybrid Server Tests

Integration tests in `tests/integration/test_hybrid_server.py` test the hybrid server mode that runs both implementations simultaneously. These tests:

- Start both HTTP and FastAPI servers
- Verify that both servers can be accessed
- Verify that both servers share data correctly
- Test concurrent access to both servers

## Test Coverage

To generate test coverage reports:

```bash
python -m pytest --cov=src.first1k
```

For HTML coverage reports:

```bash
python -m pytest --cov=src.first1k --cov-report=html
```

## Troubleshooting Tests

If tests are failing, check:

1. **Import Issues**: Ensure paths are correctly set up
2. **Mock Objects**: Verify that mocks are correctly configured
3. **Server Availability**: Check that servers can start correctly
4. **Port Conflicts**: Ensure tests use different ports
5. **Environment Variables**: Check if any environment variables need to be set

For more detailed documentation on specific test categories, see the README files in each test subdirectory. 