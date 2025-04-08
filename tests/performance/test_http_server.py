#!/usr/bin/env python3
"""Performance tests for First1KGreek Browser HTTP server."""

import unittest
import time
import urllib.request
import urllib.error
import threading
import statistics
import socket
import logging
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.first1k.server.server import run_server, server_instance
from src.first1k.utils.network import find_available_port

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class HTTPServerPerformanceTest(unittest.TestCase):
    """Performance test case for HTTP server."""

    @classmethod
    def setUpClass(cls):
        """Start a server for testing."""
        # Find an available port
        cls.port = find_available_port(8123)  # Use a different port than default
        
        # Start server in a separate thread
        cls.server_thread = threading.Thread(
            target=run_server,
            args=(cls.port, True),  # port, debug
            daemon=True  # Allow the thread to be killed when the test exits
        )
        cls.server_thread.start()
        
        # Wait for server to start
        cls.wait_for_server(cls.port)
        
        # Base URL for requests
        cls.base_url = f"http://localhost:{cls.port}"
        
        # Performance thresholds (in seconds)
        cls.thresholds = {
            "home": 0.5,
            "authors": 1.0,
            "search": 1.0,
            "works": 1.0,
            "view": 2.0
        }
    
    @classmethod
    def tearDownClass(cls):
        """Stop the server after testing."""
        if server_instance:
            server_instance.shutdown()
            cls.server_thread.join(timeout=2.0)
    
    @staticmethod
    def wait_for_server(port, max_attempts=10, delay=0.5):
        """Wait for server to start accepting connections."""
        for attempt in range(max_attempts):
            try:
                with socket.create_connection(("localhost", port), timeout=1.0):
                    # Connection successful
                    time.sleep(1.0)  # Give server a little more time to initialize
                    return True
            except (socket.timeout, ConnectionRefusedError):
                if attempt < max_attempts - 1:
                    time.sleep(delay)
        
        raise RuntimeError(f"Server did not start on port {port} after {max_attempts} attempts")
    
    def make_request(self, url):
        """Make a request and measure response time."""
        start_time = time.time()
        try:
            with urllib.request.urlopen(url, timeout=5.0) as response:
                content = response.read()
                status = response.status
        except urllib.error.URLError as e:
            self.fail(f"Request failed: {e}")
        
        response_time = time.time() - start_time
        return response_time, status, len(content)
    
    def perform_requests(self, url, name, n=5):
        """Perform multiple requests and calculate statistics."""
        print(f"\nTesting {name} performance...")
        print(f"URL: {url}")
        
        times = []
        for i in range(n):
            response_time, status, size = self.make_request(url)
            times.append(response_time)
            print(f"  Request {i+1}: {response_time:.3f}s, Status: {status}, Size: {size} bytes")
            time.sleep(0.2)  # Avoid overwhelming the server
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        median_time = statistics.median(times)
        
        print(f"Results for {name}:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median:  {median_time:.3f}s")
        print(f"  Min:     {min_time:.3f}s")
        print(f"  Max:     {max_time:.3f}s")
        
        # Check performance against threshold
        threshold = self.thresholds.get(name, 1.0)
        self.assertLess(
            avg_time, threshold,
            f"{name} average response time ({avg_time:.3f}s) exceeds threshold ({threshold}s)"
        )
        
        return {
            "avg": avg_time,
            "median": median_time,
            "min": min_time,
            "max": max_time
        }
    
    def test_home_page_performance(self):
        """Test the home page response time."""
        self.perform_requests(f"{self.base_url}/", "home")
    
    def test_authors_page_performance(self):
        """Test the authors page response time."""
        self.perform_requests(f"{self.base_url}/browse/authors", "authors")
    
    def test_search_page_performance(self):
        """Test the search page response time."""
        self.perform_requests(f"{self.base_url}/search?q=Aristotle", "search")
    
    def test_works_page_performance(self):
        """Test the works page response time."""
        self.perform_requests(f"{self.base_url}/works?author=tlg0086", "works")  # Aristotle
    
    def test_all_pages_sequence(self):
        """Test a typical user sequence of page visits."""
        print("\nTesting full user sequence...")
        
        sequence = [
            (f"{self.base_url}/", "home"),
            (f"{self.base_url}/browse/authors", "authors"),
            (f"{self.base_url}/works?author=tlg0086", "works"),  # Aristotle
            (f"{self.base_url}/search?q=ethics", "search"),
        ]
        
        results = {}
        for url, name in sequence:
            result = self.perform_requests(url, name, n=3)
            results[name] = result
        
        # Calculate overall statistics
        overall_times = []
        for name, stats in results.items():
            overall_times.append(stats["avg"])
        
        total_time = sum(overall_times)
        avg_time = statistics.mean(overall_times)
        
        print("\nOverall Sequence Results:")
        print(f"  Total sequence time: {total_time:.3f}s")
        print(f"  Average page time:   {avg_time:.3f}s")
        
        self.assertLess(
            avg_time, 1.5,
            f"Average page response time ({avg_time:.3f}s) exceeds threshold (1.5s)"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2) 