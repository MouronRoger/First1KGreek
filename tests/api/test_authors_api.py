#!/usr/bin/env python3
"""Tests for the authors API endpoints."""

import os
import sys
import unittest
import json
from unittest import mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.test_base import BaseTest
from fastapi.testclient import TestClient
from src.first1k.api import app
from src.first1k.models import Author


class AuthorsAPITests(BaseTest):
    """Test cases for authors API endpoints."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = TestClient(app)

    def test_list_authors(self):
        """Test the GET /api/authors endpoint."""
        # Mock the async_get_filtered_authors function
        with mock.patch('src.first1k.data.authors.async_get_filtered_authors') as mock_get_authors:
            # Setup the mock response
            mock_get_authors.return_value = [
                {"id": "auth001", "name": "Test Author 1", "century": -2, "type": "Stoic"},
                {"id": "auth002", "name": "Test Author 2", "century": 1, "type": "Epicurean"}
            ]
            
            # Call the API endpoint
            response = self.client.get("/api/authors/")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            authors = response.json()
            self.assertEqual(len(authors), 2)
            self.assertEqual(authors[0]["id"], "auth001")
            self.assertEqual(authors[0]["name"], "Test Author 1")
            self.assertEqual(authors[0]["century"], -2)
            self.assertEqual(authors[0]["type"], "Stoic")
            
            # Verify the mock was called correctly
            mock_get_authors.assert_called_once_with(century=None, author_type=None, skip=0, limit=100)

    def test_list_authors_with_filters(self):
        """Test the GET /api/authors endpoint with filters."""
        # Mock the async_get_filtered_authors function
        with mock.patch('src.first1k.data.authors.async_get_filtered_authors') as mock_get_authors:
            # Setup the mock response
            mock_get_authors.return_value = [
                {"id": "auth001", "name": "Test Author 1", "century": -2, "type": "Stoic"}
            ]
            
            # Call the API endpoint with filters
            response = self.client.get("/api/authors/?century=-2&type=Stoic&skip=0&limit=10")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            authors = response.json()
            self.assertEqual(len(authors), 1)
            self.assertEqual(authors[0]["id"], "auth001")
            
            # Verify the mock was called correctly
            mock_get_authors.assert_called_once_with(century=-2, author_type="Stoic", skip=0, limit=10)

    def test_get_author(self):
        """Test the GET /api/authors/{author_id} endpoint."""
        # Mock the async_get_author_by_id function
        with mock.patch('src.first1k.data.authors.async_get_author_by_id') as mock_get_author:
            # Setup the mock response
            mock_get_author.return_value = {
                "name": "Test Author 1", 
                "century": -2, 
                "type": "Stoic"
            }
            
            # Call the API endpoint
            response = self.client.get("/api/authors/auth001")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            author = response.json()
            self.assertEqual(author["id"], "auth001")
            self.assertEqual(author["name"], "Test Author 1")
            self.assertEqual(author["century"], -2)
            self.assertEqual(author["type"], "Stoic")
            
            # Verify the mock was called correctly
            mock_get_author.assert_called_once_with("auth001")

    def test_get_author_not_found(self):
        """Test the GET /api/authors/{author_id} endpoint with non-existent author."""
        # Mock the async_get_author_by_id function
        with mock.patch('src.first1k.data.authors.async_get_author_by_id') as mock_get_author:
            # Setup the mock response
            mock_get_author.return_value = None
            
            # Call the API endpoint
            response = self.client.get("/api/authors/nonexistent")
            
            # Verify the response
            self.assertEqual(response.status_code, 404)
            error = response.json()
            self.assertEqual(error["detail"], "Author nonexistent not found")
            
            # Verify the mock was called correctly
            mock_get_author.assert_called_once_with("nonexistent")

    def test_get_author_works(self):
        """Test the GET /api/authors/{author_id}/works endpoint."""
        # Mock the necessary functions
        with mock.patch('os.path.exists') as mock_exists, \
             mock.patch('os.path.isdir') as mock_isdir, \
             mock.patch('src.first1k.utils.api_handler.get_author_works_for_api') as mock_get_works:
            
            # Setup the mocks
            mock_exists.return_value = True
            mock_isdir.return_value = True
            mock_get_works.return_value = [
                {
                    "id": "work001",
                    "title": "Work 1",
                    "author_id": "auth001",
                    "language": "grc",
                    "file_path": "data/auth001/work001/test.xml",
                    "is_favorite": True,
                    "is_archived": False,
                    "files": [
                        {"name": "test.xml", "type": "xml", "path": "data/auth001/work001/test.xml"}
                    ]
                }
            ]
            
            # Call the API endpoint
            response = self.client.get("/api/authors/auth001/works")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            works = response.json()
            self.assertEqual(len(works), 1)
            self.assertEqual(works[0]["id"], "work001")
            self.assertEqual(works[0]["title"], "Work 1")
            self.assertEqual(works[0]["author_id"], "auth001")
            self.assertEqual(works[0]["language"], "grc")
            self.assertEqual(works[0]["file_path"], "data/auth001/work001/test.xml")
            self.assertEqual(works[0]["is_favorite"], True)
            self.assertEqual(works[0]["is_archived"], False)
            self.assertEqual(len(works[0]["files"]), 1)
            self.assertEqual(works[0]["files"][0]["name"], "test.xml")
            
            # Verify the mocks were called correctly
            mock_exists.assert_called()
            mock_isdir.assert_called()
            mock_get_works.assert_called_once_with("auth001")

    def test_get_author_works_author_not_found(self):
        """Test the GET /api/authors/{author_id}/works endpoint with non-existent author."""
        # Mock the necessary functions
        with mock.patch('os.path.exists') as mock_exists:
            # Setup the mocks
            mock_exists.return_value = False
            
            # Call the API endpoint
            response = self.client.get("/api/authors/nonexistent/works")
            
            # Verify the response
            self.assertEqual(response.status_code, 404)
            error = response.json()
            self.assertEqual(error["detail"], "Author nonexistent not found")


if __name__ == '__main__':
    unittest.main() 