#!/usr/bin/env python3
"""Integration tests for the hybrid server mode.

These tests verify that both HTTP and FastAPI servers can run simultaneously
and communicate with the same data sources.
"""

import os
import sys
import unittest
import time
import json
import socket
import threading
import requests
from unittest import mock
from contextlib import contextmanager

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.test_base import BaseTest
from src.first1k.utils.network import find_available_port
from src.first1k.config import USER_PREFS_FILE

# Import server modules - use try/except to handle possible import errors
try:
    from src.first1k.server.hybrid_server import HybridServer
    HYBRID_SERVER_AVAILABLE = True
except ImportError:
    HYBRID_SERVER_AVAILABLE = False


@unittest.skipIf(not HYBRID_SERVER_AVAILABLE, "Hybrid server not available")
class HybridServerTests(BaseTest):
    """Test cases for the hybrid server mode."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()

        # Find available ports for testing
        self.http_port = find_available_port(start_port=8800)
        self.fastapi_port = find_available_port(start_port=8900)

        # Set up patches for server configuration
        self.config_patches = []
        
        # Patch USER_PREFS_FILE to use our test file
        self.prefs_file_path = os.path.join(self.temp_dir, 'user_preferences.json')
        self.prefs_patch = mock.patch('src.first1k.config.USER_PREFS_FILE', 
                                      self.prefs_file_path)
        self.prefs_patch.start()
        self.config_patches.append(self.prefs_patch)
        
        # Patch DATA_DIR to use our test directory
        self.data_dir_patch = mock.patch('src.first1k.config.DATA_DIR', 
                                         self.data_dir)
        self.data_dir_patch.start()
        self.config_patches.append(self.data_dir_patch)
        
        # Other necessary patches to avoid file system dependencies
        self.authors_data_patch = mock.patch('src.first1k.server.hybrid_server.AUTHORS_DATA', 
                                             self.mock_authors_data)
        self.authors_data_patch.start()
        self.config_patches.append(self.authors_data_patch)

    def tearDown(self):
        """Clean up test environment."""
        # Stop all patches
        for patch in self.config_patches:
            patch.stop()
        
        super().tearDown()

    @contextmanager
    def run_hybrid_server(self, timeout=5):
        """Run the hybrid server in a separate thread with proper resource management.
        
        Args:
            timeout: Maximum time to wait for server startup in seconds
            
        Yields:
            tuple: (http_url, fastapi_url) for making requests
        """
        # Create the server
        server = HybridServer(
            http_port=self.http_port,
            fastapi_port=self.fastapi_port,
            debug=True,
            no_browser=True
        )
        
        # Set server references for cleanup
        http_server = None
        fastapi_app = None
        server_thread = None
        
        try:
            # Start server in a separate thread
            server_thread = threading.Thread(target=server.start)
            server_thread.daemon = True  # Daemon thread will be killed when the main thread exits
            server_thread.start()
            
            # Store references for cleanup
            # Access these early to avoid AttributeError if server fails to start
            if hasattr(server, 'http_server'):
                http_server = server.http_server
            if hasattr(server, 'fastapi_app'):
                fastapi_app = server.fastapi_app
            
            # Wait for servers to start (with timeout)
            start_time = time.time()
            both_up = False
            
            while time.time() - start_time < timeout and not both_up:
                try:
                    # Check if HTTP server is up
                    http_response = requests.get(f"http://localhost:{self.http_port}/", timeout=0.5)
                    # Check if FastAPI server is up
                    fastapi_response = requests.get(f"http://localhost:{self.fastapi_port}/", timeout=0.5)
                    both_up = True
                except (requests.RequestException, socket.error):
                    # Wait a bit and retry
                    time.sleep(0.1)
            
            if not both_up:
                raise TimeoutError(f"Hybrid server failed to start within {timeout} seconds")
            
            # Provide the server URLs to the test
            yield (
                f"http://localhost:{self.http_port}",
                f"http://localhost:{self.fastapi_port}"
            )
            
        finally:
            # Cleanup resources
            if server and hasattr(server, 'stop'):
                try:
                    server.stop()
                except Exception:
                    pass  # Ignore errors during cleanup
            
            # Make sure server thread is terminated
            if server_thread and server_thread.is_alive():
                # Wait for thread to finish (with timeout)
                server_thread.join(timeout=2)
            
            # Force cleanup of server resources if they still exist
            # This handles the case where server.stop() fails
            if http_server:
                try:
                    http_server.shutdown()
                    http_server.server_close()
                except Exception:
                    pass
            
            # Sleep briefly to ensure sockets are fully released
            time.sleep(0.5)

    def test_http_server_home_page(self):
        """Test that the HTTP server serves the home page."""
        with self.run_hybrid_server() as (http_url, _):
            # Make a request to the HTTP server
            response = requests.get(http_url)
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<!DOCTYPE html>", response.content)
            self.assertIn(b"First1K Greek Browser", response.content)

    def test_fastapi_server_authors_endpoint(self):
        """Test that the FastAPI server serves the authors API endpoint."""
        with self.run_hybrid_server() as (_, fastapi_url):
            # Make a request to the FastAPI server
            response = requests.get(f"{fastapi_url}/api/authors/")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            authors = response.json()
            self.assertIsInstance(authors, list)

    def test_both_servers_share_data(self):
        """Test that both servers access the same data."""
        with self.run_hybrid_server() as (http_url, fastapi_url):
            # 1. Use HTTP server to add an author to favorites
            author_id = "auth001"
            http_response = requests.post(
                f"{http_url}/update_preference",
                data={"author_id": author_id, "pref_type": "favorites", "value": "true"}
            )
            self.assertEqual(http_response.status_code, 200)
            
            # 2. Check with FastAPI server that the author is now in favorites
            fastapi_response = requests.get(f"{fastapi_url}/api/preferences/")
            self.assertEqual(fastapi_response.status_code, 200)
            prefs = fastapi_response.json()
            self.assertIn(author_id, prefs["favorites"])

    def test_error_handling(self):
        """Test error handling in both servers."""
        with self.run_hybrid_server() as (http_url, fastapi_url):
            # Test HTTP server error handling
            http_response = requests.get(f"{http_url}/nonexistent")
            self.assertEqual(http_response.status_code, 404)
            
            # Test FastAPI server error handling
            fastapi_response = requests.get(f"{fastapi_url}/api/authors/nonexistent")
            self.assertEqual(fastapi_response.status_code, 404)
            error = fastapi_response.json()
            self.assertIn("detail", error)


if __name__ == '__main__':
    unittest.main() 