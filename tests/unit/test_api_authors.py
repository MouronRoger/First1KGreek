"""Tests for the authors API endpoints in First1KGreek FastAPI implementation.

This module contains unit tests for the authors router functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.first1k.api import app
from src.first1k.models import Author, Work

# Create test client
client = TestClient(app)

# Sample test data
SAMPLE_AUTHORS = [
    {
        "id": "tlg0007",
        "name": "Plutarch",
        "century": 1,
        "type": "Biographer",
        "works_count": 3
    },
    {
        "id": "tlg0012",
        "name": "Homer",
        "century": -8,
        "type": "Poet",
        "works_count": 2
    }
]

SAMPLE_AUTHOR_WORKS = [
    {
        "id": "tlg0007.tlg136.perseus-grc2",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
        "is_favorite": False,
        "is_archived": False
    }
]


@patch("src.first1k.data.authors.async_get_filtered_authors")
def test_list_authors(mock_get_filtered_authors):
    """Test the list_authors endpoint."""
    # Set up mock
    mock_get_filtered_authors.return_value = SAMPLE_AUTHORS
    
    # Make request
    response = client.get("/api/authors/")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "tlg0007"
    assert data[0]["name"] == "Plutarch"
    assert data[1]["id"] == "tlg0012"
    assert data[1]["name"] == "Homer"
    assert data[1]["century"] == -8  # Negative for BCE
    
    # Check mock called correctly
    mock_get_filtered_authors.assert_called_once()


@patch("src.first1k.data.authors.async_get_filtered_authors")
def test_list_authors_with_filters(mock_get_filtered_authors):
    """Test the list_authors endpoint with filters."""
    # Set up mock to return filtered results
    mock_get_filtered_authors.return_value = [SAMPLE_AUTHORS[0]]  # Just Plutarch
    
    # Make request with filters
    response = client.get("/api/authors/?century=1&type=Biographer")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "tlg0007"
    
    # Check mock called with correct filters
    mock_get_filtered_authors.assert_called_once_with(
        century=1, 
        author_type="Biographer",
        skip=0,
        limit=100
    )


@patch("src.first1k.data.authors.async_get_author_by_id")
def test_get_author(mock_get_author_by_id):
    """Test the get_author endpoint."""
    # Set up mock
    mock_get_author_by_id.return_value = SAMPLE_AUTHORS[0]
    
    # Make request
    response = client.get("/api/authors/tlg0007")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tlg0007"
    assert data["name"] == "Plutarch"
    
    # Check mock called correctly
    mock_get_author_by_id.assert_called_once_with("tlg0007")


@patch("src.first1k.data.authors.async_get_author_by_id")
def test_get_author_not_found(mock_get_author_by_id):
    """Test the get_author endpoint with an invalid author ID."""
    # Set up mock
    mock_get_author_by_id.return_value = None
    
    # Make request
    response = client.get("/api/authors/invalid")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    
    # Check mock called correctly
    mock_get_author_by_id.assert_called_once_with("invalid")


@patch("src.first1k.data.authors.async_get_author_works")
@patch("src.first1k.data.authors.async_author_exists")
def test_get_author_works(mock_author_exists, mock_get_author_works):
    """Test the get_author_works endpoint."""
    # Set up mocks
    mock_author_exists.return_value = True
    mock_get_author_works.return_value = SAMPLE_AUTHOR_WORKS
    
    # Make request
    response = client.get("/api/authors/tlg0007/works")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "tlg0007.tlg136.perseus-grc2"
    assert data[0]["title"] == "De Stoicorum Repugnantiis"
    
    # Check mocks called correctly
    mock_author_exists.assert_called_once_with("tlg0007")
    mock_get_author_works.assert_called_once_with("tlg0007")


@patch("src.first1k.data.authors.async_author_exists")
def test_get_author_works_not_found(mock_author_exists):
    """Test the get_author_works endpoint with an invalid author ID."""
    # Set up mock
    mock_author_exists.return_value = False
    
    # Make request
    response = client.get("/api/authors/invalid/works")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    
    # Check mock called correctly
    mock_author_exists.assert_called_once_with("invalid")


@patch("src.first1k.data.authors.async_get_filtered_authors")
def test_list_authors_error_handling(mock_get_filtered_authors):
    """Test error handling in the list_authors endpoint."""
    # Set up mock to raise an exception
    mock_get_filtered_authors.side_effect = Exception("Test database error")
    
    # Make request
    response = client.get("/api/authors/")
    
    # Check response
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Test database error" in data["detail"] 