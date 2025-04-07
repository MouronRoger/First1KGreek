#!/usr/bin/env python3
"""Tests for HTTP request handler functionality."""

import unittest
import os
import json
import io
import urllib.parse
from unittest import mock

from tests.test_base import BaseTest
import browse_texts_fixed


class HTTPHandlerTests(BaseTest):
    """Test cases for the CustomHTTPRequestHandler class."""

    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        # Create a mock server for request handler
        self.mock_server = mock.MagicMock()
        self.mock_server.server_name = "localhost"
        self.mock_server.server_port = 8000
        
        # No need to patch args since it's no longer a module attribute
        # Just patch PORT and DEBUG directly
        self.port_patch = mock.patch.object(browse_texts_fixed, 'PORT', 8000)
        self.debug_patch = mock.patch.object(browse_texts_fixed, 'DEBUG', True)
        self.port_patch.start()
        self.debug_patch.start()
        self.patches.append(self.port_patch)
        self.patches.append(self.debug_patch)
        
        # Patch os functions to use our temp directory
        self.os_path_exists_patch = mock.patch('os.path.exists')
        self.mock_os_path_exists = self.os_path_exists_patch.start()
        self.mock_os_path_exists.return_value = True
        self.patches.append(self.os_path_exists_patch)
        
        # Patch open function for file operations
        self.open_patch = mock.patch('builtins.open', mock.mock_open(
            read_data=json.dumps(self.mock_authors_data)))
        self.mock_open = self.open_patch.start()
        self.patches.append(self.open_patch)

    def create_handler(self, path='/', method='GET', body=None):
        """Create a CustomHTTPRequestHandler instance for testing."""
        # Use direct mock instead of trying to create real handler 
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Add required attributes
        handler.path = path
        handler.command = method
        handler.requestline = f"{method} {path} HTTP/1.1"  # Add requestline attribute
        handler.client_address = ('127.0.0.1', 54321)
        handler.headers = {'Content-Length': '0'}
        
        # Setup an appropriate rfile that won't fail
        if body:
            handler.rfile = io.BytesIO(body.encode('utf-8'))
            handler.headers = {'Content-Length': str(len(body))}
        else:
            handler.rfile = io.BytesIO()
        
        # Set response methods
        handler.send_response = mock.MagicMock()
        handler.send_header = mock.MagicMock()
        handler.end_headers = mock.MagicMock()
        handler.send_error = mock.MagicMock()
        handler.wfile = mock.MagicMock()
        handler.send_html_response = mock.MagicMock()
        
        # Create a mock page_generator
        handler.page_generator = mock.MagicMock()
        handler.page_generator.get_home_page = mock.MagicMock(return_value="<html>Test Home Page</html>")
        handler.page_generator.get_authors_table_page = mock.MagicMock(return_value="<html>Test Authors Page</html>")
        handler.page_generator.get_works_page = mock.MagicMock(return_value="<html>Test Works Page</html>")
        handler.page_generator.get_view_page = mock.MagicMock(return_value="<html>Test View Page</html>")
        handler.page_generator.get_editors_page = mock.MagicMock(return_value="<html>Test Editors Page</html>")
        handler.page_generator.get_search_page = mock.MagicMock(return_value="<html>Test Search Page</html>")
        handler.page_generator.get_error_page = mock.MagicMock(return_value="<html>Test Error Page</html>")
        handler.page_generator.get_author_works = mock.MagicMock(return_value=['work001'])
        
        # Add mock do_GET and do_POST methods
        handler.do_GET = browse_texts_fixed.CustomHTTPRequestHandler.do_GET.__get__(handler)
        handler.do_POST = browse_texts_fixed.CustomHTTPRequestHandler.do_POST.__get__(handler)
        handler.handle_update_preference = browse_texts_fixed.CustomHTTPRequestHandler.handle_update_preference.__get__(handler)
        
        return handler

    def test_do_get_home_page(self):
        """Test GET request for home page."""
        # Create handler for the home page
        handler = self.create_handler('/')
        
        # Call the handler method
        handler.do_GET()
        
        # Verify send_html_response was called with the result from page_generator.get_home_page
        handler.page_generator.get_home_page.assert_called_once()
        handler.send_html_response.assert_called_once_with("<html>Test Home Page</html>")

    def test_do_get_authors_page(self):
        """Test GET request for authors page."""
        # Create handler for the authors page
        handler = self.create_handler('/authors')
        
        # Call the handler method
        handler.do_GET()
        
        # Verify the response
        handler.page_generator.get_authors_table_page.assert_called_once()
        handler.send_html_response.assert_called_once_with("<html>Test Authors Page</html>")

    def test_do_get_works_page(self):
        """Test GET request for works page."""
        # Create handler for the works page with query string
        query_string = "author_id=auth001"
        handler = self.create_handler(f'/works?{query_string}')
        
        # Call the handler method
        handler.do_GET()
        
        # Verify the response
        handler.page_generator.get_works_page.assert_called_once()
        handler.send_html_response.assert_called_once_with("<html>Test Works Page</html>")

    def test_do_get_view_page(self):
        """Test GET request for view page."""
        # Create handler for the view page with query string
        query_string = "author_id=auth001&work_id=work001"
        handler = self.create_handler(f'/view?{query_string}')
        
        # Call the handler method
        handler.do_GET()
        
        # Verify the response
        handler.page_generator.get_view_page.assert_called_once()
        handler.send_html_response.assert_called_once_with("<html>Test View Page</html>")

    def test_do_get_static_file(self):
        """Test GET request for static file."""
        # Create handler for a static file
        handler = self.create_handler('/static/css/styles.css')
        
        # Add serve_static_file method
        handler.serve_static_file = mock.MagicMock()
        
        # Call the handler method
        handler.do_GET()
        
        # Verify serve_static_file was called
        handler.serve_static_file.assert_called_once_with('/static/css/styles.css')

    def test_do_get_not_found(self):
        """Test GET request for non-existent path."""
        # Create handler for a non-existent path
        handler = self.create_handler('/nonexistent')
        
        # Call the handler method
        handler.do_GET()
        
        # Verify send_error was called with 404
        handler.send_error.assert_called_once_with(404, 'Not Found')

    def test_do_post_update_preference(self):
        """Test POST request for updating preferences."""
        # Create post data
        post_data = "author_id=auth001&pref_type=favorites&value=true"
        
        # Create handler for update preference
        handler = self.create_handler('/update_preference', 'POST', post_data)
        
        # Mock the parse_qs function to avoid file operations
        parsed_data = {
            'author_id': ['auth001'],
            'pref_type': ['favorites'],
            'value': ['true']
        }
        
        # Mock methods
        with mock.patch('urllib.parse.parse_qs', return_value=parsed_data), \
             mock.patch.object(handler, 'handle_update_preference') as mock_handle:
            
            # Call the handler method
            handler.do_POST()
            
            # Verify handle_update_preference was called with correct data
            mock_handle.assert_called_once()
            actual_post_data = mock_handle.call_args[0][0]
            self.assertEqual(actual_post_data, parsed_data)

    def test_do_post_update_century(self):
        """Test POST request for updating century."""
        # Create post data
        post_data = "author_id=auth001&century=3 BCE"
        
        # Create handler for update century
        handler = self.create_handler('/update_century', 'POST', post_data)
        
        # Mock the parse_qs function to avoid file operations
        parsed_data = {
            'author_id': ['auth001'],
            'century': ['3 BCE']
        }
        
        # Mock methods
        with mock.patch('urllib.parse.parse_qs', return_value=parsed_data), \
             mock.patch.object(handler, 'handle_update_century') as mock_handle:
            
            # Call the handler method
            handler.do_POST()
            
            # Verify handle_update_century was called with correct data
            mock_handle.assert_called_once()
            actual_post_data = mock_handle.call_args[0][0]
            self.assertEqual(actual_post_data, parsed_data)

    def test_handle_update_preference(self):
        """Test handling of preference updates."""
        # Create handler
        handler = self.create_handler()
        
        # Create post data
        post_data = {
            'author_id': ['auth001'],
            'pref_type': ['favorites'],
            'value': ['true']
        }
        
        # Mock file operations and user_prefs method
        mock_prefs = {'favorites': [], 'archived': [], 'deleted': []}
        handler.get_user_prefs = mock.MagicMock(return_value=mock_prefs)
        
        # Setup open to return preferences when reading and capture when writing
        with mock.patch('builtins.open', mock.mock_open()) as m, \
             mock.patch('json.dump') as mock_json_dump, \
             mock.patch.object(handler, 'send_response'), \
             mock.patch.object(handler, 'send_header'), \
             mock.patch.object(handler, 'end_headers'), \
             mock.patch.object(handler, 'wfile'):
            
            # Call the handler method
            handler.handle_update_preference(post_data)
            
            # Verify preference was updated and file was written
            self.assertIn('auth001', mock_prefs['favorites'])
            m.assert_any_call('user_preferences.json', 'w')
            mock_json_dump.assert_called_once_with(mock_prefs, m(), indent=2)


if __name__ == '__main__':
    unittest.main() 