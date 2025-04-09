#!/usr/bin/env python3
"""Tests for server initialization and port handling functionality."""

import unittest
import socket
from unittest import mock
import pytest

from tests.core.test_base import BaseTest
import browse_texts_fixed

# Mark all tests in this module as unit tests for pytest
pytestmark = pytest.mark.unit


class ServerTests(BaseTest):
    """Test cases for server initialization and port handling."""

    def test_is_port_in_use(self):
        """Test port availability checking function."""
        # Mock socket.socket to control its behavior
        with mock.patch('socket.socket') as mock_socket:
            # Configure the mock to indicate port is in use
            mock_socket_instance = mock.MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            mock_socket_instance.connect_ex.return_value = 0  # 0 means success (port in use)

            # Test when port is in use
            result = browse_texts_fixed.is_port_in_use(8000)
            self.assertTrue(result)
            mock_socket_instance.connect_ex.assert_called_with(('localhost', 8000))

            # Reset and configure for port not in use
            mock_socket_instance.reset_mock()
            mock_socket_instance.connect_ex.return_value = 1  # Non-zero means failure (port not in use)

            # Test when port is not in use
            result = browse_texts_fixed.is_port_in_use(8000)
            self.assertFalse(result)
            mock_socket_instance.connect_ex.assert_called_with(('localhost', 8000))

    def test_find_available_port(self):
        """Test finding an available port."""
        # Patch is_port_in_use to control its behavior for testing
        with mock.patch('browse_texts_fixed.is_port_in_use') as mock_is_port_in_use:
            # First case: first port is available
            mock_is_port_in_use.return_value = False
            result = browse_texts_fixed.find_available_port(8000)
            self.assertEqual(result, 8000)
            mock_is_port_in_use.assert_called_once_with(8000)

            # Reset mock for next test
            mock_is_port_in_use.reset_mock()

            # Second case: first port is busy, second is available
            mock_is_port_in_use.side_effect = [True, False]
            result = browse_texts_fixed.find_available_port(8000)
            self.assertEqual(result, 8001)
            mock_is_port_in_use.assert_has_calls([
                mock.call(8000),
                mock.call(8001)
            ])

            # Reset mock for next test
            mock_is_port_in_use.reset_mock()

            # Third case: all ports are busy
            # Create a list with the right number of True values 
            mock_is_port_in_use.side_effect = [True] * 3  # Explicitly create 3 True values
            result = browse_texts_fixed.find_available_port(8000, max_attempts=3)
            self.assertEqual(result, 8000)  # Returns default when all ports are busy
            self.assertEqual(mock_is_port_in_use.call_count, 3)

    def test_server_initialization(self):
        """Test server initialization in the main method."""
        # Create a mock for TCPServer
        mock_server = mock.MagicMock()
        
        # Patch socket server and related functions
        with mock.patch('socketserver.TCPServer', return_value=mock_server), \
             mock.patch('browse_texts_fixed.is_port_in_use', return_value=False), \
             mock.patch('browse_texts_fixed.find_available_port', return_value=8000), \
             mock.patch('sys.exit'), \
             mock.patch('builtins.print'):
            
            # Patch the serve_forever method to raise KeyboardInterrupt
            serve_mock = mock.MagicMock(side_effect=KeyboardInterrupt())
            mock_server.serve_forever = serve_mock
            
            # Call the main function with our mocked server
            browse_texts_fixed.main()
            
            # Verify that server methods were called correctly
            serve_mock.assert_called_once()  # serve_forever should be called
            
            # Shutdown should be called after KeyboardInterrupt
            mock_server.shutdown.assert_called_once()

    def test_server_error_handling(self):
        """Test server error handling for address already in use."""
        # Create a mock for TCPServer that raises OSError
        mock_server = mock.MagicMock()
        
        # Patch socket server and related functions
        with mock.patch('socketserver.TCPServer', 
                         side_effect=OSError(48, 'Address already in use')), \
             mock.patch('browse_texts_fixed.is_port_in_use', return_value=True), \
             mock.patch('browse_texts_fixed.find_available_port', return_value=8001), \
             mock.patch('sys.exit'), \
             mock.patch('builtins.print'):
            
            # Run the main function
            # This should attempt to retry with a new port
            browse_texts_fixed.main()
            # We're primarily testing that it doesn't crash with the OSError


# Example of a pytest-style test function (can coexist with unittest tests)
@pytest.mark.unit
def test_is_port_in_use_pytest_style():
    """Test port availability checking using pytest style."""
    # Mock socket.socket to control its behavior
    with mock.patch('socket.socket') as mock_socket:
        # Configure the mock to indicate port is in use
        mock_socket_instance = mock.MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0  # 0 means success (port in use)

        # Test when port is in use
        result = browse_texts_fixed.is_port_in_use(8000)
        assert result is True
        mock_socket_instance.connect_ex.assert_called_with(('localhost', 8000))

        # Reset and configure for port not in use
        mock_socket_instance.reset_mock()
        mock_socket_instance.connect_ex.return_value = 1  # Non-zero means failure (port not in use)

        # Test when port is not in use
        result = browse_texts_fixed.is_port_in_use(8000)
        assert result is False
        mock_socket_instance.connect_ex.assert_called_with(('localhost', 8000))


if __name__ == '__main__':
    unittest.main() 