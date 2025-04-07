#!/usr/bin/env python3
"""First1KGreek Browser - Fixed Version.

A Python-based browser for viewing and managing ancient Greek texts.
Version: 1.2.0 (with cache-busting and dark theme)
Last updated: 2025-03-07
"""

import argparse
import http.server
import json
import logging
import os
import re
import signal
import socket
import socketserver
import sys
import threading
import time
import traceback
import urllib.parse
import xml.etree.ElementTree as ET
from html import escape
from urllib.error import HTTPError, URLError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("server.log", mode="w")],
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="First1KGreek Browser")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


# Global variable to store server instance
server_instance = None

# Constants
args = parse_args()
PORT = args.port
HOST = "localhost"
SHUTDOWN_PATH = "/shutdown"
DEBUG = args.debug

# Load author data
try:
    with open("authors_data.json", "r", encoding="utf-8") as f:
        AUTHORS_DATA = json.load(f)
    logger.info(f"Loaded author data with {len(AUTHORS_DATA)} entries")
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Error loading author data: {e}")
    AUTHORS_DATA = {}

# Print version info when starting
logger.info("Starting First1KGreek Browser - Fixed Version 1.2.0")
logger.info("With dark theme and improved editor detection")

# Reader mode stylesheet
READER_STYLESHEET = """
:root {
    --background: #2a2a2a;
    --foreground: #f2f2f2;
    --surface: #333;
    --primary: #4299e1;
}

body {
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif;
    margin: 0;
    padding: 0;
    line-height: 1.8;
    background-color: var(--background);
    color: var(--foreground);
}
h1, h2, h3 {
    color: #fff;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--surface);
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    min-height: 100vh;
}
"""

# Main stylesheet
MAIN_STYLESHEET = """
:root {
    --background: #1a1a1a;
    --foreground: #ffffff;
    --primary: #4299e1;
    --accent: #805ad5;
    --success: #48bb78;
    --warning: #ed8936;
    --error: #f56565;
    --surface: #2d2d2d;
    --surface-light: #333;
    --surface-dark: #222;
    --text-light: #f2f2f2;
    --text-dim: #a0aec0;
    --border: #444;
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    background-color: var(--background);
    color: var(--foreground);
}
h1, h2, h3 {
    color: var(--primary);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--surface);
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    min-height: 100vh;
}
"""

