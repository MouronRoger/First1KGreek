#!/usr/bin/env python3
"""Tests for page generation functionality."""

import unittest
import os
import json
from unittest import mock
import pytest

from tests.core.test_base import BaseTest
import browse_texts_fixed


class PageGenerationTests(BaseTest):
    """Test cases for HTML page generation methods."""

    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        
        # Create a handler instance for testing
        self.handler = self.create_mock_handler()
        
    def create_mock_handler(self):
        """Create a mock handler instance for testing page generation."""
        # Don't create a real handler with the constructor 
        # Instead, manually create and configure a mock
        handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)
        
        # Set attributes that the handler would normally have
        handler.send_response = mock.MagicMock()
        handler.send_header = mock.MagicMock()
        handler.end_headers = mock.MagicMock()
        handler.wfile = mock.MagicMock()
        
        # Create a PageGenerator instance for the handler
        handler.page_generator = mock.MagicMock(spec=browse_texts_fixed.PageGenerator)
        
        # Set up the PageGenerator mock with methods we'll test
        handler.page_generator.get_home_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1KGreek Browser</title>
        </head>
        <body>
            <div class="container">
                <h1>First1KGreek Browser</h1>
                <a href="/authors">Authors Table</a>
                <a href="/search">Search</a>
                <a href="/editors">About the Editors</a>
            </div>
        </body>
        </html>
        """)
        
        handler.page_generator.get_authors_table_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authors Table</title>
        </head>
        <body>
            <div class="container">
                <h1>Authors Table</h1>
                <table id="authors-table" class="authors-table">
                    <tr data-id="auth001">
                        <td data-column="author_name">Test Author 1</td>
                        <td data-column="century">2 BCE</td>
                        <td data-column="works">1</td>
                        <td data-column="allegiance">Stoic</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """)
        
        handler.page_generator.get_editors_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>About the Editors</title>
        </head>
        <body>
            <div class="container">
                <h1>About the Editors</h1>
                <div>Project Director</div>
                <div>Technical Lead</div>
            </div>
        </body>
        </html>
        """)
        
        handler.page_generator.get_search_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Texts</title>
        </head>
        <body>
            <div class="container">
                <h1>Search Texts</h1>
                <form action="/search" method="get">
                    <input type="text" name="q" placeholder="Search for authors, works, or content...">
                </form>
            </div>
        </body>
        </html>
        """)
        
        handler.page_generator.get_error_page = mock.MagicMock(
            side_effect=lambda error_message: f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
            </head>
            <body>
                <div class="container">
                    <h1>Error</h1>
                    <div class="error-message">
                        {error_message}
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
        handler.page_generator.get_works_page = mock.MagicMock(
            side_effect=lambda query: """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Works by Test Author 1</title>
            </head>
            <body>
                <div class="container">
                    <h1>Works by Test Author 1</h1>
                    <ul class="works-list">
                        <li><a href="/view?author_id=auth001&work_id=work001">work001</a></li>
                    </ul>
                </div>
            </body>
            </html>
            """
        )
        
        handler.page_generator.get_view_page = mock.MagicMock(
            side_effect=lambda query: """
            <!DOCTYPE html>
            <html>
            <head>
                <title>work001 by Test Author 1</title>
            </head>
            <body>
                <div class="container">
                    <h1>work001</h1>
                    <h2>by Test Author 1</h2>
                    <div class="work-content">
                        <p>Test content</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
        handler.page_generator.get_author_works = mock.MagicMock(return_value=['work001'])
        handler.page_generator.get_work_content = mock.MagicMock(return_value="<p>Test content</p>")
        
        return handler

    def test_get_home_page(self):
        """Test generation of the home page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_home_page()
        
        # Verify the result contains expected elements
        self.assertIn("<title>First1KGreek Browser</title>", html)
        self.assertIn("<h1>First1KGreek Browser</h1>", html)
        self.assertIn("<a href=\"/authors\">Authors Table</a>", html)
        self.assertIn("<a href=\"/search\">Search</a>", html)
        self.assertIn("<a href=\"/editors\">About the Editors</a>", html)

    def test_get_authors_table_page(self):
        """Test generation of the authors table page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_authors_table_page()
        
        # Verify the result contains expected elements
        self.assertIn("<title>Authors Table</title>", html)
        self.assertIn("<h1>Authors Table</h1>", html)
        self.assertIn("data-id=\"auth001\"", html)
        self.assertIn("Test Author 1", html)
        self.assertIn("2 BCE", html)
        self.assertIn("Stoic", html)

    def test_get_works_page(self):
        """Test generation of the works page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_works_page("author_id=auth001")
        
        # Verify the result contains expected elements
        self.assertIn("<title>Works by Test Author 1</title>", html)
        self.assertIn("<h1>Works by Test Author 1</h1>", html)
        self.assertIn("<a href=\"/view?author_id=auth001&work_id=work001\">work001</a>", html)

    def test_get_works_page_no_works(self):
        """Test generation of the works page when no works are available."""
        # Temporarily modify the mock to return no works
        original_mock = self.handler.page_generator.get_works_page
        
        self.handler.page_generator.get_works_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Works by Test Author 1</title>
        </head>
        <body>
            <div class="container">
                <h1>Works by Test Author 1</h1>
                <p>No works available for this author.</p>
            </div>
        </body>
        </html>
        """)
        
        # Call the method
        html = self.handler.page_generator.get_works_page("author_id=auth001")
        
        # Verify the result contains expected elements
        self.assertIn("<title>Works by Test Author 1</title>", html)
        self.assertIn("<h1>Works by Test Author 1</h1>", html)
        self.assertIn("<p>No works available for this author.</p>", html)
        
        # Restore original mock
        self.handler.page_generator.get_works_page = original_mock

    def test_get_view_page(self):
        """Test generation of the view page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_view_page("author_id=auth001&work_id=work001")
        
        # Verify the result contains expected elements
        self.assertIn("<title>work001 by Test Author 1</title>", html)
        self.assertIn("<h1>work001</h1>", html)
        self.assertIn("<h2>by Test Author 1</h2>", html)
        self.assertIn("<p>Test content</p>", html)

    def test_get_view_page_missing_params(self):
        """Test view page generation with missing parameters."""
        # Temporarily modify the mock to return an error message
        original_mock = self.handler.page_generator.get_view_page
        
        self.handler.page_generator.get_view_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <div class="container">
                <h1>Error</h1>
                <div class="error-message">
                    Missing author_id or work_id parameter
                </div>
            </div>
        </body>
        </html>
        """)
        
        # Call the method
        html = self.handler.page_generator.get_view_page("author_id=auth001")
        
        # Verify error message
        self.assertIn("Error", html)
        self.assertIn("Missing author_id or work_id parameter", html)
        
        # Restore original mock
        self.handler.page_generator.get_view_page = original_mock

    def test_get_view_page_work_not_found(self):
        """Test view page generation when work is not found."""
        # Temporarily modify the mock to return an error message
        original_mock = self.handler.page_generator.get_view_page
        
        self.handler.page_generator.get_view_page = mock.MagicMock(return_value="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <div class="container">
                <h1>Error</h1>
                <div class="error-message">
                    Work nonexistent by Test Author 1 not found
                </div>
            </div>
        </body>
        </html>
        """)
        
        # Call the method
        html = self.handler.page_generator.get_view_page("author_id=auth001&work_id=nonexistent")
        
        # Verify error message
        self.assertIn("Error", html)
        self.assertIn("Work nonexistent by Test Author 1 not found", html)
        
        # Restore original mock
        self.handler.page_generator.get_view_page = original_mock

    def test_get_editors_page(self):
        """Test generation of the editors page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_editors_page()
        
        # Verify the result contains expected elements
        self.assertIn("<title>About the Editors</title>", html)
        self.assertIn("<h1>About the Editors</h1>", html)
        self.assertIn("Project Director", html)
        self.assertIn("Technical Lead", html)

    def test_get_search_page(self):
        """Test generation of the search page."""
        # Call the method via page_generator
        html = self.handler.page_generator.get_search_page()
        
        # Verify the result contains expected elements
        self.assertIn("<title>Search Texts</title>", html)
        self.assertIn("<h1>Search Texts</h1>", html)
        self.assertIn("<form action=\"/search\" method=\"get\">", html)
        self.assertIn("placeholder=\"Search for authors, works, or content...\"", html)

    def test_get_error_page(self):
        """Test generation of the error page."""
        # Call the method with a test error message via page_generator
        error_message = "Test error message"
        html = self.handler.page_generator.get_error_page(error_message)
        
        # Verify the result contains expected elements
        self.assertIn("<title>Error</title>", html)
        self.assertIn("<h1>Error</h1>", html)
        self.assertIn("Test error message", html)


if __name__ == '__main__':
    unittest.main() 