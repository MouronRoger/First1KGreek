#!/usr/bin/env python3
"""Integration tests for First1KGreek Browser server."""

import http.server
import socket
import tempfile
import threading
import time
import unittest

import requests


def find_free_port():
    """Find an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Simple HTTP request handler for testing."""

    def log_message(self, format, *args):
        """Override to suppress log messages."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Test Server</h1></body></html>")
        else:
            self.send_error(404, "Not found")


class ServerIntegrationTest(unittest.TestCase):
    """Integration test case for server functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create temporary directory
        cls.test_dir = tempfile.mkdtemp()

        # Find an available port
        cls.port = find_free_port()

        # Start test server in a separate thread
        cls.server_thread = threading.Thread(target=cls.run_test_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Give server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil

        shutil.rmtree(cls.test_dir)

    @classmethod
    def run_test_server(cls):
        """Run a simple HTTP server for testing."""
        server_address = ("localhost", cls.port)
        httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.serve_forever()

    def test_server_response(self):
        """Test that server responds to requests."""
        response = requests.get(f"http://localhost:{self.port}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Server", response.text)

    def test_404_response(self):
        """Test that server returns 404 for nonexistent pages."""
        response = requests.get(f"http://localhost:{self.port}/nonexistent")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