# Authors table stylesheet
AUTHORS_TABLE_STYLESHEET = """
.authors-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: var(--surface-light);
    border-radius: 5px;
    overflow: hidden;
    table-layout: fixed;
}

.authors-table th {
    padding: 12px 15px;
    text-align: left;
    background-color: #1a365d;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

.authors-table th:hover {
    background-color: #2a4365;
}

.authors-table td {
    padding: 10px 15px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Fixed column widths */
.authors-table th:nth-child(1),
.authors-table td:nth-child(1) {
    width: 20ch;
}

.authors-table th:nth-child(2),
.authors-table td:nth-child(2) {
    width: 12ch;
}

.authors-table th:nth-child(3),
.authors-table td:nth-child(3) {
    width: 8ch;
}

.authors-table th:nth-child(4),
.authors-table td:nth-child(4) {
    width: 15ch;
}

.authors-table th:nth-child(5),
.authors-table td:nth-child(5) {
    width: auto;
}

.authors-table tr:hover {
    background-color: var(--surface-dark);
}

.action-btn {
    padding: 5px 10px;
    margin-right: 5px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    color: white;
}

.favorite-btn {
    background-color: var(--warning);
}

.favorite-btn:hover {
    background-color: var(--warning);
    opacity: 0.9;
}

.favorite-btn.active {
    background-color: var(--warning);
}

.archive-btn {
    background-color: var(--success);
}

.archive-btn:hover {
    background-color: var(--success);
    opacity: 0.9;
}

.archive-btn.active {
    background-color: var(--success);
}

.delete-btn {
    background-color: var(--error);
}

.delete-btn:hover {
    background-color: var(--error);
    opacity: 0.9;
}

.delete-btn.active {
    background-color: var(--error);
}

.edit-btn {
    background-color: var(--primary);
}

.edit-btn:hover {
    background-color: var(--primary);
    opacity: 0.9;
}

.status-filters, .century-filters {
    margin: 10px 0;
}

.status-filters button, .century-filters button {
    padding: 8px 15px;
    margin-right: 10px;
    background-color: var(--surface-dark);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.status-filters button:hover, .century-filters button:hover {
    background-color: var(--surface);
}

.status-filters button.active, .century-filters button.active {
    background-color: var(--primary);
}

.pagination {
    margin: 20px 0;
    text-align: center;
}

.pagination button {
    padding: 8px 15px;
    margin: 0 5px;
    background-color: var(--surface-dark);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.pagination button:hover {
    background-color: var(--surface);
}

.pagination button.active {
    background-color: var(--primary);
}

.search-filter {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--surface-dark);
    border-radius: 5px;
}

.search-filter input[type="text"] {
    padding: 10px;
    width: 70%;
    border: 1px solid var(--border);
    background-color: var(--surface-light);
    color: white;
    border-radius: 4px;
}

.search-filter button {
    padding: 10px 20px;
    background-color: var(--primary);
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    margin-left: 10px;
}

.search-filter button:hover {
    background-color: var(--primary);
    opacity: 0.9;
}

.favorites-star {
    color: var(--warning);
    font-size: 1.2em;
    margin-right: 5px;
}

.archived-icon {
    color: var(--success);
    font-size: 1.2em;
    margin-right: 5px;
}

/* Century edit modal */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: var(--surface);
    margin: 15% auto;
    padding: 20px;
    border-radius: 5px;
    width: 50%;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.modal-header h2 {
    margin: 0;
    color: var(--primary);
}

.close-modal {
    color: #aaa;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close-modal:hover {
    color: #fff;
}

.modal-body {
    margin-bottom: 20px;
}

.modal-body label {
    display: block;
    margin-bottom: 5px;
    color: var(--text-light);
}

.modal-body input {
    width: 100%;
    padding: 8px;
    margin-bottom: 15px;
    border: 1px solid var(--border);
    background-color: var(--surface-light);
    color: white;
    border-radius: 4px;
}

.modal-footer {
    text-align: right;
}

.modal-footer button {
    padding: 8px 16px;
    margin-left: 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.save-btn {
    background-color: var(--primary);
    color: white;
}

.save-btn:hover {
    background-color: var(--primary);
    opacity: 0.9;
}

.cancel-btn {
    background-color: #718096;
    color: white;
}

.cancel-btn:hover {
    background-color: #4a5568;
}

/* Works tree styles */
.works-container {
    padding: 0 !important;
    background-color: var(--surface-dark);
}

.works-tree {
    padding: 15px;
    border-top: 1px solid var(--border);
}

.loading-indicator {
    color: var(--text-dim);
    font-style: italic;
    text-align: center;
    padding: 20px;
}

.work-item {
    padding: 10px;
    margin-bottom: 5px;
    border-radius: 4px;
    background-color: var(--surface-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.work-item:hover {
    background-color: var(--surface);
}

.work-info {
    flex-grow: 1;
}

.work-title {
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 5px;
}

.work-meta {
    font-size: 0.9em;
    color: var(--text-dim);
}

.work-actions {
    display: flex;
    gap: 5px;
}

.toggle-works-btn {
    background-color: var(--accent);
}

.toggle-works-btn:hover {
    background-color: var(--accent);
    opacity: 0.9;
}

.work-editor {
    font-size: 0.9em;
    color: var(--text-dim);
    font-style: italic;
    margin-top: 3px;
}

.error {
    color: var(--error);
    background-color: rgba(252, 129, 129, 0.1);
    padding: 10px;
    border-radius: 4px;
    margin: 10px 0;
    text-align: center;
}

.retry-btn {
    background-color: var(--primary);
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    margin-top: 10px;
    cursor: pointer;
}

.retry-btn:hover {
    background-color: var(--primary);
    opacity: 0.9;
}
"""


