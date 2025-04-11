#!/usr/bin/env python3
"""Performance tests for the FastAPI implementation.

These tests measure response times and set baseline expectations for API endpoints.
"""

import os
import sys
import unittest
import time
import statistics
import json
from unittest import mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try to import FastAPI specific modules
try:
    from fastapi.testclient import TestClient
    from src.first1k.api import app
    from src.first1k.models import Author, Work
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from tests.test_base import BaseTest


@unittest.skipIf(not FASTAPI_AVAILABLE, "FastAPI not available")
class APIPerformanceTests(BaseTest):
    """Performance tests for the FastAPI API endpoints."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = TestClient(app)
        
        # Set up patches for test data
        self.setup_performance_test_data()
        
        # Performance thresholds (in milliseconds)
        self.thresholds = {
            "list_authors": 5.0,
            "get_author": 3.0,
            "get_author_works": 5.0,
            "search": 10.0,
            "view_xml": 15.0  # XML processing is more expensive
        }
        
        # Number of test iterations
        self.iterations = 10

    def setup_performance_test_data(self):
        """Set up test data for performance testing.
        
        This creates a larger dataset than the regular unit tests
        to better simulate production conditions.
        """
        # Mock the async_get_filtered_authors function to return many authors
        self.get_authors_patch = mock.patch(
            'src.first1k.data.authors.async_get_filtered_authors')
        self.mock_get_authors = self.get_authors_patch.start()
        self.patches.append(self.get_authors_patch)
        
        # Create 100 test authors
        self.mock_authors = [
            {"id": f"auth{i:03d}", "name": f"Test Author {i}", 
             "century": (i % 10) - 5, "type": "Poet" if i % 2 == 0 else "Historian"}
            for i in range(100)
        ]
        self.mock_get_authors.return_value = self.mock_authors
        
        # Mock the async_get_author_by_id function
        self.get_author_patch = mock.patch(
            'src.first1k.data.authors.async_get_author_by_id')
        self.mock_get_author = self.get_author_patch.start()
        self.patches.append(self.get_author_patch)
        self.mock_get_author.return_value = self.mock_authors[0]
        
        # Mock the get_author_works_for_api function
        self.get_works_patch = mock.patch(
            'src.first1k.utils.api_handler.get_author_works_for_api')
        self.mock_get_works = self.get_works_patch.start()
        self.patches.append(self.get_works_patch)
        
        # Create 20 test works
        self.mock_works = [
            {
                "id": f"work{i:03d}",
                "title": f"Test Work {i}",
                "author_id": "auth001",
                "language": "grc" if i % 2 == 0 else "eng",
                "file_path": f"data/auth001/work{i:03d}/test.xml",
                "is_favorite": i % 3 == 0,
                "is_archived": i % 5 == 0,
                "files": [
                    {"name": "test.xml", "type": "xml", "path": f"data/auth001/work{i:03d}/test.xml"}
                ]
            }
            for i in range(20)
        ]
        self.mock_get_works.return_value = self.mock_works
        
        # Mock the async_search_corpus function
        self.search_patch = mock.patch(
            'src.first1k.handlers.search.async_search_corpus')
        self.mock_search = self.search_patch.start()
        self.patches.append(self.search_patch)
        
        # Create 50 search results
        self.mock_search_results = [
            {
                "file_path": f"data/auth{i//5:03d}/work{i%10:03d}/test.xml",
                "context": f"This is search result {i} with <em>test</em> keyword."
            }
            for i in range(50)
        ]
        self.mock_search.return_value = self.mock_search_results
        
        # Set up XML rendering mocks
        self.render_xml_patch = mock.patch(
            'src.first1k.handlers.view.async_render_xml_view_page')
        self.mock_render_xml = self.render_xml_patch.start()
        self.patches.append(self.render_xml_patch)
        self.mock_render_xml.return_value = "<html><body><pre>Test XML content</pre></body></html>"
        
        # Mock os.path.exists to always return True for path checks
        self.path_exists_patch = mock.patch('os.path.exists')
        self.mock_path_exists = self.path_exists_patch.start()
        self.patches.append(self.path_exists_patch)
        self.mock_path_exists.return_value = True

    def tearDown(self):
        """Clean up test environment."""
        super().tearDown()

    def measure_endpoint_performance(self, endpoint, **kwargs):
        """Measure the performance of an API endpoint.
        
        Args:
            endpoint: Function to call the endpoint (typically a lambda)
            **kwargs: Additional parameters to include in the report
            
        Returns:
            dict: Performance metrics including min, max, mean, median, and p95
        """
        times = []
        
        # Run the endpoint multiple times to get stable measurements
        for _ in range(self.iterations):
            start_time = time.time()
            response = endpoint()
            end_time = time.time()
            
            # Verify the response is valid
            self.assertEqual(response.status_code, 200)
            
            # Record time in milliseconds
            elapsed_ms = (end_time - start_time) * 1000
            times.append(elapsed_ms)
        
        # Calculate statistics
        result = {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "p95": sorted(times)[int(0.95 * len(times))],
            "iterations": self.iterations
        }
        
        # Add any additional context
        result.update(kwargs)
        
        return result

    def test_list_authors_performance(self):
        """Test the performance of the GET /api/authors/ endpoint."""
        endpoint = lambda: self.client.get("/api/authors/")
        
        metrics = self.measure_endpoint_performance(
            endpoint, endpoint_name="list_authors")
        
        # Check against threshold
        self.assertLess(
            metrics["mean"], 
            self.thresholds["list_authors"],
            f"Mean response time {metrics['mean']:.2f}ms exceeds threshold "
            f"{self.thresholds['list_authors']}ms"
        )
        
        # Log detailed metrics for information
        print(f"\nPerformance metrics for list_authors:")
        print(f"  Min: {metrics['min']:.2f}ms")
        print(f"  Max: {metrics['max']:.2f}ms")
        print(f"  Mean: {metrics['mean']:.2f}ms")
        print(f"  Median: {metrics['median']:.2f}ms")
        print(f"  P95: {metrics['p95']:.2f}ms")

    def test_get_author_performance(self):
        """Test the performance of the GET /api/authors/{author_id} endpoint."""
        endpoint = lambda: self.client.get("/api/authors/auth001")
        
        metrics = self.measure_endpoint_performance(
            endpoint, endpoint_name="get_author")
        
        # Check against threshold
        self.assertLess(
            metrics["mean"], 
            self.thresholds["get_author"],
            f"Mean response time {metrics['mean']:.2f}ms exceeds threshold "
            f"{self.thresholds['get_author']}ms"
        )

    def test_get_author_works_performance(self):
        """Test the performance of the GET /api/authors/{author_id}/works endpoint."""
        endpoint = lambda: self.client.get("/api/authors/auth001/works")
        
        metrics = self.measure_endpoint_performance(
            endpoint, endpoint_name="get_author_works")
        
        # Check against threshold
        self.assertLess(
            metrics["mean"], 
            self.thresholds["get_author_works"],
            f"Mean response time {metrics['mean']:.2f}ms exceeds threshold "
            f"{self.thresholds['get_author_works']}ms"
        )

    def test_search_performance(self):
        """Test the performance of the GET /api/search/ endpoint."""
        endpoint = lambda: self.client.get("/api/search/?query=test")
        
        metrics = self.measure_endpoint_performance(
            endpoint, endpoint_name="search")
        
        # Check against threshold
        self.assertLess(
            metrics["mean"], 
            self.thresholds["search"],
            f"Mean response time {metrics['mean']:.2f}ms exceeds threshold "
            f"{self.thresholds['search']}ms"
        )

    def test_view_xml_performance(self):
        """Test the performance of the GET /api/view/xml endpoint."""
        endpoint = lambda: self.client.get(
            "/api/view/xml?path=data/auth001/work001/test.xml")
        
        metrics = self.measure_endpoint_performance(
            endpoint, endpoint_name="view_xml")
        
        # Check against threshold
        self.assertLess(
            metrics["mean"], 
            self.thresholds["view_xml"],
            f"Mean response time {metrics['mean']:.2f}ms exceeds threshold "
            f"{self.thresholds['view_xml']}ms"
        )

    def test_concurrent_requests_performance(self):
        """Test performance with concurrent requests."""
        import concurrent.futures
        
        # List of endpoints to test concurrently
        endpoints = [
            lambda: self.client.get("/api/authors/"),
            lambda: self.client.get("/api/authors/auth001"),
            lambda: self.client.get("/api/authors/auth001/works"),
            lambda: self.client.get("/api/search/?query=test"),
            lambda: self.client.get("/api/view/xml?path=data/auth001/work001/test.xml")
        ]
        
        # Number of concurrent requests for each endpoint
        concurrency = 5
        
        # Create a flat list with all endpoints repeated concurrency times
        all_endpoints = endpoints * concurrency
        
        # Track success/failure
        success_count = 0
        failure_count = 0
        response_times = []
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(all_endpoints)) as executor:
            start_time = time.time()
            futures = [executor.submit(endpoint) for endpoint in all_endpoints]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    response = future.result()
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception:
                    failure_count += 1
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Calculate metrics
        total_requests = len(all_endpoints)
        success_rate = (success_count / total_requests) * 100
        requests_per_second = total_requests / (total_time / 1000)
        
        # Log results
        print(f"\nConcurrent requests performance:")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful: {success_count} ({success_rate:.1f}%)")
        print(f"  Failed: {failure_count}")
        print(f"  Total time: {total_time:.2f}ms")
        print(f"  Requests per second: {requests_per_second:.2f}")
        
        # Check success rate
        self.assertEqual(
            success_count, 
            total_requests,
            f"Only {success_count} of {total_requests} concurrent requests succeeded"
        )


if __name__ == '__main__':
    unittest.main() 