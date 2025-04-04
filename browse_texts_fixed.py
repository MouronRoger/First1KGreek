#!/usr/bin/env python3
"""
First1KGreek Browser - Fixed Version
Version: 1.2.0 (with cache-busting and dark theme)
Last updated: 2025-03-07
"""

import os
import sys
import http.server
import socketserver
import json
import re
import threading
import time
import socket
import xml.etree.ElementTree as ET
import urllib.parse
from urllib.error import URLError, HTTPError
from html import escape

# Global variable to store server instance
server_instance = None

# Constants
PORT = 8000
HOST = "localhost"
SHUTDOWN_PATH = "/shutdown"

# Load author data
try:
    with open('authors_data.json', 'r', encoding='utf-8') as f:
        AUTHORS_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading author data: {e}")
    AUTHORS_DATA = {}

# Print version info when starting
print("Starting First1KGreek Browser - Fixed Version 1.2.0")
print("With dark theme and improved editor detection")

# Reader mode stylesheet
READER_STYLESHEET = """
body { 
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.8; 
    background-color: #2a2a2a; 
    color: #f2f2f2; 
}
h1, h2, h3 { 
    color: #fff;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #4299e1; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 800px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #333;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    min-height: 100vh;
}
""" 

# Main stylesheet
MAIN_STYLESHEET = """
body { 
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.6; 
    background-color: #1a1a1a; 
    color: #ffffff; 
}
h1, h2, h3 { 
    color: #4299e1;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #4299e1; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 1000px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #2d2d2d;
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
    background-color: #333;
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
    border-bottom: 1px solid #444;
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
    background-color: #3a3a3a;
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
    background-color: #f6ad55;
}

.favorite-btn:hover {
    background-color: #ed8936;
}

.favorite-btn.active {
    background-color: #ed8936;
}

.archive-btn {
    background-color: #68d391;
}

.archive-btn:hover {
    background-color: #48bb78;
}

.archive-btn.active {
    background-color: #48bb78;
}

.delete-btn {
    background-color: #fc8181;
}

.delete-btn:hover {
    background-color: #f56565;
}

.delete-btn.active {
    background-color: #f56565;
}

.edit-btn {
    background-color: #4299e1;
}

.edit-btn:hover {
    background-color: #3182ce;
}

.status-filters, .century-filters {
    margin: 10px 0;
}

.status-filters button, .century-filters button {
    padding: 8px 15px;
    margin-right: 10px;
    background-color: #2d3748;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.status-filters button:hover, .century-filters button:hover {
    background-color: #4a5568;
}

.status-filters button.active, .century-filters button.active {
    background-color: #3182ce;
}

.pagination {
    margin: 20px 0;
    text-align: center;
}

.pagination button {
    padding: 8px 15px;
    margin: 0 5px;
    background-color: #2d3748;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.pagination button:hover {
    background-color: #4a5568;
}

.pagination button.active {
    background-color: #3182ce;
}

.search-filter {
    margin: 20px 0;
    padding: 20px;
    background-color: #2a4365;
    border-radius: 5px;
}

.search-filter input[type="text"] {
    padding: 10px;
    width: 70%;
    border: 1px solid #444;
    background-color: #333;
    color: white;
    border-radius: 4px;
}

.search-filter button {
    padding: 10px 20px;
    background-color: #3182ce;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    margin-left: 10px;
}

.search-filter button:hover {
    background-color: #2c5282;
}

.favorites-star {
    color: #f6ad55;
    font-size: 1.2em;
    margin-right: 5px;
}

.archived-icon {
    color: #68d391;
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
    background-color: #2d2d2d;
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
    border-bottom: 1px solid #444;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.modal-header h2 {
    margin: 0;
    color: #4299e1;
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
    color: #eee;
}

.modal-body input {
    width: 100%;
    padding: 8px;
    margin-bottom: 15px;
    border: 1px solid #444;
    background-color: #333;
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
    background-color: #4299e1;
    color: white;
}

.save-btn:hover {
    background-color: #3182ce;
}

.cancel-btn {
    background-color: #718096;
    color: white;
}

.cancel-btn:hover {
    background-color: #4a5568;
}
"""

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return start_port

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP server handler for browsing and viewing texts"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # Serve static files
        if path.startswith('/static/'):
            self.serve_static_file(path)
            return

        # Handle other routes
        if path == '/':
            self.send_html_response(self.get_home_page())
        elif path == '/authors':
            self.send_html_response(self.get_authors_table_page())
        elif path == '/works':
            self.send_html_response(self.get_works_page(parsed_path.query))
        elif path == '/view':
            self.send_html_response(self.get_view_page(parsed_path.query))
        elif path == '/editors':
            self.send_html_response(self.get_editors_page())
        elif path == '/search':
            self.send_html_response(self.get_search_page())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # Parse form data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))

        if path == '/update_preference':
            self.handle_update_preference(post_data)
        elif path == '/update_century':
            self.handle_update_century(post_data)
        else:
            self.send_error(404, "Not Found")

    def handle_update_preference(self, post_data):
        """Handle updating user preferences"""
        author_id = post_data.get('author_id', [''])[0]
        pref_type = post_data.get('pref_type', [''])[0]
        value = post_data.get('value', ['false'])[0].lower() == 'true'

        if not author_id or not pref_type:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current preferences
            try:
                with open('user_preferences.json', 'r') as f:
                    prefs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                prefs = {'favorites': [], 'archived': [], 'deleted': []}

            # Update preference
            if pref_type not in prefs:
                prefs[pref_type] = []

            if value and author_id not in prefs[pref_type]:
                prefs[pref_type].append(author_id)
            elif not value and author_id in prefs[pref_type]:
                prefs[pref_type].remove(author_id)

            # Save updated preferences
            with open('user_preferences.json', 'w') as f:
                json.dump(prefs, f, indent=2)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())

        except Exception as e:
            self.send_error(500, f"Error updating preferences: {str(e)}")

    def handle_update_century(self, post_data):
        """Handle updating author century"""
        author_id = post_data.get('author_id', [''])[0]
        century = post_data.get('century', [''])[0]

        if not author_id or not century:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current author data
            try:
                with open('authors_data.json', 'r') as f:
                    authors_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                authors_data = {}

            # Update century
            if author_id in authors_data:
                authors_data[author_id]['century'] = century

                # Save updated data
                with open('authors_data.json', 'w') as f:
                    json.dump(authors_data, f, indent=2)

                self.send_response(200)
                self.send_header('content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            else:
                self.send_error(404, "Author not found")

        except Exception as e:
            self.send_error(500, f"Error updating century: {str(e)}")

    def get_authors_table_page(self):
        """Generate the authors table page"""
        # Load user preferences
        try:
            with open('user_preferences.json', 'r') as f:
                user_prefs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_prefs = {'favorites': [], 'archived': [], 'deleted': []}

        # Load author data
        try:
            with open('authors_data.json', 'r') as f:
                authors_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            authors_data = {}

        # HTML template with JavaScript and CSS includes
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authors Table</title>
            <link rel="stylesheet" href="/static/css/styles.css">
            <script id="user-prefs" type="application/json">
                {json.dumps(user_prefs)}
            </script>
            <script src="/static/js/authors_table.js"></script>
        </head>
        <body>
            <div class="container">
                <h1>Authors Table</h1>
                
                <div class="filters">
                    <div class="search-box">
                        <input type="text" id="search-input" placeholder="Search authors...">
                        <button id="search-btn">Search</button>
                    </div>
                    
                    <div class="status-filters">
                        <button class="active" data-filter="all">All</button>
                        <button data-filter="favorites">Favorites</button>
                        <button data-filter="archived">Archived</button>
                        <button data-filter="normal">Normal</button>
                    </div>
                    
                    <div class="century-filters">
                        <button class="active" data-filter="all">All Centuries</button>
                        <button data-filter="BCE">BCE</button>
                        <button data-filter="CE-1-3">CE 1-3</button>
                        <button data-filter="CE-4-6">CE 4-6</button>
                    </div>
                </div>

                <table id="authors-table" class="authors-table">
                    <thead>
                        <tr>
                            <th data-sort="author_name">Author Name</th>
                            <th data-sort="century">Century</th>
                            <th data-sort="works">Works</th>
                            <th data-sort="allegiance">Allegiance</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                '''

        # Add table rows
        for author_id, author_data in authors_data.items():
            if author_id in (user_prefs.get('deleted', []) or []):
                continue

            author_name = author_data.get('name', '')
            century = author_data.get('century', '')
            allegiance = author_data.get('allegiance', '')
            works_count = len(self.get_author_works(author_id))

            # Add icons for favorite/archived status
            name_prefix = ''
            if author_id in (user_prefs.get('favorites', []) or []):
                name_prefix += '<span class="favorites-star">★</span> '
            if author_id in (user_prefs.get('archived', []) or []):
                name_prefix += '<span class="archived-icon">📦</span> '

            html += f'''
                        <tr data-id="{author_id}">
                            <td data-column="author_name">{name_prefix}{author_name}</td>
                            <td data-column="century">{century}</td>
                            <td data-column="works">{works_count}</td>
                            <td data-column="allegiance">{allegiance}</td>
                            <td class="actions">
                                <button class="favorite-btn" data-author-id="{author_id}">
                                    {'Unfavorite' if author_id in (user_prefs.get('favorites', []) or []) else 'Favorite'}
                                </button>
                                <button class="archive-btn" data-author-id="{author_id}">
                                    {'Unarchive' if author_id in (user_prefs.get('archived', []) or []) else 'Archive'}
                                </button>
                                <button class="delete-btn" data-author-id="{author_id}">Delete</button>
                                <button class="edit-btn" 
                                        data-author-id="{author_id}"
                                        data-author-name="{author_name}"
                                        data-century="{century}">
                                    Edit Century
                                </button>
                            </td>
                        </tr>
                    '''

        # Close table and add modal
        html += '''
                    </tbody>
                </table>
                
                <div class="pagination"></div>

                <div id="century-modal" class="modal">
                    <div class="modal-content">
                        <span class="close-modal">&times;</span>
                        <h2>Edit Century</h2>
                        <p id="edit-author-name"></p>
                        <input type="hidden" id="edit-author-id">
                        <input type="text" id="edit-century" placeholder="Enter century (e.g., 2 BCE, 1 CE)">
                        <div class="modal-buttons">
                            <button class="cancel-btn">Cancel</button>
                            <button class="save-btn">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''

        return html

    def get_author_works(self, author_id):
        """Get list of works for an author"""
        works = []
        author_dir = os.path.join('data', author_id)
        
        if os.path.exists(author_dir):
            for item in os.listdir(author_dir):
                work_path = os.path.join(author_dir, item)
                if os.path.isdir(work_path) and not item.startswith('__'):
                    works.append(item)
        
        return works

    def serve_static_file(self, path):
        """Serve static files"""
        try:
            file_path = path[1:]  # Remove leading slash
            content_type = self.get_content_type(file_path)

            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_error(404, "File not found")
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")

    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
        }
        return content_types.get(ext, 'application/octet-stream')

    def send_html_response(self, html):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

if __name__ == "__main__":
    try:
        print(f"Starting server on port {PORT}...")
        httpd = socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler)
        print(f"Server started at http://{HOST}:{PORT}")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Try closing any running instances or use the following command to force close:")
            print(f"lsof -i :{PORT} | grep Python | awk '{{print $2}}' | xargs kill -9")
        else:
            print(f"Error starting server: {str(e)}")
    except Exception as e:
        print(f"Error starting server: {str(e)}") 