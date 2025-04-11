"""Tests for the FastAPI application endpoints."""

import json
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.first1k.api import app

client = TestClient(app)

# Sample test data
SAMPLE_AUTHOR = {
    "id": "tlg0007",
    "name": "Plutarch",
    "century": 1,
    "type": "Biographer",
    "works_count": 3,
    "is_favorite": False,
    "is_archived": False
}

SAMPLE_WORKS = [
    {
        "id": "tlg0007.tlg136.perseus-grc2",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
        "is_favorite": False,
        "is_archived": False
    }
]

SAMPLE_PREFERENCES = {
    "favorites": ["tlg0007.tlg136.perseus-grc2"],
    "archived": ["tlg0012.tlg001.perseus-grc2"]
}

# Tests for health endpoint
def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data

# Tests for info endpoint
def test_info():
    """Test the info endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "features" in data
    assert "last_updated" in data
    assert "client" in data
    assert "host" in data["client"]

# Tests for authors endpoints
@patch("src.first1k.handlers.api.get_authors_list")
def test_get_authors(mock_get_authors_list):
    """Test the get_authors endpoint."""
    # Set up mock
    mock_get_authors_list.return_value = [SAMPLE_AUTHOR]

    # Make request
    response = client.get("/api/authors")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == SAMPLE_AUTHOR["id"]
    
    # Check mock called correctly
    mock_get_authors_list.assert_called_once()

@patch("src.first1k.handlers.api.get_author_details")
def test_get_author(mock_get_author_details):
    """Test the get_author endpoint."""
    # Set up mock
    mock_get_author_details.return_value = SAMPLE_AUTHOR

    # Make request
    response = client.get(f"/api/authors/{SAMPLE_AUTHOR['id']}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == SAMPLE_AUTHOR["id"]
    assert data["name"] == SAMPLE_AUTHOR["name"]
    
    # Check mock called correctly
    mock_get_author_details.assert_called_once_with(SAMPLE_AUTHOR["id"])

@patch("src.first1k.handlers.api.get_author_details")
def test_get_author_not_found(mock_get_author_details):
    """Test the get_author endpoint with an invalid author ID."""
    # Set up mock
    mock_get_author_details.return_value = None

    # Make request
    response = client.get("/api/authors/invalid")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

@patch("src.first1k.handlers.api.get_author_works_for_api")
@patch("src.first1k.handlers.api.author_exists")
def test_get_author_works(mock_author_exists, mock_get_author_works):
    """Test the get_author_works endpoint."""
    # Set up mocks
    mock_get_author_works.return_value = SAMPLE_WORKS
    mock_author_exists.return_value = True

    # Make request
    response = client.get(f"/api/authors/{SAMPLE_AUTHOR['id']}/works")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == SAMPLE_WORKS[0]["id"]
    
    # Check mocks called correctly
    mock_get_author_works.assert_called_once_with(SAMPLE_AUTHOR["id"])

@patch("src.first1k.handlers.api.get_author_works_for_api")
@patch("src.first1k.handlers.api.author_exists")
def test_get_author_works_not_found(mock_author_exists, mock_get_author_works):
    """Test the get_author_works endpoint with an invalid author ID."""
    # Set up mocks
    mock_get_author_works.return_value = []
    mock_author_exists.return_value = False

    # Make request
    response = client.get("/api/authors/invalid/works")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

# Tests for preferences endpoints
@patch("src.first1k.handlers.api.get_user_preferences")
def test_get_preferences(mock_get_preferences):
    """Test the get_preferences endpoint."""
    # Set up mock
    mock_get_preferences.return_value = SAMPLE_PREFERENCES

    # Make request
    response = client.get("/api/preferences")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "favorites" in data
    assert "archived" in data
    assert data["favorites"] == SAMPLE_PREFERENCES["favorites"]
    
    # Check mock called correctly
    mock_get_preferences.assert_called_once()

@patch("src.first1k.handlers.api.update_work_preference")
def test_update_work_preference(mock_update_work_preference):
    """Test the update_work_preference endpoint."""
    # Set up mock
    mock_update_work_preference.return_value = {"status": "success"}

    # Request data
    preference_data = {
        "work_id": "tlg0007.tlg136.perseus-grc2",
        "type": "favorite",
        "action": "add"
    }

    # Make request
    response = client.post(
        "/api/preferences/work",
        json=preference_data
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check mock called correctly
    mock_update_work_preference.assert_called_once()
    assert mock_update_work_preference.call_args[0][0] == preference_data

@patch("src.first1k.handlers.api.update_bulk_preferences")
def test_update_batch_preferences(mock_update_bulk_preferences):
    """Test the update_batch_preferences endpoint."""
    # Set up mock
    mock_update_bulk_preferences.return_value = {"status": "success"}

    # Make request
    response = client.post(
        "/api/preferences/batch",
        json=SAMPLE_PREFERENCES
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check mock called correctly
    mock_update_bulk_preferences.assert_called_once()
    # Convert the call arg to dict for comparison (it's a pydantic model)
    call_arg = mock_update_bulk_preferences.call_args[0][0]
    assert call_arg["favorites"] == SAMPLE_PREFERENCES["favorites"]
    assert call_arg["archived"] == SAMPLE_PREFERENCES["archived"]

# Tests for search endpoint
@patch("src.first1k.handlers.api.search_corpus")
def test_search_texts(mock_search_corpus):
    """Test the search_texts endpoint."""
    # Sample search results
    sample_results = [
        {
            "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
            "author": "Plutarch",
            "title": "De Stoicorum Repugnantiis",
            "editor": "Unknown",
            "context": "Sample search context",
            "occurrence_count": 5
        }
    ]
    
    # Set up mock
    mock_search_corpus.return_value = sample_results

    # Make request
    response = client.get("/api/search?q=stoic")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["total"] == 1
    assert data["query"] == "stoic"
    assert len(data["results"]) == 1
    assert data["results"][0]["file_path"] == sample_results[0]["file_path"]
    
    # Check mock called correctly
    mock_search_corpus.assert_called_once_with("stoic")

# Tests for view endpoints
@patch("src.first1k.handlers.api.get_xml_content")
def test_view_xml(mock_get_xml_content):
    """Test the view_xml endpoint."""
    # Sample XML content
    sample_content = {
        "content": "<xml>Test content</xml>",
        "author": "Plutarch",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    }
    
    # Set up mock
    mock_get_xml_content.return_value = sample_content

    # Make request
    file_path = "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    response = client.get(f"/api/view/xml?path={file_path}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["content"] == sample_content["content"]
    assert data["author"] == sample_content["author"]
    
    # Check mock called correctly
    mock_get_xml_content.assert_called_once_with(file_path)

@patch("src.first1k.handlers.api.get_xml_content")
def test_view_xml_not_found(mock_get_xml_content):
    """Test the view_xml endpoint with an invalid file path."""
    # Set up mock
    mock_get_xml_content.return_value = None

    # Make request
    response = client.get("/api/view/xml?path=invalid/path.xml")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

@patch("src.first1k.handlers.api.get_reader_content")
def test_view_reader(mock_get_reader_content):
    """Test the view_reader endpoint."""
    # Sample reader content
    sample_content = {
        "content": "Test content without XML tags",
        "author": "Plutarch",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    }
    
    # Set up mock
    mock_get_reader_content.return_value = sample_content

    # Make request
    file_path = "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    response = client.get(f"/api/view/reader?path={file_path}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["content"] == sample_content["content"]
    assert data["author"] == sample_content["author"]
    
    # Check mock called correctly
    mock_get_reader_content.assert_called_once_with(file_path)

@patch("src.first1k.handlers.api.get_reader_content")
def test_view_reader_not_found(mock_get_reader_content):
    """Test the view_reader endpoint with an invalid file path."""
    # Set up mock
    mock_get_reader_content.return_value = None

    # Make request
    response = client.get("/api/view/reader?path=invalid/path.xml")
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
