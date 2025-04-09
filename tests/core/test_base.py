#!/usr/bin/env python3
"""Base test utilities and fixtures for First1KGreek Browser tests."""

import unittest
import tempfile
import shutil
import os
import json
import io
import sys
from unittest import mock
from contextlib import contextmanager

# Add parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the main module under test
import browse_texts_fixed


class BaseTest(unittest.TestCase):
    """Base test class with common utilities and setup for all tests."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a temporary directory for static files
        self.static_dir = os.path.join(self.temp_dir, 'static')
        os.makedirs(os.path.join(self.static_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'js'), exist_ok=True)
        
        # Setup mock author data
        self.mock_authors_data = {
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
        
        # Setup mock user preferences
        self.mock_user_prefs = {
            'favorites': ['auth001'],
            'archived': [],
            'deleted': []
        }
        
        # Create the test data and preferences files
        self._create_test_files()
        
        # Setup patches
        self.patches = []
        self._setup_patches()

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
        
        # Remove all patches
        for patch in self.patches:
            patch.stop()

    def _create_test_files(self):
        """Create test files needed for tests."""
        # Create authors data file
        with open(os.path.join(self.temp_dir, 'authors_data.json'), 'w') as f:
            json.dump(self.mock_authors_data, f)
        
        # Create user preferences file
        with open(os.path.join(self.temp_dir, 'user_preferences.json'), 'w') as f:
            json.dump(self.mock_user_prefs, f)
        
        # Create test work directory and files
        author_dir = os.path.join(self.data_dir, 'auth001')
        os.makedirs(author_dir, exist_ok=True)
        
        work_dir = os.path.join(author_dir, 'work001')
        os.makedirs(work_dir, exist_ok=True)
        
        # Create a test XML file
        with open(os.path.join(work_dir, 'test.xml'), 'w') as f:
            f.write('<div type="textpart"><p>Test Greek text content.</p></div>')
        
        # Create a test CSS file
        with open(os.path.join(self.static_dir, 'css', 'styles.css'), 'w') as f:
            f.write('body { background-color: #2a2a2a; color: #f2f2f2; }')
        
        # Create a test JS file
        with open(os.path.join(self.static_dir, 'js', 'authors_table.js'), 'w') as f:
            f.write('console.log("Test JS");')

    def _setup_patches(self):
        """Setup common patches for the tests."""
        # Patch the authors data
        authors_patch = mock.patch.object(
            browse_texts_fixed, 'AUTHORS_DATA', self.mock_authors_data)
        self.patches.append(authors_patch)
        authors_patch.start()

    @contextmanager
    def captured_output(self):
        """Context manager to capture stdout and stderr for testing."""
        new_out, new_err = io.StringIO(), io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def create_mock_request(self, method='GET', path='/', headers=None, body=None):
        """Create a mock request object for testing handlers."""
        mock_request = mock.MagicMock()
        mock_request.command = method
        mock_request.path = path
        mock_request.headers = headers or {}
        
        if body:
            mock_request.rfile = io.BytesIO(body.encode('utf-8'))
        else:
            mock_request.rfile = io.BytesIO()
        
        mock_request.wfile = io.BytesIO()
        mock_request.send_response = mock.MagicMock()
        mock_request.send_header = mock.MagicMock()
        mock_request.end_headers = mock.MagicMock()
        mock_request.wfile.write = mock.MagicMock()
        
        return mock_request


if __name__ == '__main__':
    unittest.main() 