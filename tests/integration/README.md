# Integration Tests for First1KGreek

This directory contains integration tests for the First1KGreek browser application. These tests verify that different components of the system work together correctly, with a specific focus on the hybrid server mode that runs both HTTP and FastAPI servers.

## Purpose

Integration tests serve several key purposes:

1. **Component Interaction**: Verify that different components interact correctly
2. **Real-world Scenarios**: Test end-to-end workflows that users would experience
3. **System Configuration**: Ensure that configuration works correctly across components
4. **Data Flow**: Verify that data flows correctly between components
5. **Server Modes**: Test different server modes (HTTP, FastAPI, hybrid)

## Test Files

- **test_hybrid_server.py**: Tests for the hybrid server mode that runs both HTTP and FastAPI servers simultaneously

## Running Tests

To run the integration tests:

```bash
python -m pytest tests/integration/
```

To run with verbose output:

```bash
python -m pytest tests/integration/ -v
```

## Test Design

The integration tests have several design considerations:

### Resource Management

The tests use the `contextmanager` pattern to ensure proper cleanup of resources:

```python
@contextmanager
def run_hybrid_server(self, timeout=5):
    # Create server and set up resources
    try:
        # Start server in a thread
        # Wait for server to start
        yield (http_url, fastapi_url)
    finally:
        # Cleanup resources
        # Shutdown server
```

### Multiprocessing and Threading Issues

The tests address potential issues with multiprocessing and threading:

1. Use threading instead of multiprocessing when possible
2. Use daemon threads to ensure proper cleanup
3. Use timeouts to prevent hanging tests
4. Implement proper cleanup of server resources
5. Use exclusive ports to avoid conflicts

### Server Verification

The tests verify that both server components (HTTP and FastAPI) work correctly:

1. Test that the HTTP server serves pages correctly
2. Test that the FastAPI server serves API endpoints correctly
3. Test that both servers can access the same data
4. Test error handling in both servers

## Adding New Integration Tests

When adding new integration tests, follow these guidelines:

1. Use the context manager pattern for resource management
2. Implement proper cleanup of resources
3. Use timeouts to prevent hanging tests
4. Test realistic user workflows
5. Verify data consistency across server modes

## Debugging Integration Test Failures

If integration tests fail, here are some troubleshooting steps:

1. **Port Conflicts**: Ensure no other processes are using the same ports
2. **Timeouts**: Check if the server startup timeout is sufficient
3. **Resource Cleanup**: Verify that resources are properly cleaned up
4. **Environmental Factors**: Check for environmental factors that might affect the tests
5. **Logging**: Enable verbose logging for more detailed error information

## Known Limitations

1. These tests require resources that may be unavailable in some environments
2. Server startup times may vary across different systems
3. Some tests use mocking to isolate specific components, which may differ from real-world behavior 