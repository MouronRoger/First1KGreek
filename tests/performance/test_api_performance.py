"""Performance benchmarks for FastAPI endpoints in First1KGreek.

This module measures the performance of key FastAPI endpoints under load.
"""

import pytest
import time
import statistics
import concurrent.futures
from fastapi.testclient import TestClient

from src.first1k.api import app

# Create test client
client = TestClient(app)

# Performance thresholds (in milliseconds)
AUTHOR_LIST_THRESHOLD = 200
AUTHOR_DETAIL_THRESHOLD = 150
AUTHOR_WORKS_THRESHOLD = 250
SEARCH_THRESHOLD = 500
PREFERENCES_THRESHOLD = 100

# Number of iterations for each test
ITERATIONS = 10


def run_concurrent_requests(url, num_requests=10):
    """Execute multiple concurrent requests and measure response times.
    
    Args:
        url: The endpoint URL to test
        num_requests: Number of concurrent requests to make
        
    Returns:
        tuple: (avg_time, min_time, max_time, success_rate)
    """
    response_times = []
    success_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        def make_request():
            start_time = time.time()
            response = client.get(url)
            end_time = time.time()
            is_success = response.status_code == 200
            return ((end_time - start_time) * 1000, is_success)  # Convert to milliseconds
        
        future_to_url = {executor.submit(make_request): i for i in range(num_requests)}
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                response_time, is_success = future.result()
                response_times.append(response_time)
                if is_success:
                    success_count += 1
            except Exception as e:
                print(f"Request generated an exception: {e}")
    
    if not response_times:
        return (0, 0, 0, 0)
    
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    success_rate = (success_count / num_requests) * 100
    
    return (avg_time, min_time, max_time, success_rate)


@pytest.mark.performance
def test_authors_endpoint_performance():
    """Benchmark the performance of the authors endpoint."""
    response_times = []
    
    for _ in range(ITERATIONS):
        start_time = time.time()
        response = client.get("/api/authors")
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Print results
    print(f"\nAuthors endpoint performance:")
    print(f"  Average: {avg_time:.2f} ms")
    print(f"  Min: {min_time:.2f} ms")
    print(f"  Max: {max_time:.2f} ms")
    
    # Assert performance meets requirements
    assert avg_time < AUTHOR_LIST_THRESHOLD, f"Average response time ({avg_time:.2f} ms) exceeds threshold ({AUTHOR_LIST_THRESHOLD} ms)"


@pytest.mark.performance
def test_author_detail_endpoint_performance():
    """Benchmark the performance of the author detail endpoint."""
    # First get an author ID to test with
    response = client.get("/api/authors")
    authors = response.json()
    assert len(authors) > 0
    author_id = authors[0]["id"]
    
    response_times = []
    
    for _ in range(ITERATIONS):
        start_time = time.time()
        response = client.get(f"/api/authors/{author_id}")
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Print results
    print(f"\nAuthor detail endpoint performance:")
    print(f"  Author ID: {author_id}")
    print(f"  Average: {avg_time:.2f} ms")
    print(f"  Min: {min_time:.2f} ms")
    print(f"  Max: {max_time:.2f} ms")
    
    # Assert performance meets requirements
    assert avg_time < AUTHOR_DETAIL_THRESHOLD, f"Average response time ({avg_time:.2f} ms) exceeds threshold ({AUTHOR_DETAIL_THRESHOLD} ms)"


@pytest.mark.performance
def test_author_works_endpoint_performance():
    """Benchmark the performance of the author works endpoint."""
    # First get an author ID to test with
    response = client.get("/api/authors")
    authors = response.json()
    assert len(authors) > 0
    author_id = authors[0]["id"]
    
    response_times = []
    
    for _ in range(ITERATIONS):
        start_time = time.time()
        response = client.get(f"/api/authors/{author_id}/works")
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Print results
    print(f"\nAuthor works endpoint performance:")
    print(f"  Author ID: {author_id}")
    print(f"  Average: {avg_time:.2f} ms")
    print(f"  Min: {min_time:.2f} ms")
    print(f"  Max: {max_time:.2f} ms")
    
    # Assert performance meets requirements
    assert avg_time < AUTHOR_WORKS_THRESHOLD, f"Average response time ({avg_time:.2f} ms) exceeds threshold ({AUTHOR_WORKS_THRESHOLD} ms)"


@pytest.mark.performance
def test_concurrent_requests_performance():
    """Test performance under concurrent load."""
    endpoints = [
        ("/api/authors", "Authors list"),
        ("/api/preferences", "Preferences"),
        ("/api/health", "Health check")
    ]
    
    for url, name in endpoints:
        avg_time, min_time, max_time, success_rate = run_concurrent_requests(url, num_requests=20)
        
        # Print results
        print(f"\nConcurrent requests performance for {name}:")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  Min: {min_time:.2f} ms")
        print(f"  Max: {max_time:.2f} ms")
        print(f"  Success rate: {success_rate:.2f}%")
        
        # Assert success rate is acceptable
        assert success_rate >= 95, f"Success rate for {name} ({success_rate:.2f}%) is below threshold (95%)"


if __name__ == "__main__":
    # Run all performance tests and print results
    test_authors_endpoint_performance()
    test_author_detail_endpoint_performance()
    test_author_works_endpoint_performance()
    test_concurrent_requests_performance() 