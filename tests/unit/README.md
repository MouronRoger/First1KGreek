# FastAPI Test Implementation for First1KGreek

This directory contains unit tests for the FastAPI implementation of First1KGreek.

## Test Structure

The tests are organized as follows:

- `test_api_preferences.py`: Tests for the preferences API endpoints
- `test_api_authors.py`: Tests for the authors API endpoints

Additional test files should be added as more endpoints are implemented:
- `test_api_search.py`: Tests for the search API endpoints
- `test_api_view.py`: Tests for the view API endpoints

## Running the Tests

To run the FastAPI tests:

```bash
# Run all API tests
pytest tests/unit/test_api_*.py -v

# Run only preferences tests
pytest tests/unit/test_api_preferences.py -v

# Run with the api marker
pytest -m api -v
```

## Test Design

The API tests follow these design principles:

1. **Isolation**: Each test uses unittest.mock to isolate the API endpoints from their dependencies.
2. **Comprehensive Testing**: Tests cover both success and error paths for each endpoint.
3. **Readable Assertions**: Tests use clear assertions to document expected behavior.
4. **Independent**: Tests can run without requiring actual files or API server.

## Adding New Tests

When adding new API endpoint tests:

1. Follow the pattern established in existing test files
2. Use the TestClient from fastapi.testclient
3. Mock external dependencies
4. Test both success and error cases
5. Add appropriate pytest markers

## Integration with Performance Tests

The unit tests focus on correctness while the performance tests in `tests/performance/test_api_performance.py` focus on the performance characteristics of the API.

For a complete test of the API, both correctness and performance tests should pass. 