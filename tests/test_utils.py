#!/usr/bin/env python3
"""Tests for utility functions in the First1KGreek Browser."""

import unittest
import os
import json
from unittest import mock

from tests.test_base import BaseTest
import browse_texts_fixed


class UtilsTests(BaseTest):
    """Test cases for utility functions."""

    def test_get_content_type(self):
        """Test content type detection based on file extension."""
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Test different file extensions
        test_cases = [
            ('styles.css', 'text/css'),
            ('script.js', 'application/javascript'),
            ('image.png', 'image/png'),
            ('photo.jpg', 'image/jpeg'),
            ('photo.jpeg', 'image/jpeg'),
            ('animation.gif', 'image/gif'),
            ('icon.svg', 'image/svg+xml'),
            ('unknown.xyz', 'application/octet-stream'),
        ]
        
        for filename, expected_type in test_cases:
            content_type = browse_texts_fixed.CustomHTTPRequestHandler.get_content_type(
                handler, filename)
            self.assertEqual(content_type, expected_type, 
                            f"Failed for {filename}, got {content_type}")

    def test_get_author_works(self):
        """Test retrieving works for an author."""
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Setup test data directory structure
        author_id = 'auth001'
        author_dir = os.path.join(self.data_dir, author_id)
        os.makedirs(author_dir, exist_ok=True)
        
        # Create some test work directories
        work_dirs = ['work001', 'work002', 'work003', '__metadata__']
        for work_dir in work_dirs:
            os.makedirs(os.path.join(author_dir, work_dir), exist_ok=True)
        
        # Fix: Use direct string concatenation instead of recursive os.path.join calls
        def mock_join(*args):
            # If this is a call to join the data and author_id
            if len(args) >= 2 and args[0] == 'data' and args[1] == author_id:
                return self.data_dir + os.sep + author_id
            
            # For other calls, just join the arguments with the path separator
            return os.sep.join(args)
        
        # Test the get_author_works method
        with mock.patch('os.path.join', side_effect=mock_join), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.listdir', return_value=work_dirs):
            
            # Call the method
            works = browse_texts_fixed.CustomHTTPRequestHandler.get_author_works(
                handler, author_id)
            
            # Verify the result
            # Should include work001, work002, work003 but not __metadata__
            self.assertEqual(len(works), 3, "Should have 3 works")
            self.assertIn('work001', works)
            self.assertIn('work002', works)
            self.assertIn('work003', works)
            self.assertNotIn('__metadata__', works, "Should not include __metadata__")

    def test_get_work_content(self):
        """Test retrieving content for a work."""
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Setup test data
        author_id = 'auth001'
        work_id = 'work001'
        work_path = os.path.join(self.data_dir, author_id, work_id)
        os.makedirs(work_path, exist_ok=True)
        
        # Create test files
        with open(os.path.join(work_path, 'test.xml'), 'w') as f:
            f.write('<div type="textpart"><p>Test XML content</p></div>')
        
        with open(os.path.join(work_path, 'test.txt'), 'w') as f:
            f.write('Test plain text content')
        
        # Fix: Use direct string concatenation instead of recursive os.path.join calls
        def mock_join(*args):
            # If this is a call for the work path
            if len(args) >= 3 and args[0] == 'data' and args[1] == author_id and args[2] == work_id:
                return self.data_dir + os.sep + author_id + os.sep + work_id
            
            # For other calls, just join the arguments with the path separator
            return os.sep.join(args)
        
        # Test the get_work_content method
        with mock.patch('os.path.join', side_effect=mock_join), \
             mock.patch('os.listdir', return_value=['test.xml', 'test.txt']):
            
            # Call the method
            content = browse_texts_fixed.CustomHTTPRequestHandler.get_work_content(
                handler, author_id, work_id)
            
            # Verify the result
            self.assertIn('test.xml', content)
            self.assertIn('test.txt', content)
            self.assertIn('Test XML content', content)
            self.assertIn('Test plain text content', content)

    def test_get_work_content_errors(self):
        """Test error handling in get_work_content."""
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Case 1: No files in work directory
        with mock.patch('os.path.join', return_value=os.path.join(self.temp_dir, 'dummy')), \
             mock.patch('os.listdir', return_value=[]):
            
            content = browse_texts_fixed.CustomHTTPRequestHandler.get_work_content(
                handler, 'auth001', 'work001')
            
            self.assertIn("No content files found for this work", content)
        
        # Case 2: Exception when listing directory
        with mock.patch('os.path.join', return_value=os.path.join(self.temp_dir, 'dummy')), \
             mock.patch('os.listdir', side_effect=Exception("Test error")):
            
            content = browse_texts_fixed.CustomHTTPRequestHandler.get_work_content(
                handler, 'auth001', 'work001')
            
            self.assertIn("Error accessing work content: Test error", content)


if __name__ == '__main__':
    unittest.main() 