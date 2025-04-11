"""Tests for the preferences API endpoints in First1KGreek FastAPI implementation.

This module contains unit tests for the preferences router functionality.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.first1k.api import app
from src.first1k.models import UserPreference, BatchPreferences, APIResponse

# Create test client
client = TestClient(app)

# Sample test data
SAMPLE_PREFERENCES = {
    "favorites": ["tlg0007.tlg136.perseus-grc2", "tlg0012.tlg001.perseus-grc2"],
    "archived": ["tlg0059.tlg030.perseus-grc2"]
}

SAMPLE_WORK_PREFERENCE = {
    "author_id": "tlg0007",
    "work_id": "tlg0007.tlg136.perseus-grc2",
    "preference_type": "favorite",
    "value": True
}


@patch("src.first1k.handlers.preferences.get_user_preferences")
def test_get_preferences(mock_get_user_preferences):
    """Test the get_preferences endpoint."""
    # Set up mock
    mock_get_user_preferences.return_value = SAMPLE_PREFERENCES

    # Make request
    response = client.get("/api/preferences/")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "favorites" in data
    assert "archived" in data
    assert len(data["favorites"]) == 2
    assert len(data["archived"]) == 1

    # Check mock called correctly
    mock_get_user_preferences.assert_called_once()


@patch("src.first1k.handlers.preferences.update_user_preferences")
@patch("src.first1k.handlers.preferences.get_user_preferences")
def test_update_work_preference(mock_get_user_preferences, mock_update_user_preferences):
    """Test the update_work_preference endpoint."""
    # Set up mocks
    mock_get_user_preferences.return_value = SAMPLE_PREFERENCES.copy()
    mock_update_user_preferences.return_value = None

    # Make request
    response = client.post(
        "/api/preferences/work",
        json=SAMPLE_WORK_PREFERENCE
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data

    # Check mocks called correctly
    mock_get_user_preferences.assert_called_once()
    mock_update_user_preferences.assert_called_once()


@patch("src.first1k.handlers.preferences.get_user_preferences")
def test_get_preferences_error(mock_get_user_preferences):
    """Test the get_preferences endpoint with an error."""
    # Set up mock to raise an exception
    mock_get_user_preferences.side_effect = Exception("Test error")

    # Make request
    response = client.get("/api/preferences/")

    # Check response
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Test error" in data["detail"]


@patch("src.first1k.handlers.preferences.update_user_preferences")
@patch("src.first1k.handlers.preferences.get_user_preferences")
def test_update_work_preference_error(mock_get_user_preferences, mock_update_user_preferences):
    """Test the update_work_preference endpoint with an error."""
    # Set up mocks
    mock_get_user_preferences.return_value = SAMPLE_PREFERENCES.copy()
    mock_update_user_preferences.side_effect = Exception("Test update error")

    # Make request
    response = client.post(
        "/api/preferences/work",
        json=SAMPLE_WORK_PREFERENCE
    )

    # Check response
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Test update error" in data["detail"]


@pytest.mark.xfail(reason="Batch endpoint not implemented yet")
@patch("src.first1k.handlers.preferences.update_user_preferences")
@patch("src.first1k.handlers.preferences.get_user_preferences")
def test_batch_update_preferences(mock_get_user_preferences, mock_update_user_preferences):
    """Test batch updating of preferences."""
    # Setup
    mock_get_user_preferences.return_value = SAMPLE_PREFERENCES.copy()

    # Create batch preference data
    batch_data = {
        "preferences": [
            {
                "author_id": "tlg0007",
                "work_id": "tlg0007.tlg136.perseus-grc2",
                "preference_type": "favorite",
                "value": False
            },
            {
                "author_id": "tlg0059",
                "work_id": "tlg0059.tlg030.perseus-grc2",
                "preference_type": "archived",
                "value": False
            }
        ]
    }

    # Make request
    response = client.post(
        "/api/preferences/batch",
        json=batch_data
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify the correct calls were made to update preferences
    assert mock_get_user_preferences.call_count == 2  # Once per preference
    assert mock_update_user_preferences.call_count == 2  # Once per preference 