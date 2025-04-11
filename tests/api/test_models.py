#!/usr/bin/env python3
"""Tests for Pydantic models in the FastAPI implementation."""

import os
import sys
import unittest
import json
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.first1k.models import (
    Author, Work, WorkFile, UserPreference, BatchPreferences,
    SearchQuery, SearchResult, SearchResponse, APIResponse
)


class ModelTests(unittest.TestCase):
    """Test cases for Pydantic models."""

    def test_author_model(self):
        """Test the Author model validation and serialization."""
        # Test valid data
        author_data = {
            "id": "auth001",
            "name": "Test Author",
            "century": -5,
            "type": "Historian"
        }
        author = Author(**author_data)
        self.assertEqual(author.id, "auth001")
        self.assertEqual(author.name, "Test Author")
        self.assertEqual(author.century, -5)
        self.assertEqual(author.type, "Historian")
        
        # Test serialization to dict
        self.assertEqual(author.dict(), author_data)
        
        # Test serialization to JSON
        author_json = author.json()
        self.assertEqual(json.loads(author_json), author_data)
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            Author(id="auth001", name="Test Author", century=-5)  # Missing type
    
    def test_work_model(self):
        """Test the Work model validation and serialization."""
        # Test valid data
        work_data = {
            "id": "work001",
            "title": "Test Work",
            "author_id": "auth001",
            "language": "grc",
            "file_path": "data/auth001/work001/test.xml",
            "is_favorite": True,
            "is_archived": False,
            "files": [
                {"name": "test.xml", "type": "xml", "path": "data/auth001/work001/test.xml"}
            ]
        }
        work = Work(**work_data)
        self.assertEqual(work.id, "work001")
        self.assertEqual(work.title, "Test Work")
        self.assertEqual(work.author_id, "auth001")
        self.assertEqual(work.language, "grc")
        self.assertEqual(work.file_path, "data/auth001/work001/test.xml")
        self.assertEqual(work.is_favorite, True)
        self.assertEqual(work.is_archived, False)
        self.assertEqual(len(work.files), 1)
        self.assertEqual(work.files[0].name, "test.xml")
        
        # Test default values
        minimal_work = Work(id="work001", title="Test Work", author_id="auth001", file_path="data/auth001/work001/test.xml")
        self.assertEqual(minimal_work.language, "grc")  # Default language
        self.assertEqual(minimal_work.is_favorite, False)  # Default is_favorite
        self.assertEqual(minimal_work.is_archived, False)  # Default is_archived
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            Work(id="work001", title="Test Work")  # Missing author_id
    
    def test_work_file_model(self):
        """Test the WorkFile model validation and serialization."""
        # Test valid data
        file_data = {
            "name": "test.xml",
            "type": "xml",
            "path": "data/auth001/work001/test.xml"
        }
        file = WorkFile(**file_data)
        self.assertEqual(file.name, "test.xml")
        self.assertEqual(file.type, "xml")
        self.assertEqual(file.path, "data/auth001/work001/test.xml")
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            WorkFile(name="test.xml", type="xml")  # Missing path
    
    def test_user_preference_model(self):
        """Test the UserPreference model validation and serialization."""
        # Test with work_id
        pref_with_work = UserPreference(
            author_id="auth001",
            work_id="work001",
            preference_type="favorites",
            value=True
        )
        self.assertEqual(pref_with_work.author_id, "auth001")
        self.assertEqual(pref_with_work.work_id, "work001")
        self.assertEqual(pref_with_work.preference_type, "favorites")
        self.assertEqual(pref_with_work.value, True)
        
        # Test without work_id (None is valid)
        pref_without_work = UserPreference(
            author_id="auth001",
            preference_type="favorites",
            value=True
        )
        self.assertEqual(pref_without_work.author_id, "auth001")
        self.assertIsNone(pref_without_work.work_id)
        self.assertEqual(pref_without_work.preference_type, "favorites")
        self.assertEqual(pref_without_work.value, True)
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            UserPreference(author_id="auth001", preference_type="favorites")  # Missing value
    
    def test_batch_preferences_model(self):
        """Test the BatchPreferences model validation and serialization."""
        # Test valid data
        batch_data = {
            "preferences": [
                {
                    "author_id": "auth001",
                    "work_id": "work001",
                    "preference_type": "favorites",
                    "value": True
                },
                {
                    "author_id": "auth002",
                    "preference_type": "archived",
                    "value": False
                }
            ]
        }
        batch = BatchPreferences(**batch_data)
        self.assertEqual(len(batch.preferences), 2)
        self.assertEqual(batch.preferences[0].author_id, "auth001")
        self.assertEqual(batch.preferences[0].work_id, "work001")
        self.assertEqual(batch.preferences[1].author_id, "auth002")
        self.assertIsNone(batch.preferences[1].work_id)
        
        # Test validation error for empty preferences list
        with self.assertRaises(ValidationError):
            BatchPreferences(preferences=[])
    
    def test_search_query_model(self):
        """Test the SearchQuery model validation and serialization."""
        # Test with minimal data
        query = SearchQuery(query="test")
        self.assertEqual(query.query, "test")
        self.assertIsNone(query.authors)
        self.assertIsNone(query.language)
        self.assertEqual(query.max_results, 100)  # Default value
        
        # Test with all fields
        full_query = SearchQuery(
            query="test",
            authors=["auth001", "auth002"],
            language="grc",
            max_results=50
        )
        self.assertEqual(full_query.query, "test")
        self.assertEqual(full_query.authors, ["auth001", "auth002"])
        self.assertEqual(full_query.language, "grc")
        self.assertEqual(full_query.max_results, 50)
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            SearchQuery()  # Missing query
    
    def test_search_result_model(self):
        """Test the SearchResult model validation and serialization."""
        # Test valid data
        result_data = {
            "author_id": "auth001",
            "work_id": "work001",
            "file_path": "data/auth001/work001/test.xml",
            "excerpt": "This is a <em>test</em> excerpt",
            "language": "grc"
        }
        result = SearchResult(**result_data)
        self.assertEqual(result.author_id, "auth001")
        self.assertEqual(result.work_id, "work001")
        self.assertEqual(result.file_path, "data/auth001/work001/test.xml")
        self.assertEqual(result.excerpt, "This is a <em>test</em> excerpt")
        self.assertEqual(result.language, "grc")
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            SearchResult(author_id="auth001", work_id="work001", file_path="path", language="grc")  # Missing excerpt
    
    def test_search_response_model(self):
        """Test the SearchResponse model validation and serialization."""
        # Test valid data
        response_data = {
            "query": "test",
            "results": [
                {
                    "author_id": "auth001",
                    "work_id": "work001",
                    "file_path": "data/auth001/work001/test.xml",
                    "excerpt": "This is a <em>test</em> excerpt",
                    "language": "grc"
                }
            ],
            "total_found": 1,
            "executed_in": 0.123
        }
        response = SearchResponse(**response_data)
        self.assertEqual(response.query, "test")
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].author_id, "auth001")
        self.assertEqual(response.total_found, 1)
        self.assertEqual(response.executed_in, 0.123)
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            SearchResponse(query="test", results=[])  # Missing total_found and executed_in
    
    def test_api_response_model(self):
        """Test the APIResponse model validation and serialization."""
        # Test without data
        response = APIResponse(success=True, message="Success")
        self.assertEqual(response.success, True)
        self.assertEqual(response.message, "Success")
        self.assertIsNone(response.data)
        
        # Test with data
        response_with_data = APIResponse(
            success=False,
            message="Error message",
            data={"error": "Invalid request"}
        )
        self.assertEqual(response_with_data.success, False)
        self.assertEqual(response_with_data.message, "Error message")
        self.assertEqual(response_with_data.data, {"error": "Invalid request"})
        
        # Test validation error for missing required field
        with self.assertRaises(ValidationError):
            APIResponse(success=True)  # Missing message


if __name__ == '__main__':
    unittest.main() 