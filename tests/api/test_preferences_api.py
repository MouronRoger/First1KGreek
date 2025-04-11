#!/usr/bin/env python3
"""Tests for the preferences API endpoints."""

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
from src.first1k.models import UserPreference, BatchPreferences, APIResponse


class PreferencesAPITests(BaseTest):
    """Test cases for preferences API endpoints."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = TestClient(app)

    def test_get_preferences(self):
        """Test the GET /api/preferences/ endpoint."""
        # Mock the get_user_preferences function
        with mock.patch('src.first1k.handlers.preferences.get_user_preferences') as mock_get_prefs:
            # Setup the mock response
            mock_get_prefs.return_value = {
                "favorites": ["auth001.work001", "auth002.work001"],
                "archived": ["auth003.work001"],
                "deleted": []
            }
            
            # Call the API endpoint
            response = self.client.get("/api/preferences/")
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            prefs = response.json()
            self.assertEqual(len(prefs["favorites"]), 2)
            self.assertEqual(prefs["favorites"][0], "auth001.work001")
            self.assertEqual(len(prefs["archived"]), 1)
            self.assertEqual(prefs["archived"][0], "auth003.work001")
            self.assertEqual(len(prefs["deleted"]), 0)
            
            # Verify the mock was called correctly
            mock_get_prefs.assert_called_once()

    def test_update_work_preference(self):
        """Test the POST /api/preferences/work endpoint."""
        # Mock the handle_update_work_preference function
        with mock.patch('src.first1k.handlers.preferences.handle_update_work_preference') as mock_update_pref:
            # Setup the mock response
            mock_update_pref.return_value = (200, "application/json", json.dumps({"status": "success"}))
            
            # Create test data
            preference = {
                "author_id": "auth001",
                "work_id": "work001",
                "preference_type": "favorites",
                "value": True
            }
            
            # Call the API endpoint
            response = self.client.post("/api/preferences/work", json=preference)
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            self.assertIn("Updated favorites preference", result["message"])
            
            # Verify the mock was called correctly with proper JSON string
            mock_update_pref.assert_called_once()
            # The first argument is query params (empty dict)
            self.assertEqual(mock_update_pref.call_args[0][0], {})
            # The second argument should be a JSON string with the expected format
            post_data = json.loads(mock_update_pref.call_args[0][1])
            self.assertEqual(post_data["work_id"], "work001")
            self.assertEqual(post_data["type"], "favorites")
            self.assertEqual(post_data["action"], "add")

    def test_update_work_preference_remove(self):
        """Test the POST /api/preferences/work endpoint for removing from a list."""
        # Mock the handle_update_work_preference function
        with mock.patch('src.first1k.handlers.preferences.handle_update_work_preference') as mock_update_pref:
            # Setup the mock response
            mock_update_pref.return_value = (200, "application/json", json.dumps({"status": "success"}))
            
            # Create test data for removal
            preference = {
                "author_id": "auth001",
                "work_id": "work001",
                "preference_type": "favorites",
                "value": False
            }
            
            # Call the API endpoint
            response = self.client.post("/api/preferences/work", json=preference)
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            
            # Verify the mock was called correctly with remove action
            mock_update_pref.assert_called_once()
            post_data = json.loads(mock_update_pref.call_args[0][1])
            self.assertEqual(post_data["action"], "remove")

    def test_update_work_preference_error(self):
        """Test the POST /api/preferences/work endpoint with an error response."""
        # Mock the handle_update_work_preference function
        with mock.patch('src.first1k.handlers.preferences.handle_update_work_preference') as mock_update_pref:
            # Setup the mock response with an error
            mock_update_pref.return_value = (400, "application/json", json.dumps({"error": "Invalid preference type"}))
            
            # Create test data
            preference = {
                "author_id": "auth001",
                "work_id": "work001",
                "preference_type": "invalid",
                "value": True
            }
            
            # Call the API endpoint
            response = self.client.post("/api/preferences/work", json=preference)
            
            # Verify the response
            self.assertEqual(response.status_code, 400)
            
            # Verify the mock was called correctly
            mock_update_pref.assert_called_once()

    def test_batch_update_preferences(self):
        """Test the POST /api/preferences/batch endpoint."""
        # Mock the handle_update_work_preference function
        with mock.patch('src.first1k.handlers.preferences.handle_update_work_preference') as mock_update_pref:
            # Setup the mock response
            mock_update_pref.return_value = (200, "application/json", json.dumps({"status": "success"}))
            
            # Create test data
            batch = {
                "preferences": [
                    {
                        "author_id": "auth001",
                        "work_id": "work001",
                        "preference_type": "favorites",
                        "value": True
                    },
                    {
                        "author_id": "auth002",
                        "work_id": "work002",
                        "preference_type": "archived",
                        "value": True
                    }
                ]
            }
            
            # Call the API endpoint
            response = self.client.post("/api/preferences/batch", json=batch)
            
            # Verify the response
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            self.assertIn("Successfully updated", result["message"])
            
            # Verify the mock was called correctly
            self.assertEqual(mock_update_pref.call_count, 2)

    def test_batch_update_preferences_error(self):
        """Test the POST /api/preferences/batch endpoint with an error."""
        # Mock the handle_update_work_preference function
        with mock.patch('src.first1k.handlers.preferences.handle_update_work_preference') as mock_update_pref:
            # First call succeeds, second call fails
            mock_update_pref.side_effect = [
                (200, "application/json", json.dumps({"status": "success"})),
                (400, "application/json", json.dumps({"error": "Invalid preference type"}))
            ]
            
            # Create test data
            batch = {
                "preferences": [
                    {
                        "author_id": "auth001",
                        "work_id": "work001",
                        "preference_type": "favorites",
                        "value": True
                    },
                    {
                        "author_id": "auth002",
                        "work_id": "work002",
                        "preference_type": "invalid",
                        "value": True
                    }
                ]
            }
            
            # Call the API endpoint
            response = self.client.post("/api/preferences/batch", json=batch)
            
            # Verify the response
            self.assertEqual(response.status_code, 400)
            
            # Verify the mock was called correctly
            self.assertEqual(mock_update_pref.call_count, 2)


if __name__ == '__main__':
    unittest.main() 