def is_port_in_use(port):
    """Check if a port is in use.
    
    Args:
        port (int): Port number to check
        
    Returns:
        bool: True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("localhost", port)) == 0
        logger.debug(f"Port {port} is {'in use' if result else 'available'}")
        return result


def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port.
    
    Args:
        start_port (int): Starting port number to check
        max_attempts (int): Maximum number of ports to check
        
    Returns:
        int: Available port number
    """
    logger.debug(f"Searching for available port starting from {start_port}")
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            logger.debug(f"Found available port: {port}")
            return port
    logger.warning(f"No available ports found in range {start_port}-{start_port+max_attempts-1}")
    return start_port


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP server handler for browsing and viewing texts."""

    def log_message(self, format, *args):
        """Override to use our logger.
        
        Args:
            format (str): Format string for the log message
            *args: Variable arguments to format the message
        """
        logger.info("%s - %s" % (self.address_string(), format % args))

    def do_GET(self):
        """Handle GET requests.
        
        Handles various endpoints including home page, authors table, works page,
        view page, editors page, search page, and API endpoints.
        """
        try:
            logger.debug(f"GET request for {self.path}")

            if self.path == "/":
                # Home page
                html = self.get_home_page()
                self.send_html_response(html)

            elif self.path == "/simple":
                # Simple view page
                try:
                    with open("simple_view.html", "r", encoding="utf-8") as f:
                        html = f.read()
                    self.send_html_response(html)
                except FileNotFoundError:
                    self.send_error(404, "Simple view template not found")
                except Exception as e:
                    self.send_error(500, f"Error serving simple view: {str(e)}")

            elif self.path == "/authors_data.json":
                # Serve authors data JSON file
                try:
                    with open("authors_data.json", "r", encoding="utf-8") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(data.encode())
                except FileNotFoundError:
                    self.send_error(404, "Authors data file not found")
                except Exception as e:
                    self.send_error(500, f"Error serving authors data: {str(e)}")

            elif self.path == "/authors":
                # Authors table page
                html = self.get_authors_page()
                self.send_html_response(html)

            elif self.path.startswith("/works?"):
                # Works page
                query = self.path.split("?", 1)[1]
                html = self.get_works_page(query)
                self.send_html_response(html)

            elif self.path.startswith("/view?"):
                # View page
                query = self.path.split("?", 1)[1]
                html = self.get_view_page(query)
                self.send_html_response(html)

            elif self.path == "/editors":
                # Editors page
                html = self.get_editors_page()
                self.send_html_response(html)

            elif self.path == "/search":
                # Search page
                html = self.get_search_page()
                self.send_html_response(html)

            elif self.path.startswith("/api/author_works?"):
                # API endpoint to get works for an author
                query = self.path.split("?", 1)[1]
                query_params = urllib.parse.parse_qs(query)
                self.handle_get_author_works(query_params)

            elif self.path.startswith("/static/"):
                # Static files
                self.serve_static_file(self.path)

            elif self.path == SHUTDOWN_PATH:
                # Shutdown server
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Server shutting down...")
                threading.Thread(target=lambda: server_instance.shutdown()).start()

            else:
                # 404 Not Found
                self.send_error(404, "Page not found")

        except Exception as e:
            logger.error(f"Error handling GET request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            parsed_data = urllib.parse.parse_qs(post_data)

            if self.path == "/update_preference":
                self.handle_update_preference(parsed_data)
            elif self.path == "/update_century":
                self.handle_update_century(parsed_data)
            elif self.path == "/update_work_preference":
                self.handle_update_work_preference(parsed_data)
            else:
                self.send_error(404, "Endpoint not found")

        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal server error: {str(e)}")

    def handle_update_preference(self, post_data):
        """Handle updating user preferences"""
        author_id = post_data.get("author_id", [""])[0]
        pref_type = post_data.get("pref_type", [""])[0]
        value = post_data.get("value", ["false"])[0].lower() == "true"

        if not author_id or not pref_type:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current preferences
            try:
                with open("user_preferences.json", "r") as f:
                    prefs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                prefs = {"favorites": [], "archived": [], "deleted": []}

            # Update preference
            if pref_type not in prefs:
                prefs[pref_type] = []

            if value and author_id not in prefs[pref_type]:
                prefs[pref_type].append(author_id)
            elif not value and author_id in prefs[pref_type]:
                prefs[pref_type].remove(author_id)

            # Save updated preferences
            with open("user_preferences.json", "w") as f:
                json.dump(prefs, f, indent=2)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        except Exception as e:
            self.send_error(500, f"Error updating preferences: {str(e)}")

    def handle_update_century(self, post_data):
        """Handle updating author century"""
        author_id = post_data.get("author_id", [""])[0]
        century = post_data.get("century", [""])[0]

        if not author_id or not century:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current author data
            try:
                with open("authors_data.json", "r") as f:
                    authors_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                authors_data = {}

            # Update century
            if author_id in authors_data:
                authors_data[author_id]["century"] = century

                # Save updated data
                with open("authors_data.json", "w") as f:
                    json.dump(authors_data, f, indent=2)

                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            else:
                self.send_error(404, "Author not found")

        except Exception as e:
            self.send_error(500, f"Error updating century: {str(e)}")

    def handle_update_work_preference(self, post_data):
        """Handle updating work preferences (favorite, archive, delete)"""
        work_key = post_data.get("work_key", [""])[0]
        pref_type = post_data.get("pref_type", [""])[0]
        value = post_data.get("value", ["false"])[0].lower() == "true"

        if not work_key or not pref_type:
            self.send_error(400, "Missing required parameters")
            return

        # Load user preferences
        try:
            with open("user_preferences.json", "r") as f:
                user_prefs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_prefs = {
                "favorites": [],
                "archived": [],
                "deleted": [],
                "favorite_works": [],
                "archived_works": [],
                "deleted_works": [],
            }

        # Update preference
        if pref_type == "favorite_works":
            if value and work_key not in user_prefs.get("favorite_works", []):
                if "favorite_works" not in user_prefs:
                    user_prefs["favorite_works"] = []
                user_prefs["favorite_works"].append(work_key)
            elif not value and work_key in user_prefs.get("favorite_works", []):
                user_prefs["favorite_works"].remove(work_key)

        elif pref_type == "archived_works":
            if value and work_key not in user_prefs.get("archived_works", []):
                if "archived_works" not in user_prefs:
                    user_prefs["archived_works"] = []
                user_prefs["archived_works"].append(work_key)
            elif not value and work_key in user_prefs.get("archived_works", []):
                user_prefs["archived_works"].remove(work_key)

        elif pref_type == "deleted_works":
            if value and work_key not in user_prefs.get("deleted_works", []):
                if "deleted_works" not in user_prefs:
                    user_prefs["deleted_works"] = []
                user_prefs["deleted_works"].append(work_key)
            elif not value and work_key in user_prefs.get("deleted_works", []):
                user_prefs["deleted_works"].remove(work_key)

        # Save updated preferences
        with open("user_preferences.json", "w") as f:
            json.dump(user_prefs, f, indent=4)

        # Send success response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"success": True}).encode())

    def get_authors_page(self):
        """Generate the authors listing page."""
        # Load authors data
        authors_data = self.load_authors_data()
        
        # Sort authors by name
        sorted_authors = sorted(
            [(id, data) for id, data in authors_data.items()],
            key=lambda x: x[1].get('name', '').lower()
        )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authors - First 1K Greek Texts</title>
            <style>
                {MAIN_STYLESHEET}

                .authors-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}

                .author-card {{
                    background-color: #252525;
                    border-radius: 8px;
                    padding: 20px;
                    border-left: 4px solid #4299e1;
                    transition: transform 0.2s;
                }}

                .author-card:hover {{
                    transform: translateY(-3px);
                    background-color: #333;
                }}

                .author-name {{
                    font-size: 1.2em;
                    margin-bottom: 10px;
                }}

                .author-name a {{
                    text-decoration: none;
                    color: #4299e1;
                }}

                .author-meta {{
                    font-size: 0.9em;
                    color: #888;
                    margin-bottom: 5px;
                }}

                .author-works {{
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #444;
                }}

                .filter-section {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #252525;
                    border-radius: 8px;
                }}

                .filter-buttons {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 10px;
                }}

                .filter-btn {{
                    padding: 5px 15px;
                    background-color: #333;
                    border: none;
                    border-radius: 4px;
                    color: #fff;
                    cursor: pointer;
                }}

                .filter-btn:hover {{
                    background-color: #444;
                }}

                .filter-btn.active {{
                    background-color: #4299e1;
                }}
            </style>
            <script>
                function filterAuthors(century) {{
                    const cards = document.querySelectorAll('.author-card');
                    cards.forEach(card => {{
                        if (century === 'all' || card.dataset.century === century) {{
                            card.style.display = 'block';
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }});

                    // Update active button
                    document.querySelectorAll('.filter-btn').forEach(btn => {{
                        btn.classList.remove('active');
                        if (btn.dataset.century === century) {{
                            btn.classList.add('active');
                        }}
                    }});
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <h1>First 1K Greek Texts</h1>
                <p><a href="/">&laquo; Home</a></p>

                <div class="filter-section">
                    <h3>Filter by Century</h3>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-century="all" onclick="filterAuthors('all')">All</button>
            """

        # Get unique centuries
        centuries = sorted(set(data.get('century', 'Unknown') for _, data in sorted_authors))
        for century in centuries:
            html += f'<button class="filter-btn" data-century="{century}" onclick="filterAuthors(\'{century}\')">{century}</button>'

        html += """
                    </div>
                </div>

                <div class="authors-grid">
        """

        for author_id, author_data in sorted_authors:
            name = author_data.get('name', f'Author {author_id}')
            century = author_data.get('century', 'Unknown')
            allegiance = author_data.get('allegiance', 'Unknown')
            
            # Get works count
            works = self.get_author_works(author_id)
            works_count = len(works)
            
            html += f"""
            <div class="author-card" data-century="{century}">
                <div class="author-name">
                    <a href="/works?author_id={author_id}">{name}</a>
                </div>
                <div class="author-meta">Century: {century}</div>
                <div class="author-meta">Allegiance: {allegiance}</div>
                <div class="author-works">
                    {works_count} work{"s" if works_count != 1 else ""}
                </div>
            </div>
            """

        html += """
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def get_work_editor(self, author_id, work_id):
        """Extract editor information from the __cts__.xml file if available"""
        cts_file = os.path.join("data", author_id, work_id, "__cts__.xml")
        editor = None

        try:
            if os.path.exists(cts_file):
                tree = ET.parse(cts_file)
                root = tree.getroot()

                # Look for editor information in various locations within the XML
                editor_elements = root.findall(".//*[@role='editor']") or root.findall(".//editor")
                if editor_elements:
                    editor = editor_elements[0].text
                else:
                    # Check for other common patterns
                    for elem in root.findall(".//*[@n]"):
                        if "ed." in elem.get("n", "").lower() or "edit" in elem.get("n", "").lower():
                            editor = elem.get("n")
                            break

                logger.debug(f"Found editor '{editor}' for work {work_id}")
                return editor
        except Exception as e:
            logger.error(f"Error extracting editor information from {cts_file}: {str(e)}")

        return None

    def load_authors_data(self):
        """Load author metadata from authors_data.json."""
        try:
            with open('authors_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading authors data: {str(e)}")
            return {}

    def get_author_metadata(self, author_id):
        """Get metadata for a specific author."""
        authors_data = self.load_authors_data()
        return authors_data.get(author_id, {
            'name': f'Author {author_id}',
            'century': 'Unknown',
            'allegiance': 'Unknown'
        })

    def get_author_works(self, author_id):
        """Get list of works for an author with metadata."""
        works = []
        author_dir = os.path.join("data", author_id)
        
        # Get author metadata
        author_metadata = self.get_author_metadata(author_id)
        author_name = author_metadata.get('name', f'Author {author_id}')
        
        if os.path.exists(author_dir):
            for work_id in os.listdir(author_dir):
                work_path = os.path.join(author_dir, work_id)
                
                # Skip hidden files and special directories
                if work_id.startswith(".") or work_id.startswith("__"):
                    continue
                    
                if os.path.isdir(work_path):
                    # Get work metadata from __cts__.xml
                    work_title = work_id
                    work_editor = None
                    work_cts = os.path.join(work_path, "__cts__.xml")
                    
                    if os.path.exists(work_cts):
                        try:
                            with open(work_cts, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Get title
                                title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                                if title_match:
                                    work_title = title_match.group(1).strip()
                                # Get editor from description
                                desc_match = re.search(r'<ti:description[^>]*>(.*?)</ti:description>', content)
                                if desc_match:
                                    desc = desc_match.group(1)
                                    editor_match = re.search(r'([^.]+), editor\.', desc)
                                    if editor_match:
                                        work_editor = editor_match.group(1).strip()
                        except Exception as e:
                            print(f"Error reading work metadata: {str(e)}")
                    
                    # Count XML files
                    file_count = len([f for f in os.listdir(work_path) if f.endswith('.xml') and f != '__cts__.xml'])
                    
                    works.append({
                        'id': work_id,
                        'title': work_title,
                        'editor': work_editor,
                        'file_count': file_count,
                        'author_name': author_name
                    })
        
        return works

    def handle_get_author_works(self, query_params):
        """Handle API request to get works for an author"""
        author_id = query_params.get("author_id", [""])[0]

        logger.debug(f"API request for author works: author_id={author_id}")

        if not author_id:
            logger.error("Missing author_id parameter in API request")
            self.send_error(400, "Missing author_id parameter")
            return

        # Load user preferences
        try:
            with open("user_preferences.json", "r") as f:
                user_prefs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"User preferences not found or invalid JSON: {e}")
            user_prefs = {
                "favorites": [],
                "archived": [],
                "deleted": [],
                "favorite_works": [],
                "archived_works": [],
                "deleted_works": [],
            }

        logger.debug(f"Getting works for author ID: {author_id}")
        works = self.get_author_works(author_id)
        logger.debug(f"Found {len(works)} works for author ID: {author_id}")

        # Add user preference flags to each work
        for work in works:
            work_key = f"{author_id}:{work['id']}"
            work["favorite"] = work_key in user_prefs.get("favorite_works", [])
            work["archived"] = work_key in user_prefs.get("archived_works", [])
            work["deleted"] = work_key in user_prefs.get("deleted_works", [])

        # Filter out deleted works
        works = [w for w in works if not w["deleted"]]

        # Send response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response_body = json.dumps(works)
        logger.debug(f"Sending works response for author_id={author_id}: {response_body[:100]}...")
        self.wfile.write(response_body.encode())

    def serve_static_file(self, path):
        """Serve static files"""
        try:
            # Get the script directory to ensure we can locate static files
            # regardless of where the script is run from
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Remove leading slash and construct full path
            file_path = path[1:]  # Remove leading slash
            full_path = os.path.join(script_dir, file_path)

            logger.debug(f"Serving static file from: {full_path}")
            content_type = self.get_content_type(file_path)

            with open(full_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            logger.error(f"Static file not found: {path}")
            self.send_error(404, "File not found")
        except Exception as e:
            logger.error(f"Error serving static file ({path}): {str(e)}")
            self.send_error(500, f"Error serving file: {str(e)}")

    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
        }
        return content_types.get(ext, "application/octet-stream")

    def send_html_response(self, html):
        """Send HTML response"""
        logger.debug(f"Sending HTML response, length: {len(html) if html else 0}")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        try:
            if html:
                encoded_html = html.encode("utf-8")
                self.wfile.write(encoded_html)
                logger.debug(f"Successfully sent {len(encoded_html)} bytes")
            else:
                logger.warning("Empty HTML response")
        except Exception as e:
            logger.error(f"Error while sending HTML response: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_home_page(self):
        """Generate the home page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1KGreek Browser</title>
            <style>
                {MAIN_STYLESHEET}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>First1KGreek Browser</h1>
                <p>Welcome to the First1KGreek Browser. This tool allows you to browse and search ancient Greek texts.</p>

                <h2>Navigation</h2>
                <ul>
                    <li><a href="/simple">Simple View</a> - Browse authors and works by century</li>
                    <li><a href="/authors">Authors Table</a> - Browse all authors</li>
                    <li><a href="/search">Search</a> - Search for specific texts</li>
                    <li><a href="/editors">About the Editors</a> - Information about the editors</li>
                </ul>
            </div>
        </body>
        </html>
        """
        return html

    def get_works_page(self, query):
        """Generate the works page for an author."""
        query_params = urllib.parse.parse_qs(query)
        author_id = query_params.get("author_id", [""])[0]

        if not author_id:
            return self.get_error_page("Missing author_id parameter")

        # Get author metadata
        author_metadata = self.get_author_metadata(author_id)
        author_name = author_metadata.get('name', f'Author {author_id}')
        century = author_metadata.get('century', 'Unknown')
        allegiance = author_metadata.get('allegiance', 'Unknown')

        # Get works for this author
        works = self.get_author_works(author_id)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Works by {author_name}</title>
            <style>
                {MAIN_STYLESHEET}

                .author-info {{
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #252525;
                    border-radius: 8px;
                }}

                .works-list {{
                    list-style-type: none;
                    padding: 0;
                }}

                .work-item {{
                    margin-bottom: 15px;
                    padding: 15px;
                    background-color: #333;
                    border-radius: 8px;
                    border-left: 4px solid #4299e1;
                }}

                .work-item:hover {{
                    background-color: #444;
                }}

                .work-title {{
                    font-size: 1.2em;
                    margin-bottom: 10px;
                }}

                .work-title a {{
                    text-decoration: none;
                    color: #4299e1;
                }}

                .work-meta {{
                    font-size: 0.9em;
                    color: #888;
                }}

                .editor-info {{
                    margin-top: 5px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works by {author_name}</h1>
                <p><a href="/">&laquo; Home</a> | <a href="/authors">Authors Table</a></p>

                <div class="author-info">
                    <h3>{author_name}</h3>
                    <p>Century: {century}</p>
                    <p>Allegiance: {allegiance}</p>
                </div>

                <h2>Available Works</h2>
                """

        if works:
            html += '<div class="works-list">'
            for work in works:
                editor_info = f'<div class="editor-info">Editor: {work["editor"]}</div>' if work["editor"] else ''
                file_info = f'<div class="work-meta">{work["file_count"]} file{"s" if work["file_count"] != 1 else ""}</div>'
                
                html += f"""
                <div class="work-item">
                    <div class="work-title">
                        <a href="/view?author_id={author_id}&work_id={work['id']}">{work['title']}</a>
                    </div>
                    {editor_info}
                    {file_info}
                </div>
                """
            html += "</div>"
        else:
            html += "<p>No works available for this author.</p>"

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def get_view_page(self, query):
        """Generate the view page for a specific work"""
        query_params = urllib.parse.parse_qs(query)
        author_id = query_params.get("author_id", [""])[0]
        work_id = query_params.get("work_id", [""])[0]

        if not author_id or not work_id:
            return self.get_error_page("Missing author_id or work_id parameter")

        # Get author info
        author_name = "Unknown Author"
        if author_id in AUTHORS_DATA:
            author_name = AUTHORS_DATA[author_id].get("name", "Unknown Author")

        # Check if work exists
        work_path = os.path.join("data", author_id, work_id)
        if not os.path.exists(work_path):
            return self.get_error_page(f"Work {work_id} by {author_name} not found")

        # Get work content
        content = self.get_work_content(author_id, work_id)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{work_id} by {author_name}</title>
            <style>
                {READER_STYLESHEET}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{work_id}</h1>
                <h2>by {author_name}</h2>
                <p><a href="/">&laquo; Home</a> | <a href="/works?author_id={author_id}">Back to Works</a></p>

                <div class="work-content">
                    {content}
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def get_work_content(self, author_id, work_id):
        """Get the content of a work"""
        work_path = os.path.join("data", author_id, work_id)
        content = "<p>This work contains multiple files. Please select from the list below:</p><ul>"

        try:
            # List all files in the work directory
            files = os.listdir(work_path)
            if files:
                for file in files:
                    if file.endswith(".xml") or file.endswith(".txt"):
                        file_path = os.path.join(work_path, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_content = f.read()
                                if file.endswith(".xml"):
                                    # Basic XML handling - just escape and display for now
                                    file_content = escape(file_content)
                                content += f"<li><h3>{file}</h3><pre>{file_content}</pre></li>"
                        except Exception as e:
                            content += f"<li>Error reading {file}: {str(e)}</li>"
            else:
                content = "<p>No content files found for this work.</p>"

        except Exception as e:
            content = f"<p>Error accessing work content: {str(e)}</p>"

        return content

    def get_editors_page(self):
        """Generate the editors page"""
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>About the Editors</title>
            <style>
                {MAIN_STYLESHEET}

                .editors-list {{
                    margin-top: 20px;
                }}

                .editor-section {{
                    margin-bottom: 30px;
                    padding: 15px;
                    background-color: #333;
                    border-radius: 5px;
                }}

                .editor-name {{
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #4299e1;
                    margin-bottom: 10px;
                }}

                .editor-works {{
                    list-style-type: none;
                    padding-left: 0;
                }}

                .editor-works li {{
                    padding: 5px 0;
                    border-bottom: 1px solid #444;
                }}

                .editor-works li:last-child {{
                    border-bottom: none;
                }}

                .no-editors {{
                    padding: 20px;
                    color: #fc8181;
                    text-align: center;
                    background-color: #333;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>About the Editors</h1>
                <p><a href="/">&laquo; Home</a> | <a href="/authors">Authors Table</a></p>

                <p>First1KGreek is a collection of ancient Greek texts maintained by a dedicated team of editors and scholars.</p>

                <h2>Editorial Team</h2>
                <ul>
                    <li><strong>Project Director:</strong> Digital Classicist Collaborative</li>
                    <li><strong>Technical Lead:</strong> Perseus Digital Library</li>
                    <li><strong>Contributors:</strong> The scholarly community</li>
                </ul>

                <h2>Editors ({len(editors)} found)</h2>
        '''

        # Find all unique editors in the works
        editors = {}
        total_editors = 0

        try:
            # Scan through all author directories
            data_dir = os.path.join("data")
            if os.path.exists(data_dir):
                for author_id in os.listdir(data_dir):
                    author_dir = os.path.join(data_dir, author_id)

                    # Skip hidden directories and files
                    if not os.path.isdir(author_dir) or author_id.startswith("."):
                        continue

                    # Get author name
                    author_name = AUTHORS_DATA.get(author_id, {}).get("name", author_id)

                    # Scan works for this author
                    for work_id in os.listdir(author_dir):
                        work_path = os.path.join(author_dir, work_id)

                        # Skip hidden and non-directory items
                        if not os.path.isdir(work_path) or work_id.startswith(".") or work_id.startswith("__"):
                            continue

                        # Check for __cts__.xml to extract editor
                        editor = self.get_work_editor(author_id, work_id)
                        if editor:
                            if editor not in editors:
                                editors[editor] = []

                            editors[editor].append(
                                {"author_id": author_id, "author_name": author_name, "work_id": work_id}
                            )
                            total_editors += 1
        except Exception as e:
            logger.error(f"Error scanning for editors: {str(e)}")

        # Generate HTML
        if editors:
            html += """<div class="editors-list">"""

            # Sort editors by name
            sorted_editors = sorted(editors.items(), key=lambda x: x[0].lower())

            for editor_name, works in sorted_editors:
                html += f"""
                <div class="editor-section">
                    <div class="editor-name">{editor_name}</div>
                    <ul class="editor-works">
                """

                # Sort works by author name
                sorted_works = sorted(works, key=lambda x: x["author_name"].lower())

                for work in sorted_works:
                    html += f"""
                    <li>
                        <a href="/view?author_id={work['author_id']}&work_id={work['work_id']}">
                            {work['author_name']} - {work['work_id']}
                        </a>
                    </li>
                    """

                html += """
                    </ul>
                </div>
                """

            html += """</div>"""
        else:
            html += """
            <div class="no-editors">
                <p>No editor information found in the works. This could be because the __cts__.xml files don't contain editor metadata.</p>
            </div>
            """

        html += """
                <h2>Contributing</h2>
                <p>If you would like to contribute to this project, please read the documentation in the repository.</p>
            </div>
        </body>
        </html>
        """

        return html

    def get_search_page(self):
        """Generate the search page"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Texts</title>
            <style>
                {MAIN_STYLESHEET}

                .search-form {{
                    margin: 20px 0;
                    padding: 20px;
                    background-color: #333;
                    border-radius: 5px;
                }}

                .search-form input[type="text"] {{
                    padding: 10px;
                    width: 70%;
                    background-color: #444;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                }}

                .search-form button {{
                    padding: 10px 20px;
                    background-color: #3182ce;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: 10px;
                }}

                .search-form button:hover {{
                    background-color: #2c5282;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Search Texts</h1>
                <p><a href="/">&laquo; Home</a></p>

                <div class="search-form">
                    <form action="/search" method="get">
                        <input type="text" name="q" placeholder="Search for authors, works, or content...">
                        <button type="submit">Search</button>
                    </form>
                </div>

                <p>Note: Full text search will be implemented in a future update.</p>
            </div>
        </body>
        </html>
        """

        return html

    def get_error_page(self, error_message):
        """Generate an error page"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                {MAIN_STYLESHEET}

                .error-message {{
                    color: #fc8181;
                    font-weight: bold;
                    padding: 20px;
                    background-color: #3a3a3a;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Error</h1>
                <p><a href="/">&laquo; Home</a></p>

                <div class="error-message">
                    {error_message}
                </div>
            </div>
        </body>
        </html>
        """

        return html


if __name__ == "__main__":
    try:
        # Make sure socket is properly released after previous runs
        socketserver.TCPServer.allow_reuse_address = True

        logger.info(f"Checking port {PORT} availability...")
        max_retries = 5
        current_port = PORT

        for attempt in range(max_retries):
            try:
                if is_port_in_use(current_port):
                    logger.warning(f"Port {current_port} is already in use.")
                    new_port = find_available_port(current_port + 1)
                    if new_port != current_port:
                        logger.info(f"Using alternative port {new_port}")
                        current_port = new_port
                    else:
                        logger.error("Failed to find an available port. Terminating.")
                        sys.exit(1)

                logger.info(f"Starting server on port {current_port}...")
                server_instance = socketserver.TCPServer((HOST, current_port), CustomHTTPRequestHandler)
                logger.info(f"Server started at http://{HOST}:{current_port}")

                # Print directly to console for visibility
                print(f"\n======================================")
                print(f"Server is running at http://{HOST}:{current_port}")
                print(f"Press Ctrl+C to shutdown")
                print(f"======================================\n")

                server_instance.serve_forever()
                break  # Exit the retry loop if server starts successfully

            except OSError as e:
                if e.errno == 48 or e.errno == 98:  # Address already in use
                    logger.warning(f"Port {current_port} is blocked, trying another port...")
                    current_port = current_port + 1
                    if attempt == max_retries - 1:
                        logger.error("Maximum retry attempts reached. Terminating.")
                        sys.exit(1)
                else:
                    logger.error(f"OS Error: {str(e)}")
                    raise

    except KeyboardInterrupt:
        logger.info("\nServer shutdown requested.")
        if server_instance:
            server_instance.shutdown()
        logger.info("Server has been shut down.")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        logger.error(traceback.format_exc())
