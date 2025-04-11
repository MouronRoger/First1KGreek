#!/usr/bin/env python3
"""Configuration and fixtures for pytest."""

import os
import sys
import pytest
import tempfile
import shutil
import json
from unittest import mock
from unittest.mock import patch

# Add parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main module under test
import browse_texts_fixed

# Try to import FastAPI modules if available
try:
    from fastapi.testclient import TestClient
    from src.first1k.api import app as fastapi_app
    from src.first1k.models import Author, Work, UserPreference
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# FastAPI-specific fixtures
if FASTAPI_AVAILABLE:
    @pytest.fixture
    def api_client():
        """Return a TestClient for the FastAPI app."""
        return TestClient(fastapi_app)
    
    @pytest.fixture
    def temp_preferences_file():
        """Create a temporary preferences file for testing."""
        # Create a temp file
        fd, path = tempfile.mkstemp()
        
        # Write initial preferences
        sample_prefs = {
            "favorites": ["tlg0007.tlg136.perseus-grc2"],
            "archived": ["tlg0059.tlg030.perseus-grc2"],
            "deleted": []
        }
        with os.fdopen(fd, 'w') as f:
            json.dump(sample_prefs, f)
        
        # Override the preferences file path
        with patch("src.first1k.handlers.preferences.USER_PREFS_FILE", path):
            yield path
        
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def mock_author_models():
        """Return mock author models for testing."""
        return [
            Author(id="auth001", name="Test Author 1", century=-5, type="Historian"),
            Author(id="auth002", name="Test Author 2", century=1, type="Poet")
        ]

    @pytest.fixture
    def mock_work_models():
        """Return mock work models for testing."""
        return [
            Work(
                id="work001",
                title="Test Work 1",
                author_id="auth001",
                language="grc",
                file_path="data/auth001/work001/test.xml",
                is_favorite=True,
                is_archived=False,
                files=[{"name": "test.xml", "type": "xml", "path": "data/auth001/work001/test.xml"}]
            ),
            Work(
                id="work002",
                title="Test Work 2",
                author_id="auth002",
                language="eng",
                file_path="data/auth002/work002/test.xml",
                is_favorite=False,
                is_archived=True,
                files=[{"name": "test.xml", "type": "xml", "path": "data/auth002/work002/test.xml"}]
            )
        ]

    @pytest.fixture
    def async_mock():
        """Create a mock that works with async functions.
        
        This fixture helps create mocks that can be used with async functions
        by automatically wrapping the mock's return_value in a coroutine.
        """
        def _create_async_mock(return_value=None):
            mock_obj = mock.MagicMock()
            
            async def _async_magic():
                return return_value
                
            mock_obj.__call__.return_value = _async_magic()
            return mock_obj
            
        return _create_async_mock


@pytest.fixture(scope="session")
def mock_authors_data():
    """Return mock authors data for testing."""
    return {
        'auth001': {
            'name': 'Test Author 1', 
            'century': '2 BCE', 
            'allegiance': 'Stoic'
        },
        'auth002': {
            'name': 'Test Author 2', 
            'century': '1 CE', 
            'allegiance': 'Epicurean'
        }
    }


@pytest.fixture(scope="session")
def mock_user_preferences():
    """Return mock user preferences for testing."""
    return {
        'favorites': ['auth001'],
        'archived': [],
        'deleted': []
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)


@pytest.fixture
def setup_test_data(temp_dir, mock_authors_data, mock_user_preferences):
    """Set up test data in temporary directory."""
    # Create data directory
    data_dir = os.path.join(temp_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create static directories
    static_dir = os.path.join(temp_dir, 'static')
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
    
    # Create authors data file
    with open(os.path.join(temp_dir, 'authors_data.json'), 'w') as f:
        json.dump(mock_authors_data, f)
    
    # Create user preferences file
    with open(os.path.join(temp_dir, 'user_preferences.json'), 'w') as f:
        json.dump(mock_user_preferences, f)
    
    # Create author directory and works
    author_dir = os.path.join(data_dir, 'auth001')
    os.makedirs(author_dir, exist_ok=True)
    
    work_dir = os.path.join(author_dir, 'work001')
    os.makedirs(work_dir, exist_ok=True)
    
    # Create a test XML file
    with open(os.path.join(work_dir, 'test.xml'), 'w') as f:
        f.write('<div type="textpart"><p>Test Greek text content.</p></div>')
    
    # Create a test CSS file
    with open(os.path.join(static_dir, 'css', 'styles.css'), 'w') as f:
        f.write('body { background-color: #2a2a2a; color: #f2f2f2; }')
    
    # Create a test JS file
    with open(os.path.join(static_dir, 'js', 'authors_table.js'), 'w') as f:
        f.write('console.log("Test JS");')
    
    return {
        'temp_dir': temp_dir,
        'data_dir': data_dir,
        'static_dir': static_dir,
        'author_dir': author_dir,
        'work_dir': work_dir
    }


@pytest.fixture
def mock_handler():
    """Create a mock HTTP handler for testing."""
    # Create a mock server
    mock_server = mock.MagicMock()
    mock_server.server_name = "localhost"
    mock_server.server_port = 8000
    
    # Create a mock request
    mock_request = mock.MagicMock()
    mock_request.makefile.return_value = mock.MagicMock()
    client_address = ('127.0.0.1', 54321)
    
    # Create the handler
    handler = browse_texts_fixed.CustomHTTPRequestHandler(
        mock_request, client_address, mock_server)
    
    return handler 