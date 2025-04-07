# First1KGreek Browser Test Suite

This directory contains the test suite for the First1KGreek Browser application. The tests are designed to validate functionality and prevent regressions when making changes to the codebase.

## Test Structure

The test suite is organized into the following files:

- `tests/__init__.py` - Makes tests a proper package
- `tests/test_base.py` - Base test class with common utilities and fixtures
- `tests/test_server.py` - Tests for server initialization and port handling
- `tests/test_http_handler.py` - Tests for the HTTP request handler
- `tests/test_page_generation.py` - Tests for HTML content generation
- `tests/test_utils.py` - Tests for utility functions
- `tests/conftest.py` - Configuration and fixtures for pytest integration
- `tests/test_pytest_sample.py` - Example of pure pytest-style tests

## Testing Frameworks

The project supports two testing approaches:

1. **unittest** - Traditional unittest-based tests that extend `unittest.TestCase`
2. **pytest** - More modern pytest-style tests with fixtures and improved assertions

We are gradually transitioning from unittest to pytest while maintaining backward compatibility. New tests should be written in pytest style when possible.

## Test Design Choices

The test suite was designed with the following principles in mind:

1. **Isolation**: Each test is isolated to ensure predictable results. We use mock objects extensively to avoid dependencies on external systems, network activity, or file system operations.

2. **Mocking Strategy**: 
   - For `HTTPHandlerTests`, we create mock handlers and selectively bind actual methods to test specific functionality.
   - For `PageGenerationTests`, we use custom implementations of page generation methods to avoid file system operations.
   - For `ServerTests`, we focus on mocking socket operations to test port handling logic.

3. **Test Coverage**: The tests cover all major components of the application:
   - Server initialization and port handling
   - HTTP request processing (both GET and POST)
   - HTML page generation
   - User preference handling
   - File operations

4. **Error Handling**: Tests include both success and error scenarios to ensure the application behaves correctly in all situations.

## Running the Tests

### Using pytest (recommended)

```bash
# Run all tests
pytest

# Run all tests with coverage report
pytest --cov=src --cov=browse_texts_fixed

# Run tests by category
pytest -m unit
pytest -m integration
pytest -m performance

# Run a specific test file
pytest tests/test_server.py

# Run a specific test function
pytest tests/test_server.py::test_is_port_in_use_pytest_style

# Using the pytest runner script
python run_pytest.py --unit
python run_pytest.py --all --coverage
```

### Using unittest

```bash
# Run all tests
python -m unittest discover -s tests

# Run a specific test file
python -m unittest tests.test_server
python -m unittest tests.test_http_handler
python -m unittest tests.test_page_generation
python -m unittest tests.test_utils

# Run a specific test case
python -m unittest tests.test_server.ServerTests
```

## Test Coverage

To generate a test coverage report, you can use pytest-cov:

```bash
# Generate coverage report
pytest --cov=src --cov=browse_texts_fixed

# Generate HTML report
pytest --cov=src --cov=browse_texts_fixed --cov-report=html
```

## Writing New Tests

When adding new features or fixing bugs, please ensure that appropriate tests are added or updated. Follow these guidelines:

1. Write new tests in pytest style when possible
2. Isolate tests by using fixtures and mocks
3. Keep tests independent and avoid dependencies between test cases
4. Document test purpose with docstrings
5. Use parametrization for testing multiple scenarios
6. Include tests for both success and error cases

### pytest Style Example

```python
import pytest
from unittest import mock

# Mark test category
@pytest.mark.unit
def test_my_function():
    """Test my_function behaves as expected."""
    # Setup
    test_input = "test input"
    
    # Exercise
    result = my_function(test_input)
    
    # Verify
    assert result == "expected output"
    
# Parameterized test example
@pytest.mark.parametrize("input_val,expected", [
    ("input1", "output1"),
    ("input2", "output2"),
])
def test_my_function_parameterized(input_val, expected):
    """Test my_function with multiple inputs."""
    result = my_function(input_val)
    assert result == expected
```

## Mocking Strategy

The test suite uses several mocking approaches:

1. **Mock Services**: The server and network operations are mocked to avoid binding to actual ports.
2. **Mock File System**: All file operations use temporary directories or mock objects.
3. **Mock Handler Methods**: HTTP handler methods are selectively mocked to focus testing on specific functionality.
4. **Custom Implementations**: For page generation tests, we provide custom HTML instead of generating it from the file system.

## Test Fixtures

The test suite includes fixtures for:

- Mock author data
- Mock user preferences
- Temporary test directories
- Mock HTTP handlers

These fixtures are available in the base test class and in `conftest.py` for pytest integration.

## Testing Philosophy

The test suite is designed to:

1. Validate core functionality
2. Catch regressions when making changes
3. Document expected behavior
4. Support future modularization efforts

When refactoring or modifying the codebase, run the full test suite before and after changes to ensure no functionality is broken. 