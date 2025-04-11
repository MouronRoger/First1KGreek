# Performance Tests for First1KGreek

This directory contains performance benchmarks for the First1KGreek FastAPI implementation. These tests measure response times, throughput, and stability under load.

## Purpose

The performance tests serve several important purposes:

1. **Baseline Establishment**: Set baseline performance expectations for key API endpoints
2. **Regression Detection**: Quickly identify performance regressions when code changes are made
3. **Bottleneck Identification**: Pinpoint performance bottlenecks in the application
4. **Load Testing**: Verify the application's behavior under concurrent load

## Test Files

- **test_api_performance.py**: Measures response times for FastAPI endpoints and tests concurrent request handling

## Running Tests

To run just the performance tests:

```bash
python -m pytest tests/performance/
```

To run with verbose output and see detailed metrics:

```bash
python -m pytest tests/performance/ -v
```

## Interpreting Results

The performance tests output several metrics:

- **Min**: Minimum response time in milliseconds
- **Max**: Maximum response time in milliseconds
- **Mean**: Average response time in milliseconds
- **Median**: Median response time in milliseconds
- **P95**: 95th percentile response time in milliseconds
- **Concurrent Requests**: Success rate and throughput under concurrent load

The tests set baseline thresholds for acceptable performance:

| Endpoint             | Threshold (ms) |
|----------------------|----------------|
| list_authors         | 5.0            |
| get_author           | 3.0            |
| get_author_works     | 5.0            |
| search               | 10.0           |
| view_xml             | 15.0           |

## Test Design

The performance tests follow these design principles:

1. **Isolation**: External dependencies (file system, network) are mocked to focus on application code
2. **Repeatability**: Tests run multiple iterations to get stable measurements
3. **Warm-up**: The first request is often slower due to initialization, so multiple iterations help stabilize results
4. **Statistical Analysis**: Tests calculate not just average but also min, max, median, and 95th percentile
5. **Concurrency**: Tests include concurrent request handling to simulate real-world load

## Benchmarking Environment

Performance metrics are highly dependent on the hardware and environment. When comparing performance metrics, ensure:

1. You're comparing tests run on the same machine
2. No other resource-intensive processes are running during the tests
3. You're using the same Python version and dependencies

## Adjusting Thresholds

The performance thresholds in `test_api_performance.py` may need adjustment based on your specific environment. If tests consistently fail on your system due to performance thresholds, you can adjust them:

```python
self.thresholds = {
    "list_authors": 10.0,  # Increased from 5.0
    "get_author": 5.0,     # Increased from 3.0
    ...
}
```

However, significant performance degradation should be investigated before simply increasing thresholds.

## Adding New Performance Tests

When adding new endpoints or features, follow these guidelines for performance testing:

1. Create a test method that measures response time over multiple iterations
2. Set a reasonable threshold based on expected performance
3. Test both single requests and concurrent load if applicable
4. Document the expected performance characteristics 