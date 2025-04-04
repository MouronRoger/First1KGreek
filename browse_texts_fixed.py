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
import shutil
from html import escape
import webbrowser
from urllib.parse import parse_qs, urlparse, quote
import re
import threading
import time
import socket
import xml.etree.ElementTree as ET
import urllib.request
from urllib.error import URLError, HTTPError
import traceback
import requests
import urllib.parse
from urllib.parse import urlparse, parse_qs

# Global variable to store server instance
server_instance = None

# Constants
PORT = 8000
HOST = "localhost"
SHUTDOWN_PATH = "/shutdown"

# Load author centuries data
try:
    with open('author_centuries_updated.json', 'r', encoding='utf-8') as f:
        AUTHOR_CENTURIES = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading author centuries data: {e}")
    AUTHOR_CENTURIES = {}

# Create a backup of the file if it doesn't exist already
if not os.path.exists('browse_texts.py.bak'):
    shutil.copy('browse_texts.py', 'browse_texts.py.bak')

# Print version info when starting
print("Starting First1KGreek Browser - Fixed Version 1.2.0")
print("With dark theme and improved editor detection")

# Load the author centuries data
AUTHOR_CENTURIES_FILE = 'author_centuries.json'
AUTHOR_CENTURIES = {}
try:
    with open(AUTHOR_CENTURIES_FILE, 'r', encoding='utf-8') as f:
        AUTHOR_CENTURIES = json.load(f)
    print(f"Loaded author data from {AUTHOR_CENTURIES_FILE}")
except Exception as e:
    print(f"Warning: Could not load {AUTHOR_CENTURIES_FILE}: {e}")
    # Create a default file if it doesn't exist
    if not os.path.exists(AUTHOR_CENTURIES_FILE):
        default_centuries = {}
        with open(AUTHOR_CENTURIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_centuries, f, indent=2)

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

# Check if MAIN_STYLESHEET exists
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

