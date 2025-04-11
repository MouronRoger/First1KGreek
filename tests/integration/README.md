# Integration Tests for First1KGreek

This directory contains integration tests for the First1KGreek application, including the hybrid server mode that runs both HTTP and FastAPI servers simultaneously.

## Test Structure

The integration tests are organized as follows:

- `test_server.py`: Tests for the HTTP server functionality
- `test_hybrid_server.py`: Tests for the hybrid server mode that runs both HTTP and FastAPI servers

## Running the Tests

To run the integration tests:

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run only hybrid server tests
pytest tests/integration/test_hybrid_server.py -v

# Run with the integration marker
pytest -m integration -v

# Run with the hybrid marker
pytest -m hybrid -v
```

## Test Design

The integration tests follow these design principles:

1. **Full System Testing**: Tests use actual server processes to verify behavior
2. **Resource Management**: Tests properly start and stop servers using pytest fixtures
3. **Port Management**: Tests dynamically find available ports to avoid conflicts
4. **Comprehensive Coverage**: Tests verify both HTTP and FastAPI endpoints
5. **Data Isolation**: Tests use isolated data to avoid affecting production data

## Test Prerequisites

Integration tests require:

1. Both HTTP and FastAPI server implementations to be available
2. Network ports to be available for testing
3. All dependencies installed (`pip install -r requirements.txt`)

## Hybrid Server Testing

The hybrid server tests verify that:

1. Both HTTP and FastAPI servers can run simultaneously
2. Both servers can access the same data sources
3. Both servers properly handle requests
4. Both servers can be gracefully shut down

## Adding New Integration Tests

When adding new integration tests:

1. Follow the pattern established in existing test files
2. Use proper fixture management for server processes
3. Clean up all resources after tests complete
4. Test realistic user scenarios
5. Add appropriate pytest markers 