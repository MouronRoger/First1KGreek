#!/usr/bin/env python3
"""Tests for the view API endpoints."""

import os
import sys
import unittest
from unittest import mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.test_base import BaseTest
from fastapi.testclient import TestClient
from src.first1k.api import app


class ViewAPITests(BaseTest):
    """Test cases for view API endpoints."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = TestClient(app)

    def test_view_xml(self):
        """Test the GET /api/view/xml endpoint."""
        # Mock the async_render_xml_view_page function
        with mock.patch('src.first1k.handlers.view.async_render_xml_view_page') as mock_render, \
             mock.patch('os.path.exists') as mock_exists:
            
            # Setup the mocks
            mock_exists.return_value = True
            mock_render.return_value = "<html><body><pre>XML content</pre></body></html>"
            
            # Call the API endpoint
            response = self.client.get("/api/view/xml?path=data/auth001/work001/test.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "<html><body><pre>XML content</pre></body></html>")
            self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
            
            # Verify the mocks were called correctly
            mock_exists.assert_called_once_with("data/auth001/work001/test.xml")
            mock_render.assert_called_once_with("data/auth001/work001/test.xml")

    def test_view_xml_file_not_found(self):
        """Test the GET /api/view/xml endpoint with non-existent file."""
        # Mock the os.path.exists function
        with mock.patch('os.path.exists') as mock_exists:
            # Setup the mock
            mock_exists.return_value = False
            
            # Call the API endpoint
            response = self.client.get("/api/view/xml?path=data/nonexistent.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 404)
            error = response.json()
            self.assertIn("File not found", error["detail"])
            
            # Verify the mock was called correctly
            mock_exists.assert_called_once_with("data/nonexistent.xml")

    def test_view_xml_invalid_file_type(self):
        """Test the GET /api/view/xml endpoint with non-XML file."""
        # Mock the os.path.exists function
        with mock.patch('os.path.exists') as mock_exists:
            # Setup the mock
            mock_exists.return_value = True
            
            # Call the API endpoint
            response = self.client.get("/api/view/xml?path=data/auth001/work001/test.txt")
            
            # Verify the response
            self.assertEqual(response.status_code, 400)
            error = response.json()
            self.assertIn("Only XML files are supported", error["detail"])

    def test_view_reader(self):
        """Test the GET /api/view/reader endpoint."""
        # Mock the necessary functions
        with mock.patch('src.first1k.handlers.view.async_render_reader_view_page') as mock_render, \
             mock.patch('os.path.exists') as mock_exists:
            
            # Setup the mocks
            mock_exists.return_value = True
            mock_render.return_value = "<html><body><div class='reader'>Reader content</div></body></html>"
            
            # Call the API endpoint
            response = self.client.get("/api/view/reader?path=data/auth001/work001/test.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "<html><body><div class='reader'>Reader content</div></body></html>")
            self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
            
            # Verify the mocks were called correctly
            mock_exists.assert_called_once_with("data/auth001/work001/test.xml")
            mock_render.assert_called_once_with("data/auth001/work001/test.xml")

    def test_view_reader_file_not_found(self):
        """Test the GET /api/view/reader endpoint with non-existent file."""
        # Mock the os.path.exists function
        with mock.patch('os.path.exists') as mock_exists:
            # Setup the mock
            mock_exists.return_value = False
            
            # Call the API endpoint
            response = self.client.get("/api/view/reader?path=data/nonexistent.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 404)
            error = response.json()
            self.assertIn("File not found", error["detail"])
            
            # Verify the mock was called correctly
            mock_exists.assert_called_once_with("data/nonexistent.xml")

    def test_view_raw(self):
        """Test the GET /api/view/raw endpoint."""
        # Mock the necessary functions
        with mock.patch('src.first1k.handlers.view.async_handle_view_raw') as mock_view_raw, \
             mock.patch('os.path.exists') as mock_exists:
            
            # Setup the mocks
            mock_exists.return_value = True
            mock_view_raw.return_value = (200, "text/plain", "Raw file content")
            
            # Call the API endpoint
            response = self.client.get("/api/view/raw?path=data/auth001/work001/test.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "Raw file content")
            self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")
            
            # Verify the mocks were called correctly
            mock_exists.assert_called_once_with("data/auth001/work001/test.xml")
            mock_view_raw.assert_called_once_with({"path": "data/auth001/work001/test.xml"})

    def test_view_raw_file_not_found(self):
        """Test the GET /api/view/raw endpoint with non-existent file."""
        # Mock the os.path.exists function
        with mock.patch('os.path.exists') as mock_exists:
            # Setup the mock
            mock_exists.return_value = False
            
            # Call the API endpoint
            response = self.client.get("/api/view/raw?path=data/nonexistent.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 404)
            error = response.json()
            self.assertIn("File not found", error["detail"])
            
            # Verify the mock was called correctly
            mock_exists.assert_called_once_with("data/nonexistent.xml")

    def test_view_raw_error(self):
        """Test the GET /api/view/raw endpoint with an error from the handler."""
        # Mock the necessary functions
        with mock.patch('src.first1k.handlers.view.async_handle_view_raw') as mock_view_raw, \
             mock.patch('os.path.exists') as mock_exists:
            
            # Setup the mocks
            mock_exists.return_value = True
            mock_view_raw.return_value = (500, "application/json", "Error reading file")
            
            # Call the API endpoint
            response = self.client.get("/api/view/raw?path=data/auth001/work001/test.xml")
            
            # Verify the response
            self.assertEqual(response.status_code, 500)
            error = response.json()
            self.assertIn("Error reading file", error["detail"])
            
            # Verify the mocks were called correctly
            mock_exists.assert_called_once_with("data/auth001/work001/test.xml")
            mock_view_raw.assert_called_once_with({"path": "data/auth001/work001/test.xml"})


if __name__ == '__main__':
    unittest.main() 