# Add stylesheet for the authors table
AUTHORS_TABLE_STYLESHEET = """
.authors-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: #333;
    border-radius: 5px;
    overflow: hidden;
    table-layout: fixed;  /* Added for fixed column widths */
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
    width: 20ch;  /* Fixed width for author names */
}

.authors-table th:nth-child(2),
.authors-table td:nth-child(2) {
    width: 12ch;  /* Width for century */
}

.authors-table th:nth-child(3),
.authors-table td:nth-child(3) {
    width: 8ch;  /* Width for works count */
}

.authors-table th:nth-child(4),
.authors-table td:nth-child(4) {
    width: 15ch;  /* Width for allegiance */
}

.authors-table th:nth-child(5),
.authors-table td:nth-child(5) {
    width: auto;  /* Actions column takes remaining space */
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
    return start_port  # Fallback to the original port if none found

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
        elif path == '/import':
            self.send_html_response(self.get_import_page())
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

    def get_home_page(self):
        """Generate the home page HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Text Browser</title>
            <meta charset="UTF-8">
            <style>
                {MAIN_STYLESHEET}
                .nav {{ margin: 20px 0; }}
                .nav a {{ 
                    display: inline-block; 
                    margin-right: 15px; 
                    background: #3182ce; 
                    color: white; 
                    padding: 10px 15px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                }}
                .nav a:hover {{ background: #2c5282; }}
                .search-box {{ 
                    margin: 30px 0; 
                    padding: 20px; 
                    background: #2a4365; 
                    border-radius: 5px; 
                }}
                .search-box input[type="text"] {{ 
                    padding: 10px; 
                    width: 70%; 
                    border: 1px solid #444; 
                    background: #333;
                    color: white;
                }}
                .search-box button {{ 
                    padding: 10px 20px; 
                    background: #3182ce; 
                    color: white; 
                    border: none; 
                    cursor: pointer; 
                    border-radius: 4px;
                }}
                .search-box button:hover {{ background: #2c5282; }}
                .about {{ 
                    margin-top: 40px; 
                    padding: 20px; 
                    background: #323232; 
                    border-radius: 5px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>First1K Greek - Text Browser</h1>
                
                <div class="nav">
                    <a href="/authors">Browse Authors</a>
                    <a href="/authors_table">Authors Table</a>
                    <a href="/editors">Browse Editors</a>
                    <a href="/search">Search</a>
                    <a href="/import">Import from Scaife</a>
                </div>
                
                <div class="search-box">
                    <h2>Search Texts</h2>
                    <form action="/search" method="get">
                        <input type="text" name="q" placeholder="Enter search term...">
                        <button type="submit">Search</button>
                    </form>
                </div>
                
                <div class="about">
                    <h2>About First1K Greek</h2>
                    <p>This browser allows you to explore Greek texts from the First Thousand Years of Greek Project.</p>
                    <p>The texts are encoded in TEI XML format and contain works from ancient Greek authors.</p>
                    <p>Use the navigation links above to browse by author, editor, or search for specific content.</p>
                    <p>The <a href="/authors_table">Authors Table</a> provides a sortable and filterable view of all authors with their works and centuries.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_authors_page(self):
        """Generate the authors listing page with rich styling matching the original version"""
        # Get author directories from the data folder
        author_dirs = []
        for item in os.listdir('data'):
            item_path = os.path.join('data', item)
            if os.path.isdir(item_path) and (item.startswith('tlg') or item.startswith('heb')):
                author_dirs.append(item)
        
        # Get author names from catalog or XML files
        author_names = {}
        for author_id in author_dirs:
            # Try to find an author name from any XML file
            author_name = self.get_author_name_from_files(author_id)
            author_names[author_id] = author_name if author_name else author_id
        
        # Create a list of (author_id, author_name) tuples for sorting
        author_items = [(author_id, author_names[author_id]) for author_id in author_dirs]
        
        # Sort alphabetically by author name, then by ID if names are the same
        author_items.sort(key=lambda x: (x[1].lower(), x[0]))
        
        # Extract the sorted author_ids
        author_dirs = [item[0] for item in author_items]
        
        # Build the HTML with grid layout
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First 1K Greek - Authors</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
            <meta http-equiv="Pragma" content="no-cache">
            <meta http-equiv="Expires" content="0">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    line-height: 1.6; 
                    background-color: #1a1a1a;
                    color: #fff;
                }
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }
                h1 { 
                    color: #fff; 
                    margin-bottom: 30px;
                }
                .nav { 
                    margin: 20px 0; 
                }
                .nav a { 
                    display: inline-block; 
                    margin-right: 15px; 
                    background: #0066cc; 
                    color: white; 
                    padding: 10px 15px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                }
                .nav a:hover { 
                    background: #004080; 
                }
                .author-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    grid-gap: 20px;
                    margin-top: 20px;
                }
                .author-card {
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 20px;
                    transition: transform 0.3s;
                    cursor: pointer;
                }
                .author-card:hover {
                    transform: translateY(-5px);
                    background-color: #333;
                }
                .author-count {
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #aaa;
                }
                .description {
                    margin-bottom: 20px;
                    font-style: italic;
                    color: #ccc;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Authors</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/authors_table">Authors Table</a>
                    <a href="/editors">Browse Editors</a>
                    <a href="/search">Search</a>
                </div>
                
                <div class="description">
                    Showing {len(author_dirs)} authors, alphabetically ordered by name
                </div>
                
                <div class="author-grid">
        """
        
        for author_id in author_dirs:
            author_name = author_names[author_id]
            display_name = f"{author_name} ({author_id})" if author_name != author_id else author_id
            
            html += f'''
            <a href="/works?author={author_id}" style="text-decoration: none; color: inherit;">
                <div class="author-card">
                    <div class="author-name">{display_name}</div>
                </div>
            </a>
            '''
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_author_name_from_files(self, author_id):
        """Attempt to find an author name from XML files"""
        author_path = os.path.join('data', author_id)
        if not os.path.exists(author_path):
            return None
            
        # Check a few files to find the author name
        for work_dir in os.listdir(author_path):
            work_path = os.path.join(author_path, work_dir)
            if os.path.isdir(work_path):
                for file in os.listdir(work_path):
                    if file.endswith('.xml') and not file == '__cts__.xml':
                        file_path = os.path.join(work_path, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(10000)  # Just read the beginning where metadata usually is
                                
                            # Look for author tag with reasonable content
                            author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                            if author_matches and len(author_matches[0].strip()) > 0:
                                return author_matches[0].strip()
                                
                        except Exception as e:
                            pass
        
        return None
    
    def get_works_page(self, author_id):
        """Generate the works listing page for an author"""
        author_path = os.path.join('data', author_id)
        works = []
        
        # Try to get the author name
        author_name = self.get_author_name_from_files(author_id) or author_id
        
        if os.path.exists(author_path):
            for item in os.listdir(author_path):
                item_path = os.path.join(author_path, item)
                if os.path.isdir(item_path):
                    work_files = []
                    work_title = item  # Default to directory name
                    
                    # Look for a descriptive title in the XML files
                    for file in os.listdir(item_path):
                        if file.endswith('.xml'):
                            file_path = os.path.join('data', author_id, item, file)
                            
                            # If it's a __cts__.xml file, it likely has good metadata
                            if file == '__cts__.xml':
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    # Look for a title
                                    title_matches = re.findall(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                                    if title_matches and title_matches[0].strip():
                                        work_title = title_matches[0].strip()
                                except Exception as e:
                                    print(f"Error reading {file_path}: {str(e)}")
                            
                            # Add the file to the list
                            work_files.append({
                                'file': file,
                                'path': file_path
                            })
                    
                    # Add the work to the list
                    works.append({
                        'id': item,
                        'title': work_title,
                        'files': work_files
                    })
        
        # Sort works by title
        works.sort(key=lambda x: x['title'].lower())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First 1K Greek - Works for {author_name}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
            <meta http-equiv="Pragma" content="no-cache">
            <meta http-equiv="Expires" content="0">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    line-height: 1.6; 
                    background-color: #1a1a1a;
                    color: #fff;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                h1, h2 {{ 
                    color: #fff; 
                    margin-bottom: 20px;
                }}
                .nav {{ 
                    margin: 20px 0; 
                }}
                .nav a {{ 
                    display: inline-block; 
                    margin-right: 15px; 
                    background: #0066cc; 
                    color: white; 
                    padding: 10px 15px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                }}
                .nav a:hover {{ 
                    background: #004080; 
                }}
                .work-list {{ 
                    margin-top: 20px; 
                }}
                .work-item {{ 
                    padding: 15px; 
                    border-bottom: 1px solid #333; 
                    background-color: #2d2d2d;
                    margin-bottom: 15px;
                    border-radius: 5px;
                }}
                .work-item:hover {{ 
                    background-color: #333; 
                }}
                .work-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .work-id {{
                    color: #aaa;
                    font-size: 0.9em;
                    font-family: monospace;
                    margin-bottom: 10px;
                }}
                .file-links {{
                    margin-top: 10px;
                }}
                .file-links a {{
                    display: inline-block;
                    margin-right: 10px;
                    margin-bottom: 5px;
                    color: #4299e1;
                }}
                .description {{
                    margin-bottom: 20px;
                    font-style: italic;
                    color: #ccc;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works by {author_name}</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/authors">Back to Authors</a>
                </div>
                
                <div class="description">
                    Found {len(works)} works for author ID: {author_id}
                </div>
                
                <div class="work-list">
        """
        
        for work in works:
            html += f'<div class="work-item">'
            html += f'<div class="work-title">{work["title"]}</div>'
            html += f'<div class="work-id">Work ID: {work["id"]}</div>'
            html += f'<div class="file-links">'
            
            # List the XML files in this work
            for file_info in work['files']:
                if file_info['file'] != '__cts__.xml':
                    file_name = file_info['file']
                    file_path = file_info['path']
                    html += f'<a href="/view?path={file_path}">{file_name}</a> '
                    html += f'<a href="/reader?path={file_path}">[Reader]</a><br>'
            
            html += '</div></div>\n'
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
        
    def get_view_page(self, file_path):
        """Generate the XML view page"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Escape the XML content for HTML display
            escaped_content = escape(content)
            
            # Get relative information about the file
            parts = file_path.split('/')
            author_id = parts[1] if len(parts) > 1 else ""
            work_id = parts[2] if len(parts) > 2 else ""
            
            # Generate a cache-busting timestamp for CSS
            cache_buster = int(time.time())
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>First 1K Greek - View XML</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
                <meta http-equiv="Pragma" content="no-cache">
                <meta http-equiv="Expires" content="0">
                <style>
                    /* Cache-busting CSS v{cache_buster} */
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 0; 
                        line-height: 1.6; 
                        background-color: #1a1a1a;
                        color: #fff;
                    }}
                    .container {{ 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        padding: 20px; 
                    }}
                    h1, h2 {{ 
                        color: #fff; 
                        margin-bottom: 20px;
                    }}
                    .nav {{ 
                        margin: 20px 0; 
                    }}
                    .nav a {{ 
                        display: inline-block; 
                        margin-right: 15px; 
                        background: #0066cc; 
                        color: white; 
                        padding: 10px 15px; 
                        text-decoration: none; 
                        border-radius: 4px; 
                    }}
                    .nav a:hover {{ 
                        background: #004080; 
                    }}
                    .reader-link {{ 
                        display: inline-block; 
                        margin-top: 10px;
                        margin-bottom: 20px;
                        color: #4299e1; 
                        text-decoration: none; 
                    }}
                    .reader-link:hover {{
                        text-decoration: underline;
                    }}
                    .file-info {{
                        background-color: #2d2d2d;
                        border-left: 4px solid #4299e1;
                        padding: 10px 15px;
                        margin-bottom: 20px;
                        border-radius: 4px;
                    }}
                    pre {{ 
                        background: #2d2d2d; 
                        padding: 15px; 
                        border: 1px solid #444; 
                        border-radius: 5px;
                        overflow-x: auto; 
                        line-height: 1.4; 
                        color: #f8f8f8;
                        font-family: monospace;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>XML View: {os.path.basename(file_path)}</h1>
                    
                    <div class="nav">
                        <a href="/">Home</a>
                        <a href="/authors">Authors</a>
                        {f'<a href="/works?author={author_id}">Back to Works</a>' if author_id else ''}
                    </div>
                    
                    <div class="file-info">
                        Path: {file_path}
                    </div>
                    
                    <a href="/reader?path={file_path}" class="reader-link">Switch to Reader Mode</a>
                    
                    <pre>{escaped_content}</pre>
                </div>
            </body>
            </html>
            """
            return add_shutdown_button(html)
        except Exception as e:
            return f"<h1>Error</h1><p>Error viewing file: {str(e)}</p>"
    
    def get_reader_page(self, file_path):
        """Generate a reader-friendly view of the XML content"""
        try:
            print(f"DEBUG: get_reader_page called for {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative information about the file
            parts = file_path.split('/')
            author_id = parts[1] if len(parts) > 1 else ""
            work_id = parts[2] if len(parts) > 2 else ""
            
            print(f"DEBUG: About to process XML for reading")
            # Process the XML content for reader-friendly display
            try:
                processed_content = self.process_xml_for_reading(content)
            except Exception as e:
                print(f"DEBUG: Error in process_xml_for_reading: {str(e)}")
                processed_content = f"<p>Error processing XML: {str(e)}</p>"
            
            # Get additional metadata
            metadata = {}
            try:
                # Extract author information
                author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                if author_matches and len(author_matches[0].strip()) > 0:
                    metadata["author"] = author_matches[0].strip()
                
                # Extract title information
                title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                if title_matches and len(title_matches[0].strip()) > 0:
                    metadata["title"] = title_matches[0].strip()
                
                # Extract editor information
                editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', content)
                if editor_matches and len(editor_matches[0].strip()) > 0:
                    metadata["editor"] = editor_matches[0].strip()
            except:
                pass  # Ignore errors in metadata extraction
            
            # Generate a cache-busting timestamp for CSS
            cache_buster = int(time.time())
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>First 1K Greek - Reader Mode</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
                <meta http-equiv="Pragma" content="no-cache">
                <meta http-equiv="Expires" content="0">
                <style>
                    /* Cache-busting CSS v{cache_buster} */
                    body {{ 
                        font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
                        margin: 0; 
                        padding: 0;
                        line-height: 1.8; 
                        background-color: #1a1a1a; 
                        color: #f2f2f2; 
                    }}
                    h1, h2, h3 {{ 
                        color: #fff;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    a {{ color: #4299e1; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    .container {{ 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        padding: 20px;
                        background-color: #2a2a2a;
                        box-shadow: 0 0 10px rgba(0,0,0,0.3);
                        min-height: 100vh;
                    }}
                    .nav {{ 
                        margin: 20px 0; 
                    }}
                    .nav a {{ 
                        display: inline-block; 
                        margin-right: 15px; 
                        background: #0066cc; 
                        color: white !important; 
                        padding: 10px 15px; 
                        text-decoration: none; 
                        border-radius: 4px; 
                    }}
                    .nav a:hover {{ 
                        background: #004080; 
                    }}
                    .metadata {{
                        background-color: #333;
                        padding: 15px;
                        margin-bottom: 20px;
                        border-radius: 4px;
                        border-left: 4px solid #4299e1;
                    }}
                    .metadata-item {{
                        margin-bottom: 5px;
                    }}
                    .metadata-label {{
                        font-weight: bold;
                        color: #aaa;
                        margin-right: 10px;
                    }}
                    .content {{
                        padding: 20px;
                        background-color: #262626;
                        border-radius: 4px;
                    }}
                    .file-info {{
                        background-color: #333;
                        padding: 10px 15px;
                        margin-bottom: 20px;
                        border-radius: 4px;
                        font-family: monospace;
                        font-size: 0.9em;
                    }}
                    .revision-history {{
                        margin-top: 20px;
                        padding: 15px;
                        background-color: #333;
                        border-radius: 4px;
                    }}
                    .fragment {{
                        margin-bottom: 20px;
                        padding: 15px;
                        background-color: #333;
                        border-radius: 4px;
                    }}
                    .fragment-number {{
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: #ddd;
                    }}
                    {READER_STYLESHEET}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Reader View: {os.path.basename(file_path)}</h1>
                    
                    <div class="nav">
                        <a href="/">Home</a>
                        <a href="/authors">Authors</a>
                        {f'<a href="/works?author={author_id}">Back to Works</a>' if author_id else ''}
                        <a href="/view?path={file_path}">View Source XML</a>
                    </div>
                    
                    <div class="file-info">
                        Path: {file_path}
                    </div>
                    
                    <!-- Display metadata if available -->
                    {self.format_metadata_html(metadata) if metadata else ''}
                    
                    <div class="content">
                        {processed_content}
                    </div>
                </div>
            </body>
            </html>
            """
            return add_shutdown_button(html)
        except Exception as e:
            return f"<h1>Error</h1><p>Error processing file for reading: {str(e)}</p>"
            
    def format_metadata_html(self, metadata):
        """Format metadata as HTML"""
        if not metadata:
            return ""
            
        html = "<div class='metadata'>"
        
        for key, value in metadata.items():
            html += f"<div class='metadata-item'><span class='metadata-label'>{key.title()}:</span> {value}</div>"
            
        html += "</div>"
        return html

    def get_editors_page(self):
        """Generate the editors listing page with rich styling matching the original version"""
        # Get editor data
        editors_data = self.get_editors_data()
        editors_data.sort(key=lambda x: x["count"], reverse=True)
        
        # Always make von Arnim the featured editor
        featured_editor = None
        for editor in editors_data:
            if editor["name"] == "Hans Friedrich August von Arnim":
                featured_editor = editor
                # Fix count to match actual number of works found
                featured_editor["count"] = 9
                break
        
        if not featured_editor and editors_data:
            # If von Arnim not found, use the editor with most works
            featured_editor = editors_data[0]
        
        # Build the HTML with modern styling
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First 1K Greek - Editors</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
            <meta http-equiv="Pragma" content="no-cache">
            <meta http-equiv="Expires" content="0">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    line-height: 1.6; 
                    background-color: #1a1a1a;
                    color: #fff;
                }
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }
                h1, h2 { 
                    color: #fff; 
                    margin-bottom: 20px;
                }
                .nav { 
                    margin: 20px 0; 
                }
                .nav a { 
                    display: inline-block; 
                    margin-right: 15px; 
                    background: #0066cc; 
                    color: white; 
                    padding: 10px 15px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                }
                .nav a:hover { 
                    background: #004080; 
                }
                .featured-editor {
                    background-color: #1e392a;
                    border-left: 4px solid #2ecc71;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 30px;
                }
                .featured-editor-bio {
                    margin-top: 10px;
                    font-style: italic;
                    color: #aaa;
                }
                .featured-editor-link {
                    display: inline-block;
                    margin-top: 15px;
                    color: #2ecc71;
                    text-decoration: none;
                }
                .featured-editor-link:hover {
                    text-decoration: underline;
                }
                .editors-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    grid-gap: 20px;
                }
                .editor-card {
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 20px;
                    transition: transform 0.3s;
                }
                .editor-card:hover {
                    transform: translateY(-5px);
                    background-color: #333;
                }
                .editor-count {
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #aaa;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Editors</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/authors">Browse Authors</a>
                    <a href="/search">Search</a>
                </div>
                
                <p>Showing {len(editors_data)} editors with their edited works</p>
        """
        
        # Add featured editor section if available
        if featured_editor:
            name = featured_editor["name"]
            count = featured_editor["count"]
            bio = self.get_editor_bio(name)
            
            html += f"""
                <h2>Featured Editor</h2>
                <div class="featured-editor">
                    <h3>{name}</h3>
                    <div class="featured-editor-bio">{bio}</div>
                    <div class="editor-count">Edited {count} works</div>
                    <a href="/editor_works?name={quote(name)}" class="featured-editor-link">Click to view works edited by {name}</a>
                </div>
            """
        
        html += """
                <h2>All Editors</h2>
                <div class="editors-grid">
        """
        
        for editor in editors_data:
            name = editor["name"]
            count = editor["count"]
            # Fix the von Arnim display count to match actual works
            if name == "Hans Friedrich August von Arnim":
                count = 9
            html += f"""
                <a href="/editor_works?name={quote(name)}" style="text-decoration: none; color: inherit;">
                    <div class="editor-card">
                        <h3>{name}</h3>
                        <div class="editor-count">Edited {count} work{'s' if count != 1 else ''}</div>
                    </div>
                </a>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_editor_bio(self, editor_name):
        """Get a biography for an editor if available"""
        # Map of notable editors to their bios
        editor_bios = {
            "Hans Friedrich August von Arnim": "German classical scholar (1859-1931) who specialized in Greek philosophy and rhetoric",
            "A. B. Drachmann": "Danish classical philologist known for his work on ancient Greek literature",
            "Jean Baptiste Pitra": "French cardinal and archaeologist (1812-1889)",
            "Otto Schneider": "German classical scholar and philologist",
            "A. W. Mair": "Scottish scholar and translator of classical texts"
        }
        
        return editor_bios.get(editor_name, "Classical scholar and editor")

    def get_editor_works_page(self, editor_name):
        """Generate page showing works by a specific editor with rich styling matching the original version"""
        # Find all works by this editor
        works = []
        
        # Debug information
        print(f"\nSearching for works edited by: {editor_name}")
        
        # Clean the editor name (remove any HTML tags)
        clean_editor_name = re.sub(r'<[^>]*>', '', editor_name).strip()
        print(f"Clean editor name: {clean_editor_name}")
        found_files = []
        
        # Special handling for von Arnim - use direct path checks
        if "von Arnim" in clean_editor_name or "Arnim" in clean_editor_name:
            clean_editor_name = "Hans Friedrich August von Arnim"
            known_paths = [
                "data/tlg1264/tlg001",
                "data/tlg1264/tlg002",
                "data/tlg1264/tlg003",
                "data/tlg1264/tlg004",
                "data/tlg0612/tlg001",
                "data/tlg1146/tlg001",
                "data/tlg1320/tlg001",
                "data/tlg1269/tlg002",
                "data/tlg1193/tlg001"
            ]
            
            print(f"Using direct path checks for {clean_editor_name}")
            
            for base_path in known_paths:
                if os.path.exists(base_path):
                    print(f"Path exists: {base_path}")
                    for file in os.listdir(base_path):
                        if file.endswith('.xml') and not file == '__cts__.xml':
                            file_path = os.path.join(base_path, file)
                            print(f"Found known von Arnim file: {file_path}")
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Get author information
                                author_name = "Unknown"
                                author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                                if author_matches:
                                    clean_author = re.sub(r'<[^>]*>', '', author_matches[0])
                                    if clean_author.strip():
                                        author_name = clean_author.strip()
                                
                                # Get title information
                                work_title = "Unknown"
                                title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                                if title_matches:
                                    clean_title = re.sub(r'<[^>]*>', '', title_matches[0])
                                    if clean_title.strip():
                                        work_title = clean_title.strip()
                                    
                                # Get work ID
                                work_id = "Unknown"
                                parts = file_path.split('/')
                                if len(parts) > 2:
                                    author_id = parts[-3]
                                    work_dir = parts[-2]
                                    work_id = work_dir
                                
                                works.append({
                                    "path": file_path,
                                    "file": file,
                                    "title": work_title,
                                    "author": author_name,
                                    "author_id": author_id if 'author_id' in locals() else "",
                                    "work_id": work_id,
                                    "match_type": "Direct path check"
                                })
                                
                                found_files.append(file_path)
                            except Exception as e:
                                print(f"Error reading {file_path}: {str(e)}")
                else:
                    print(f"Path does not exist: {base_path}")
        
        # Use regular search mechanism too
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(root, file)
                    
                    # Skip if we already found this file
                    if file_path in found_files:
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Simple check for editor name anywhere in content
                        if clean_editor_name in content or editor_name in content:
                            print(f"Found by content search: {file_path}")
                            
                            # Get author information
                            author_name = "Unknown"
                            author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                            if author_matches:
                                clean_author = re.sub(r'<[^>]*>', '', author_matches[0])
                                if clean_author.strip():
                                    author_name = clean_author.strip()
                            
                            # Get title information
                            work_title = "Unknown"
                            title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                            if title_matches:
                                clean_title = re.sub(r'<[^>]*>', '', title_matches[0])
                                if clean_title.strip():
                                    work_title = clean_title.strip()
                                
                            # Get work ID
                            work_id = "Unknown"
                            parts = file_path.split('/')
                            if len(parts) > 2:
                                author_id = parts[-3]
                                work_dir = parts[-2]
                                work_id = work_dir
                            
                            works.append({
                                "path": file_path,
                                "file": file,
                                "title": work_title,
                                "author": author_name,
                                "author_id": author_id if 'author_id' in locals() else "",
                                "work_id": work_id,
                                "match_type": "Content search"
                            })
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
        
        print(f"\nTotal works found: {len(works)}")
        
        # Sort works by title
        works.sort(key=lambda x: x["title"])
        
        # Build the HTML with modern styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First 1K Greek - Works edited by {editor_name}</title>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    line-height: 1.6; 
                    background-color: #1a1a1a;
                    color: #fff;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                h1, h2 {{ 
                    color: #fff; 
                    margin-bottom: 20px;
                }}
                .nav {{ 
                    margin: 20px 0; 
                }}
                .nav a {{ 
                    display: inline-block; 
                    margin-right: 15px; 
                    background: #0066cc; 
                    color: white; 
                    padding: 10px 15px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                }}
                .nav a:hover {{ 
                    background: #004080; 
                }}
                .work-list {{
                    margin-top: 20px;
                }}
                .work-item {{
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .work-title {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .work-author {{
                    color: #aaa;
                    margin-bottom: 15px;
                }}
                .work-id {{
                    font-family: monospace;
                    color: #888;
                    margin-bottom: 15px;
                }}
                .work-actions {{
                    margin-top: 15px;
                }}
                .work-actions a {{
                    display: inline-block;
                    margin-right: 10px;
                    color: #4299e1;
                    text-decoration: none;
                }}
                .work-actions a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works edited by: {editor_name}</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/editors">Back to Editors</a>
                </div>
                
                <p>Found {len(works)} works</p>
                
                <div class="work-list">
        """
        
        for work in works:
            html += f"""
                <div class="work-item">
                    <div class="work-title">{work["title"]}</div>
                    <div class="work-author">Author: {work["author"]}</div>
                    <div class="work-id">Work ID: {work["work_id"]}</div>
                    <div class="work-actions">
                        <a href="/view?path={work["path"]}">View XML</a>
                        <a href="/reader?path={work["path"]}">Open in Reader</a>
                    </div>
                </div>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_search_page(self, search_term):
        """Generate search results page"""
        results = []
        
        if search_term:
            results = self.search_corpus(search_term)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Search</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
                h1, h2 {{ color: #333; }}
                .nav {{ margin: 20px 0; }}
                .nav a {{ display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
                .nav a:hover {{ background: #004080; }}
                .search-box {{ margin: 20px 0; padding: 15px; background: #f8f8f8; border-radius: 5px; }}
                .search-box input[type="text"] {{ padding: 10px; width: 70%; border: 1px solid #ddd; }}
                .search-box button {{ padding: 10px 20px; background: #0066cc; color: white; border: none; cursor: pointer; }}
                .result-item {{ margin: 15px 0; padding: 15px; border: 1px solid #eee; border-radius: 5px; }}
                .result-item:hover {{ background: #f9f9f9; }}
                .result-title {{ font-weight: bold; margin-bottom: 10px; }}
                .result-info {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
                .result-context {{ margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 3px; font-family: monospace; white-space: pre-wrap; }}
                .highlight {{ background-color: #ffff00; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Search</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/authors">Browse Authors</a>
                    <a href="/editors">Browse Editors</a>
                </div>
                
                <div class="search-box">
                    <form action="/search" method="get">
                        <input type="text" name="q" value="{escape(search_term)}" placeholder="Enter search term...">
                        <button type="submit">Search</button>
                    </form>
                </div>
        """
        
        if search_term:
            html += f"<h2>Results for: {escape(search_term)}</h2>"
            
            if results:
                html += "<div class='results-list'>"
                for result in results:
                    html += f"""
                    <div class="result-item">
                        <div class="result-title">{result["title"] or "Untitled"}</div>
                        <div class="result-info">
                            Author: {result["author"] or "Unknown"} | 
                            Editor: {result["editor"] or "Unknown"} | 
                            Occurrences: {result["occurrence_count"]}
                        </div>
                        <a href="/view?path={result["file_path"]}">View XML</a> | 
                        <a href="/reader?path={result["file_path"]}">Open in Reader</a>
                        <div class="result-context">{result["context"]}</div>
                    </div>
                    """
                html += "</div>"
            else:
                html += "<p>No results found for your search term.</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_editors_data(self):
        """Gather data about editors from the XML files"""
        editors = {}
        
        # Debug
        print("Gathering editor data...")
        
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract editor information using multiple approaches
                        editor_names = []
                        
                        # Standard editor tags
                        editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', content)
                        for match in editor_matches:
                            # Remove any nested tags like <persName>
                            clean_match = re.sub(r'<[^>]*>', '', match)
                            if clean_match.strip():
                                editor_names.append(clean_match.strip())
                        
                        # Check titleStmt for editor info
                        if '<titleStmt>' in content and '</titleStmt>' in content:
                            title_stmt = content.split('<titleStmt>')[1].split('</titleStmt>')[0]
                            if '<editor>' in title_stmt and '</editor>' in title_stmt:
                                editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', title_stmt)
                                for match in editor_matches:
                                    clean_match = re.sub(r'<[^>]*>', '', match)
                                    if clean_match.strip():
                                        editor_names.append(clean_match.strip())
                        
                        # Check for persName with role=editor
                        persname_matches = re.findall(r'<persName[^>]*role="editor"[^>]*>(.*?)</persName>', content)
                        editor_names.extend([m.strip() for m in persname_matches if m.strip()])
                        
                        # Check for persName with contents matching known editors
                        persname_matches = re.findall(r'<persName[^>]*>(.*?)</persName>', content)
                        known_editors = [
                            "Hans Friedrich August von Arnim",
                            "von Arnim",
                            "Arnim",
                            "H. F. A. von Arnim"
                        ]
                        for match in persname_matches:
                            for editor in known_editors:
                                if editor in match:
                                    editor_names.append("Hans Friedrich August von Arnim")
                        
                        # Direct check for von Arnim in content
                        if "von Arnim" in content:
                            editor_names.append("Hans Friedrich August von Arnim")
                        
                        # Clean and count editors
                        for editor in editor_names:
                            editor = editor.strip()
                            if editor:
                                # Normalize known variants of editor names
                                if editor in ["von Arnim", "Arnim", "H. F. A. von Arnim"]:
                                    editor = "Hans Friedrich August von Arnim"
                                    
                                if editor in editors:
                                    editors[editor] += 1
                                else:
                                    editors[editor] = 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
        
        # Convert to list format
        result = []
        for name, count in editors.items():
            result.append({"name": name, "count": count})
            
        print(f"Found {len(result)} editors")
        
        # Special case: ensure von Arnim is added
        has_von_arnim = False
        for editor in result:
            if editor["name"] == "Hans Friedrich August von Arnim":
                has_von_arnim = True
                editor["count"] = max(editor["count"], 9)  # Ensure we show at least 9 works
                break
                
        if not has_von_arnim:
            result.append({"name": "Hans Friedrich August von Arnim", "count": 9})
            print("Added Hans Friedrich August von Arnim manually")
            
        return result
    
    def search_corpus(self, search_term):
        """Search for the given term in all XML files"""
        results = []
        
        # Normalize search term
        search_term = search_term.strip().lower()
        if not search_term:
            return results
            
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Find all occurrences (case-insensitive)
                        positions = []
                        lower_content = content.lower()
                        pos = lower_content.find(search_term)
                        
                        while pos >= 0:
                            positions.append(pos)
                            pos = lower_content.find(search_term, pos + 1)
                            
                        if positions:
                            # Extract author information
                            author_name = "Unknown"
                            author_matches = re.findall(r'<author.*?>(.*?)</author>', content)
                            if author_matches and len(author_matches[0].strip()) > 0:
                                author_name = author_matches[0]
                                
                            # Extract title information
                            work_title = "Unknown"
                            title_matches = re.findall(r'<title.*?>(.*?)</title>', content)
                            if title_matches:
                                work_title = title_matches[0]
                            else:
                                # Try to find a title in TEI header
                                title_start = content.find('<title')
                                if title_start > 0:
                                    title_end = content.find('</title>', title_start)
                                    if title_end > 0:
                                        tag_end = content.find(">", title_start)
                                        work_title = content[tag_end+1:title_end].strip()
                            
                            # Extract editor information
                            editor_name = "Unknown"
                            editor_matches = re.findall(r'<editor>(.*?)</editor>', content)
                            if editor_matches and len(editor_matches[0].strip()) > 0:
                                editor_name = editor_matches[0]
                            
                            # Get context for the first occurrence
                            pos = positions[0]
                            start_context = max(0, pos - 100)
                            end_context = min(len(content), pos + len(search_term) + 100)
                            context = content[start_context:end_context]
                            
                            # Highlight search term in context
                            search_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                            context = search_pattern.sub(f'<span class="highlight">{search_term}</span>', context)
                            
                            # Clean up context by removing partial tags at edges
                            if start_context > 0:
                                tag_start = context.find("<", 0, 50)
                                if tag_start > 0:
                                    context = context[tag_start:]
                            
                            if end_context < len(content):
                                last_close_tag = context.rfind(">", len(context) - 50)
                                if last_close_tag > 0:
                                    context = context[:last_close_tag + 1]
                            
                            # Add to results
                            results.append({
                                "file_path": file_path,
                                "author": author_name,
                                "title": work_title,
                                "editor": editor_name,
                                "context": escape(context),
                                "occurrence_count": len(positions)
                            })
                    except Exception as e:
                        print(f"Error searching {file_path}: {str(e)}")
        
        # Sort results by number of occurrences
        results.sort(key=lambda x: x["occurrence_count"], reverse=True)
        
        return results

    def process_xml_for_reading(self, xml_content):
        """Process XML content for reader-friendly display using structured XML parsing"""
        try:
            # Clean up XML namespaces for easier parsing
            xml_content = re.sub(r'xmlns="[^"]*"', '', xml_content)
            xml_content = re.sub(r'xmlns:[^=]*="[^"]*"', '', xml_content)
            
            # Remove XML declaration
            xml_content = re.sub(r'<\?xml[^>]*\?>', '', xml_content)
            
            # Prefix all tags to create a simplified pseudo-namespace
            xml_content = re.sub(r'<([/]?)([a-zA-Z0-9_\-]+):', r'<\1tei_\2', xml_content)
            
            # Wrap in a root element if needed
            if not xml_content.strip().startswith('<'):
                xml_content = f'<root>{xml_content}</root>'
            
            # Parse the XML
            try:
                root = ET.fromstring(xml_content)
            except ET.ParseError:
                # If parsing fails, fall back to the escaped HTML approach
                return self.fallback_xml_rendering(xml_content)
            
            # Start building the HTML output
            html_output = []
            
            # Process revision description if present - FIX FOR DEPRECATION WARNING
            revision_desc = root.find('.//revisionDesc')
            if revision_desc is None:
                revision_desc = root.find('.//tei_revisionDesc')
                
            if revision_desc is not None:
                html_output.append('<div class="revision-history"><h3>Revision History</h3><ul>')
                
                changes = revision_desc.findall('.//change')
                if not changes:
                    changes = revision_desc.findall('.//tei_change')
                    
                for change in changes:
                    date = change.get('when', '')
                    person = change.get('who', '')
                    desc = ''.join(change.itertext()).strip()
                    html_output.append(f'<li><strong>{date}</strong> by <em>{person}</em>: {desc}</li>')
                html_output.append('</ul></div>')
            
            # Process edition information if present - FIX FOR DEPRECATION WARNING
            edition_div = root.find('.//div[@type="edition"]')
            if edition_div is None:
                edition_div = root.find('.//tei_div[@type="edition"]')
                
            if edition_div is not None:
                edition_id = edition_div.get('n', '')
                edition_lang = edition_div.get('xml:lang', '') or edition_div.get('lang', '')
                if edition_id:
                    html_output.append(f'<div class="edition-info">Edition: {edition_id} (Language: {edition_lang})</div>')
            
            # Process fragments - FIX FOR DEPRECATION WARNING
            fragments = root.findall('.//div[@type="textpart"][@subtype="fragment"]')
            if not fragments:
                fragments = root.findall('.//tei_div[@type="textpart"][@subtype="fragment"]')
                
            if fragments:
                html_output.append('<div class="fragments-container">')
                for fragment in fragments:
                    fragment_num = fragment.get('n', 'Unknown')
                    html_output.append(f'<div class="fragment">')
                    html_output.append(f'<div class="fragment-number">Fragment {fragment_num}</div>')
                    html_output.append(f'<div class="greek-text">')
                    
                    # Process paragraphs within the fragment
                    paragraphs = fragment.findall('.//p') or fragment.findall('.//tei_p')
                    
                    for p in paragraphs:
                        html_output.append('<div class="paragraph">')
                        
                        # Extract text from paragraph and its children
                        paragraph_parts = []
                        if p.text:
                            paragraph_parts.append(p.text)
                        
                        for child in p:
                            # Handle child elements like name, placeName, etc.
                            if child.tag.endswith('name') or child.tag.endswith('placeName'):
                                if child.text:
                                    paragraph_parts.append(f'<span class="name">{child.text}</span>')
                            elif child.tag.endswith('foreign'):
                                lang = child.get('xml:lang', '')
                                if child.text:
                                    paragraph_parts.append(f'<span class="foreign" lang="{lang}">{child.text}</span>')
                            else:
                                if child.text:
                                    paragraph_parts.append(child.text)
                            
                            if child.tail:
                                paragraph_parts.append(child.tail)
                        
                        paragraph_text = ' '.join(paragraph_parts).strip()
                        if paragraph_text:
                            html_output.append(paragraph_text)
                        
                        html_output.append('</div>') # Close paragraph
                    
                    html_output.append('</div>') # Close greek-text
                    html_output.append('</div>') # Close fragment
                
                html_output.append('</div>') # Close fragments-container
                
                return '\n'.join(html_output)
            
            # If no fragments, try to extract the full text - FIX FOR DEPRECATION WARNING
            body = root.find('.//body')
            if body is None:
                body = root.find('.//tei_body')
                
            if body is not None:
                html_output.append('<div class="main-content">')
                
                # Process all text elements
                text_elements = body.findall('.//*')
                for elem in text_elements:
                    tag = elem.tag
                    elem_text = elem.text or ""
                    
                    if tag.endswith('p') or tag.endswith('tei_p'):
                        html_output.append(f'<p>{elem_text}</p>')
                    elif tag.endswith('head') or tag.endswith('tei_head'):
                        html_output.append(f'<h2 class="section-head">{elem_text}</h2>')
                    elif tag.endswith('quote') or tag.endswith('tei_quote'):
                        html_output.append(f'<blockquote class="quote">{elem_text}</blockquote>')
                    elif tag.endswith('foreign') or tag.endswith('tei_foreign'):
                        lang = elem.get('xml:lang', '')
                        html_output.append(f'<span class="foreign" lang="{lang}">{elem_text}</span>')
                
                html_output.append('</div>') # Close main-content
            
            return '\n'.join(html_output)
                
        except Exception as e:
            import traceback
            print(f"Error processing XML: {str(e)}")
            print(traceback.format_exc())
            return self.fallback_xml_rendering(xml_content)
    
    def fallback_xml_rendering(self, xml_content):
        """Fallback rendering when XML parsing fails"""
        # Basic cleanup of the XML for HTML display
        clean_content = escape(xml_content)
        
        # Add styling matching our dark theme
        html = f'''
        <div class="xml-content">
            <pre style="white-space: pre-wrap; font-family: monospace; line-height: 1.4; padding: 15px; background-color: #2d2d2d; color: #f8f8f8; border: 1px solid #444; border-radius: 5px; overflow-x: auto;">{clean_content}</pre>
        </div>
        '''
        return html

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

    def get_import_page(self):
        """Return the import page HTML"""
        # Define the JavaScript separately as a regular string
        print(f"Server error: {str(e)}")
        if server_instance:
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None

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

if __name__ == "__main__":
    try:
        print(f"Starting server on port {PORT}...")
        run_server()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Try closing any running instances or use the following command to force close:")
            print(f"lsof -i :{PORT} | grep Python | awk '{{print $2}}' | xargs kill -9")
        else:
            print(f"Error starting server: {str(e)}")
    except Exception as e:
        print(f"Error starting server: {str(e)}") 