# Performance Tests for First1KGreek

This directory contains performance benchmark tests for the First1KGreek application, including both the HTTP server and FastAPI implementations.

## Test Structure

The performance tests are organized as follows:

- `test_http_server.py`: Performance benchmarks for the HTTP server
- `test_api_performance.py`: Performance benchmarks for the FastAPI endpoints
- `test_xml_processing.py`: Performance tests for XML processing functions

## Running the Tests

To run the performance tests:

```bash
# Run all performance tests
pytest tests/performance/ -v

# Run only API performance tests
pytest tests/performance/test_api_performance.py -v

# Run with the performance marker
pytest -m performance -v
```

## Test Design

The performance tests follow these design principles:

1. **Reproducible Benchmarks**: Tests use consistent methodology to ensure reproducible results
2. **Statistical Analysis**: Tests calculate average, min, max, and standard deviation
3. **Configurable Thresholds**: Performance thresholds can be adjusted as needed
4. **Concurrent Testing**: Tests include concurrent request handling to simulate real-world load
5. **Isolated Testing**: Tests can run in isolation to avoid interference

## Performance Metrics

The tests measure the following metrics:

1. **Response Time**: Time to process and respond to requests (in milliseconds)
2. **Success Rate**: Percentage of successful responses under load
3. **Throughput**: Number of requests that can be handled per second
4. **Resource Usage**: Memory and CPU usage during operation (where applicable)

## Performance Thresholds

Current performance thresholds:

- Author List: 200ms
- Author Detail: 150ms
- Author Works: 250ms
- Search: 500ms
- Preferences: 100ms
- Concurrent Request Success Rate: 95%

These thresholds can be adjusted in `test_api_performance.py` based on baseline performance.

## Interpreting Results

Performance test results are printed to the console, showing:

- Average response time
- Minimum response time
- Maximum response time
- Success rate (for concurrent tests)

If a test exceeds its threshold, it will fail with a message indicating the performance issue.

## Adding New Performance Tests

When adding new performance tests:

1. Follow the pattern established in existing test files
2. Set reasonable thresholds based on baseline testing
3. Include both single-request and concurrent testing
4. Add appropriate pytest markers
5. Document the performance expectations 