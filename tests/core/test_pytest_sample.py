#!/usr/bin/env python3
"""Example pytest-style tests for First1KGreek Browser."""

import os
import sys
import pytest
from unittest import mock

# Add parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main module under test
import browse_texts_fixed

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


# Example of simple pytest fixture
@pytest.fixture
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


def test_find_available_port_pytest_style():
    """Test finding an available port using pytest style."""
    # Patch is_port_in_use to control its behavior for testing
    with mock.patch('browse_texts_fixed.is_port_in_use') as mock_is_port_in_use:
        # First case: first port is available
        mock_is_port_in_use.return_value = False
        result = browse_texts_fixed.find_available_port(8000)
        assert result == 8000
        mock_is_port_in_use.assert_called_once_with(8000)

        # Reset mock for next test
        mock_is_port_in_use.reset_mock()

        # Second case: first port is busy, second is available
        mock_is_port_in_use.side_effect = [True, False]
        result = browse_texts_fixed.find_available_port(8000)
        assert result == 8001
        assert mock_is_port_in_use.call_count == 2


# Example of using a fixture in a test
def test_author_processing(mock_authors_data):
    """Test author data processing with a fixture."""
    # Mock the global AUTHORS_DATA with our fixture data
    with mock.patch.object(browse_texts_fixed, 'AUTHORS_DATA', mock_authors_data):
        # Test that we can find an author by ID
        auth_names = list(browse_texts_fixed.AUTHORS_DATA.keys())
        assert 'auth001' in auth_names
        assert browse_texts_fixed.AUTHORS_DATA['auth001']['name'] == 'Test Author 1'


# Example of parameterized test
@pytest.mark.parametrize("test_port,expected_result", [
    (8000, True),  # Port is in use
    (8001, False),  # Port is not in use
])
def test_is_port_in_use_parameterized(test_port, expected_result):
    """Test port checking with parameterized inputs."""
    with mock.patch('socket.socket') as mock_socket:
        mock_socket_instance = mock.MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # Set the return value based on the expected result
        # 0 means success (port in use), non-zero means failure (port not in use)
        mock_socket_instance.connect_ex.return_value = 0 if expected_result else 1
        
        result = browse_texts_fixed.is_port_in_use(test_port)
        assert result is expected_result
        mock_socket_instance.connect_ex.assert_called_with(('localhost', test_port)) 