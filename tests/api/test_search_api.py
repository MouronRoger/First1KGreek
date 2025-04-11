#!/usr/bin/env python3
"""Tests for the search API endpoints."""

import os
import sys
import unittest
import json
import time
from unittest import mock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.test_base import BaseTest
from fastapi.testclient import TestClient
from src.first1k.api import app
from src.first1k.models import SearchResponse, SearchResult


class SearchAPITests(BaseTest):
    """Test cases for search API endpoints."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = TestClient(app)

    def test_search_corpus(self):
        """Test the GET /api/search/ endpoint with basic query."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock response
            mock_search.return_value = [
                {
                    "file_path": "data/auth001/work001/auth001.work001.perseus-grc2.xml",
                    "context": "This is a <em>test</em> match in Greek text."
                },
                {
                    "file_path": "data/auth002/work001/auth002.work001.perseus-eng2.xml",
                    "context": "This is another <em>test</em> match in English text."
                }
            ]
            
            # Call the API endpoint
            response = self.client.get("/api/search/?query=test")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            search_response = response.json()
            self.assertEqual(search_response["query"], "test")
            self.assertEqual(len(search_response["results"]), 2)
            self.assertEqual(search_response["total_found"], 2)
            self.assertIsInstance(search_response["executed_in"], float)
            
            # Verify result structure
            result1 = search_response["results"][0]
            self.assertEqual(result1["author_id"], "auth001")
            self.assertEqual(result1["work_id"], "work001")
            self.assertEqual(result1["language"], "grc")
            self.assertEqual(result1["file_path"], "data/auth001/work001/auth001.work001.perseus-grc2.xml")
            self.assertEqual(result1["excerpt"], "This is a <em>test</em> match in Greek text.")
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("test")

    def test_search_corpus_with_author_filter(self):
        """Test the GET /api/search/ endpoint with author filter."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock response
            mock_search.return_value = [
                {
                    "file_path": "data/auth001/work001/auth001.work001.perseus-grc2.xml",
                    "context": "This is a <em>test</em> match in Greek text."
                },
                {
                    "file_path": "data/auth002/work001/auth002.work001.perseus-eng2.xml",
                    "context": "This is another <em>test</em> match in English text."
                }
            ]
            
            # Call the API endpoint with author filter
            response = self.client.get("/api/search/?query=test&authors=auth001")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            search_response = response.json()
            self.assertEqual(len(search_response["results"]), 1)
            self.assertEqual(search_response["results"][0]["author_id"], "auth001")
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("test")

    def test_search_corpus_with_language_filter(self):
        """Test the GET /api/search/ endpoint with language filter."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock response
            mock_search.return_value = [
                {
                    "file_path": "data/auth001/work001/auth001.work001.perseus-grc2.xml",
                    "context": "This is a <em>test</em> match in Greek text."
                },
                {
                    "file_path": "data/auth002/work001/auth002.work001.perseus-eng2.xml",
                    "context": "This is another <em>test</em> match in English text."
                }
            ]
            
            # Call the API endpoint with language filter
            response = self.client.get("/api/search/?query=test&language=eng")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            search_response = response.json()
            self.assertEqual(len(search_response["results"]), 1)
            self.assertEqual(search_response["results"][0]["language"], "eng")
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("test")

    def test_search_corpus_with_max_results(self):
        """Test the GET /api/search/ endpoint with max_results limit."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock response with multiple results
            mock_search.return_value = [
                {"file_path": f"data/auth001/work{i:03d}/auth001.work{i:03d}.perseus-grc2.xml", 
                 "context": f"This is match {i}"} 
                for i in range(10)
            ]
            
            # Call the API endpoint with max_results=5
            response = self.client.get("/api/search/?query=test&max_results=5")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            search_response = response.json()
            self.assertEqual(len(search_response["results"]), 5)
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("test")

    def test_search_corpus_with_empty_results(self):
        """Test the GET /api/search/ endpoint with no matching results."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock response with no results
            mock_search.return_value = []
            
            # Call the API endpoint
            response = self.client.get("/api/search/?query=nonexistent")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            search_response = response.json()
            self.assertEqual(search_response["query"], "nonexistent")
            self.assertEqual(len(search_response["results"]), 0)
            self.assertEqual(search_response["total_found"], 0)
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("nonexistent")

    def test_search_corpus_error(self):
        """Test the GET /api/search/ endpoint with an error from the search function."""
        # Mock the async_search_corpus function
        with mock.patch('src.first1k.handlers.search.async_search_corpus') as mock_search:
            # Setup the mock to raise an exception
            mock_search.side_effect = Exception("Search error")
            
            # Call the API endpoint
            response = self.client.get("/api/search/?query=test")
            
            # Verify the response
            self.assertEqual(response.status_code, 500)
            error = response.json()
            self.assertIn("Error searching corpus", error["detail"])
            
            # Verify the mock was called correctly
            mock_search.assert_called_once_with("test")


if __name__ == '__main__':
    unittest.main() 