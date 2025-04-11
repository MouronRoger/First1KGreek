# FastAPI Test Suite for First1KGreek

This directory contains tests specifically for the FastAPI implementation of the First1KGreek browser. The tests use FastAPI's TestClient to make requests to the API endpoints and verify their behavior.

## Test Structure

The tests follow a consistent pattern:

1. **Setup**: Each test class inherits from `BaseTest` which provides common utilities and fixtures.
2. **Mocking**: External dependencies like file operations and data access are mocked to isolate the tests.
3. **Test Methods**: Individual test methods focus on testing specific endpoints and scenarios.
4. **Verification**: Assertions validate both the response status code and the content.

## Test Files

- **test_authors_api.py**: Tests for author-related endpoints (`/api/authors/`, `/api/authors/{id}`, `/api/authors/{id}/works`)
- **test_preferences_api.py**: Tests for preference management endpoints (`/api/preferences/`, `/api/preferences/work`, `/api/preferences/batch`)
- **test_search_api.py**: Tests for search functionality (`/api/search/`)
- **test_view_api.py**: Tests for content viewing endpoints (`/api/view/xml`, `/api/view/reader`, `/api/view/raw`)
- **test_models.py**: Tests for Pydantic model validation and serialization/deserialization

## Integration Tests

For integration tests that involve running actual server instances, see `tests/integration/test_hybrid_server.py`. These tests verify that both HTTP and FastAPI servers can run simultaneously and access the same data sources.

## Performance Tests

Performance tests are located in `tests/performance/test_api_performance.py`. These tests measure response times for key endpoints and establish baseline performance expectations.

## Running Tests

To run only the FastAPI API tests:

```bash
python -m pytest tests/api/
```

To run with verbose output:

```bash
python -m pytest tests/api/ -v
```

## Adding New Tests

When adding tests for new API endpoints, follow these guidelines:

1. Create test methods that focus on individual endpoints and specific scenarios
2. Mock external dependencies like file operations and data access
3. Test both success and error cases
4. Verify response status codes and content
5. Follow the naming convention: `test_<endpoint>_<scenario>`

Example:

```python
def test_get_authors_with_filter(self):
    """Test filtering authors by type."""
    # Mock the data access function
    with mock.patch('src.first1k.data.authors.async_get_filtered_authors') as mock_get_authors:
        # Setup the mock response
        mock_get_authors.return_value = [...]
        
        # Call the API endpoint with filter
        response = self.client.get("/api/authors/?type=Poet")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        ...
        
        # Verify the mock was called correctly
        mock_get_authors.assert_called_once_with(century=None, author_type="Poet", skip=0, limit=100)
```

## Best Practices

- **Isolate Tests**: Each test should be independent and not rely on state from other tests
- **Mock External Dependencies**: Use `unittest.mock` to isolate tests from external systems
- **Test Edge Cases**: Test both valid and invalid inputs
- **Clear Error Messages**: Use descriptive assert messages to make failures easier to debug
- **Follow Naming Conventions**: Use clear, descriptive names for test methods
- **Document Tests**: Include docstrings explaining what each test is verifying 