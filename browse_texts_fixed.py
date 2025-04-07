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
import signal
import xml.etree.ElementTree as ET
import urllib.parse
import argparse
import logging
import traceback
from urllib.error import URLError, HTTPError
from html import escape

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='First1KGreek Browser')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

# Global variable to store server instance
server_instance = None

# Constants
# Only define args when run as main module
PORT = 8000  # Default port
HOST = "localhost"
SHUTDOWN_PATH = "/shutdown"
DEBUG = False  # Default debug flag

# Load author data
try:
    with open('authors_data.json', 'r', encoding='utf-8') as f:
        AUTHORS_DATA = json.load(f)
    logger.info(f"Loaded author data with {len(AUTHORS_DATA)} entries")
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Error loading author data: {e}")
    AUTHORS_DATA = {}

# Print version info when starting
logger.info("Starting First1KGreek Browser - Fixed Version 1.2.0")
logger.info("With dark theme and improved editor detection")

# Stylesheets moved to external files in static/css
# For reference, keeping the original definitions commented out

# Reader mode stylesheet
"""
READER_STYLESHEET = '''
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
'''
"""

# Main stylesheet
"""
MAIN_STYLESHEET = '''
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
'''
"""

# Authors table stylesheet
"""
AUTHORS_TABLE_STYLESHEET = '''
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
'''
"""

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port)) == 0
        logger.debug(f"Port {port} is {'in use' if result else 'available'}")
        return result

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    logger.debug(f"Searching for available port starting from {start_port}")
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            logger.debug(f"Found available port: {port}")
            return port
    logger.warning(f"No available ports found in range {start_port}-{start_port+max_attempts-1}")
    return start_port

class PageGenerator:
    """Class to handle HTML page generation"""
    
    def __init__(self):
        """Initialize with common data"""
        self.authors_data = {}
        self.user_prefs = {'favorites': [], 'archived': [], 'deleted': []}
        
        # Load data with proper error handling
        self.load_data()
    
    def load_data(self):
        """Load data with error handling"""
        # Load authors data
        try:
            with open('authors_data.json', 'r', encoding='utf-8') as f:
                self.authors_data = json.load(f)
            logger.info(f"PageGenerator loaded author data with {len(self.authors_data)} entries")
        except FileNotFoundError:
            logger.error("authors_data.json not found - using empty dictionary")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing authors_data.json: {str(e)}")
            logger.error(f"At line {e.lineno}, column {e.colno}: {e.msg}")
        except Exception as e:
            logger.error(f"Unexpected error loading authors_data.json: {str(e)}")
            logger.error(traceback.format_exc())
            
        # Load user preferences    
        try:
            with open('user_preferences.json', 'r', encoding='utf-8') as f:
                self.user_prefs = json.load(f)
            logger.info(f"PageGenerator loaded user preferences with {sum(len(v) for v in self.user_prefs.values())} total entries")
        except FileNotFoundError:
            logger.info("user_preferences.json not found - using default preferences")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing user_preferences.json: {str(e)}")
            logger.error(f"At line {e.lineno}, column {e.colno}: {e.msg}")
        except Exception as e:
            logger.error(f"Unexpected error loading user_preferences.json: {str(e)}")
            logger.error(traceback.format_exc())
    
    def reload_data(self):
        """Reload data from disk to ensure we have the latest version"""
        logger.debug("Reloading data from disk")
        data_reload_start = time.time()
        self.load_data()
        logger.debug(f"Data reload completed in {time.time() - data_reload_start:.3f}s")
    
    def get_home_page(self):
        """Generate the home page"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1KGreek Browser</title>
            <link rel="stylesheet" href="/static/css/main.css">
        </head>
        <body>
            <div class="container">
                <h1>First1KGreek Browser</h1>
                <p>Welcome to the First1KGreek Browser. This tool allows you to browse, search, and view texts from the First 1000 Years of Greek project.</p>
                
                <h2>Navigation</h2>
                <ul>
                    <li><a href="/authors">Browse Authors</a></li>
                    <li><a href="/editors">Browse Editors</a></li>
                    <li><a href="/search">Search Texts</a></li>
                </ul>
                
                <p><small>Version 1.2.0 (with dark theme) - Last updated: 2025-03-07</small></p>
            </div>
        </body>
        </html>
        '''
        return html
    
    def get_authors_table_page(self):
        """Generate the authors table page"""
        # Reload data to ensure we have the latest values
        self.reload_data()
        
        # HTML template with JavaScript and CSS includes
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authors Table</title>
            <link rel="stylesheet" href="/static/css/main.css">
            <link rel="stylesheet" href="/static/css/authors-table.css">
            <script id="user-prefs" type="application/json">
                {json.dumps(self.user_prefs)}
            </script>
            <script src="/static/js/authors_table.js?v={int(time.time())}"></script>
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
                            <th data-sort="type">Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                '''

        # Add table rows
        for author_id, author_data in self.authors_data.items():
            if author_id in (self.user_prefs.get('deleted', []) or []):
                continue

            author_name = author_data.get('name', '')
            century_value = author_data.get('century', '')
            
            # Format century value - negative for BCE, positive for CE
            if isinstance(century_value, int):
                if century_value < 0:
                    century = f"{abs(century_value)} BCE"
                else:
                    century = f"{century_value} CE"
            else:
                century = str(century_value)
                
            type_value = author_data.get('type', author_data.get('allegiance', ''))
            works_count = len(self.get_author_works(author_id))

            # Add icons for favorite/archived status
            name_prefix = ''
            if author_id in (self.user_prefs.get('favorites', []) or []):
                name_prefix += '<span class="favorites-star">★</span> '
            if author_id in (self.user_prefs.get('archived', []) or []):
                name_prefix += '<span class="archived-icon">📦</span> '

            html += f'''
                        <tr data-id="{author_id}">
                            <td data-column="author_name">
                                {name_prefix}{author_name}
                                <div class="author-type">{type_value}</div>
                            </td>
                            <td data-column="century">{century}</td>
                            <td data-column="works">{works_count}</td>
                            <td data-column="type">{type_value}</td>
                            <td class="actions">
                                <button class="favorite-btn" data-author-id="{author_id}">
                                    {'Unfavorite' if author_id in (self.user_prefs.get('favorites', []) or []) else 'Favorite'}
                                </button>
                                <button class="archive-btn" data-author-id="{author_id}">
                                    {'Unarchive' if author_id in (self.user_prefs.get('archived', []) or []) else 'Archive'}
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
                        <input type="text" id="edit-century" placeholder="Enter century (e.g., -5 for 5 BCE, 2 for 2 CE)">
                        <p class="modal-help">Use negative values for BCE (e.g., -5 for 5 BCE) and positive values for CE (e.g., 2 for 2 CE)</p>
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
                    # Get more information about the work
                    work_info = {
                        'id': item,
                        'title': item,  # Default to directory name
                        'files': []
                    }
                    
                    # Check if there's any metadata available
                    cts_file = os.path.join(work_path, '__cts__.xml')
                    if os.path.exists(cts_file):
                        try:
                            with open(cts_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                                if title_match:
                                    work_info['title'] = title_match.group(1).strip()
                        except Exception as e:
                            logger.error(f"Error reading metadata for {work_path}: {str(e)}")
                    
                    # Get file list
                    try:
                        for file in os.listdir(work_path):
                            file_path = os.path.join(work_path, file)
                            if os.path.isfile(file_path) and not file.startswith('__'):
                                work_info['files'].append({
                                    'name': file,
                                    'type': file.split('.')[-1] if '.' in file else 'unknown'
                                })
                    except Exception as e:
                        logger.error(f"Error listing files for {work_path}: {str(e)}")
                    
                    works.append(work_info)
        
        return works
    
    def get_works_page(self, query_string):
        """Generate the works page"""
        # Parse query parameters
        query_params = urllib.parse.parse_qs(query_string)
        author_id = query_params.get('author_id', [''])[0]
        
        if not author_id:
            return self.get_error_page("Missing author_id parameter")
        
        # Get author data
        author_data = self.authors_data.get(author_id, {})
        author_name = author_data.get('name', 'Unknown Author')
        
        # Get works for this author
        works = self.get_author_works(author_id)
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Works by {author_name}</title>
            <link rel="stylesheet" href="/static/css/main.css">
            <style>
                .work-item {{
                    margin-bottom: 15px;
                    padding: 15px;
                    background-color: #333;
                    border-radius: 5px;
                }}
                
                .work-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works by {author_name}</h1>
                <p><a href="/authors">&laquo; Back to Authors</a></p>
                
                <div class="works-list">
        '''
        
        # Add each work as a list item
        if works:
            for work_info in works:
                html += f'''
                    <div class="work-item">
                        <div class="work-title">{work_info['title']}</div>
                        <a href="/view?author_id={author_id}&work_id={work_info['id']}">View Content</a>
                    </div>
                '''
        else:
            html += '<p>No works found for this author.</p>'
        
        # Close HTML structure
        html += '''
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def get_view_page(self, query_string):
        """Generate the view page"""
        # Parse query parameters
        query_params = urllib.parse.parse_qs(query_string)
        author_id = query_params.get('author_id', [''])[0]
        work_id = query_params.get('work_id', [''])[0]
        view_mode = query_params.get('view_mode', ['readable'])[0]
        
        if not author_id or not work_id:
            return self.get_error_page("Missing author_id or work_id parameter")
        
        # Get author data
        author_data = self.authors_data.get(author_id, {})
        author_name = author_data.get('name', 'Unknown Author')
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{work_id} by {author_name}</title>
            <link rel="stylesheet" href="/static/css/reader.css">
            <style>
                .view-toggle {{
                    margin: 10px 0;
                    text-align: right;
                }}
                .view-toggle a {{
                    display: inline-block;
                    padding: 8px 16px;
                    background-color: #2d3748;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-left: 10px;
                }}
                .view-toggle a.active {{
                    background-color: #3182ce;
                }}
                .view-toggle a:hover {{
                    background-color: #4a5568;
                }}
                pre.xml-view {{
                    background-color: #222;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    font-family: monospace;
                    line-height: 1.4;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{work_id}</h1>
                <p>Author: {author_name}</p>
                <p><a href="/works?author_id={author_id}">&laquo; Back to Works</a></p>
                
                <div class="view-toggle">
                    <a href="/view?author_id={author_id}&work_id={work_id}&view_mode=readable" 
                       class="{'' if view_mode == 'readable' else 'active'}">Human Readable</a>
                    <a href="/view?author_id={author_id}&work_id={work_id}&view_mode=raw" 
                       class="{'' if view_mode == 'raw' else 'active'}">Raw XML</a>
                </div>
                
                <div class="work-content">
                    {self.get_work_content(author_id, work_id, view_mode)}
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def get_work_content(self, author_id, work_id, view_mode='readable'):
        """Get the content of a work"""
        work_path = os.path.join('data', author_id, work_id)
        content_start_time = time.time()
        content = "<p>This work contains multiple files. Please select from the list below:</p><ul>"
        
        try:
            # Check if the work directory exists
            if not os.path.exists(work_path):
                logger.warning(f"Work directory not found: {work_path}")
                return f"<p>Error: Work directory for {work_id} not found.</p>"
                
            # List all files in the work directory
            try:
                files = os.listdir(work_path)
            except PermissionError:
                logger.error(f"Permission denied when accessing directory: {work_path}")
                return f"<p>Error: Permission denied when accessing work directory.</p>"
            except Exception as e:
                logger.error(f"Error listing directory {work_path}: {str(e)}")
                logger.error(traceback.format_exc())
                return f"<p>Error accessing work files: {str(e)}</p>"
            
            if not files:
                logger.info(f"No files found in work directory: {work_path}")
                content = "<p>No content files found for this work.</p>"
            else:
                xml_files = 0
                text_files = 0
                
                for file in files:
                    file_path = os.path.join(work_path, file)
                    
                    # Skip directories and non-content files
                    if os.path.isdir(file_path) or not (file.endswith('.xml') or file.endswith('.txt')):
                        continue
                        
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > 5 * 1024 * 1024:  # 5MB
                            logger.warning(f"Skipping large file: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
                            content += f"<li><h3>{file}</h3><p>File too large to display ({file_size / 1024 / 1024:.2f} MB)</p></li>"
                            continue
                            
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            if file.endswith('.xml'):
                                if view_mode == 'raw':
                                    # For raw XML view, just escape and display in a pre tag
                                    content += f"<li><h3>{file} (Raw XML)</h3><pre class='xml-view'>{escape(file_content)}</pre></li>"
                                else:
                                    # Basic XML handling for readable view - just escape and display for now
                                    content += f"<li><h3>{file}</h3><pre>{escape(file_content)}</pre></li>"
                                xml_files += 1
                            elif file.endswith('.txt'):
                                text_files += 1
                                content += f"<li><h3>{file}</h3><pre>{file_content}</pre></li>"
                    except UnicodeDecodeError:
                        logger.error(f"Unicode decode error for file: {file_path}")
                        content += f"<li><h3>{file}</h3><p>Error: This file contains non-UTF-8 characters and cannot be displayed.</p></li>"
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {str(e)}")
                        logger.error(traceback.format_exc())
                        content += f"<li><h3>{file}</h3><p>Error reading file: {str(e)}</p></li>"
                
                # Add summary
                logger.info(f"Processed {xml_files} XML files and {text_files} text files for {author_id}/{work_id}")
        except Exception as e:
            logger.error(f"Error accessing work content for {author_id}/{work_id}: {str(e)}")
            logger.error(traceback.format_exc())
            content = f"<p>Error accessing work content: {str(e)}</p>"
        finally:
            content_time = time.time() - content_start_time
            logger.debug(f"get_work_content({author_id}, {work_id}) took {content_time:.3f}s")
            
        return content
    
    def get_editors_page(self):
        """Generate the editors page"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Editors</title>
            <link rel="stylesheet" href="/static/css/main.css">
        </head>
        <body>
            <div class="container">
                <h1>Editors</h1>
                <p><a href="/">&laquo; Home</a></p>
                
                <p>This page will list all editors of the texts in the corpus.</p>
                <p>Feature coming soon!</p>
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def get_search_page(self):
        """Generate the search page"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Texts</title>
            <link rel="stylesheet" href="/static/css/main.css">
            <style>
                .search-form {
                    margin: 20px 0;
                    padding: 20px;
                    background-color: #333;
                    border-radius: 5px;
                }
                
                .search-form input[type="text"] {
                    padding: 10px;
                    width: 70%;
                    background-color: #444;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                
                .search-form button {
                    padding: 10px 20px;
                    background-color: #3182ce;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: 10px;
                }
                
                .search-form button:hover {
                    background-color: #2c5282;
                }
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
        '''
        
        return html
    
    def get_error_page(self, error_message):
        """Generate an error page"""
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <link rel="stylesheet" href="/static/css/main.css">
            <style>
                .error-container {{
                    background-color: #422;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                
                .error-message {{
                    color: #f88;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Error</h1>
                
                <div class="error-container">
                    <p class="error-message">{error_message}</p>
                </div>
                
                <p><a href="/">&laquo; Back to Home</a></p>
            </div>
        </body>
        </html>
        '''
        
        return html

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP server handler for browsing and viewing texts"""
    
    def __init__(self, *args, **kwargs):
        self.page_generator = PageGenerator()
        self.request_start_time = None
        super().__init__(*args, **kwargs)
    
    def get_user_prefs(self):
        """Load user preferences from file."""
        try:
            logger.debug("Loading user preferences from file")
            with open('user_preferences.json', 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                logger.debug(f"Loaded user preferences with {sum(len(v) for v in prefs.values() if isinstance(v, list))} entries")
                return prefs
        except FileNotFoundError:
            logger.warning("user_preferences.json not found - using empty defaults")
            return {'favorites': [], 'archived': [], 'deleted': []}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing user_preferences.json: {str(e)}")
            logger.error(f"At line {e.lineno}, column {e.colno}: {e.msg}")
            return {'favorites': [], 'archived': [], 'deleted': []}
        except Exception as e:
            logger.error(f"Unexpected error loading user_preferences.json: {str(e)}")
            logger.error(traceback.format_exc())
            return {'favorites': [], 'archived': [], 'deleted': []}
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def do_GET(self):
        """Handle GET requests"""
        self.request_start_time = time.time()
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            logger.info(f"GET request for {self.path} from {self.client_address}")

            # Serve static files
            if path.startswith('/static/'):
                logger.debug(f"Serving static file: {path}")
                self.serve_static_file(path)
                return

            # Handle other routes
            if path == '/':
                logger.debug("Serving home page")
                self.send_html_response(self.page_generator.get_home_page())
            elif path == '/authors':
                logger.debug("Serving authors table page")
                self.send_html_response(self.page_generator.get_authors_table_page())
            elif path == '/works':
                author_id = urllib.parse.parse_qs(parsed_path.query).get('author_id', [''])[0]
                logger.debug(f"Serving works page for author_id: {author_id}")
                self.send_html_response(self.page_generator.get_works_page(parsed_path.query))
            elif path == '/view':
                params = urllib.parse.parse_qs(parsed_path.query)
                author_id = params.get('author_id', [''])[0]
                work_id = params.get('work_id', [''])[0]
                view_mode = params.get('view_mode', ['readable'])[0]
                logger.debug(f"Serving view page for author_id: {author_id}, work_id: {work_id}, view_mode: {view_mode}")
                self.send_html_response(self.page_generator.get_view_page(parsed_path.query))
            elif path == '/get_author_works':
                author_id = urllib.parse.parse_qs(parsed_path.query).get('author_id', [''])[0]
                if author_id:
                    logger.debug(f"Getting works for author_id: {author_id}")
                    try:
                        works = self.page_generator.get_author_works(author_id)
                        logger.info(f"Found {len(works)} works for author {author_id}")
                        self.send_json_response(works)
                    except Exception as e:
                        logger.error(f"Error getting works for {author_id}: {str(e)}")
                        logger.error(traceback.format_exc())
                        self.send_error(500, f"Error retrieving works: {str(e)}")
                else:
                    logger.warning("Missing author_id parameter")
                    self.send_error(400, "Missing author_id parameter")
            elif path == '/editors':
                logger.debug("Serving editors page")
                self.send_html_response(self.page_generator.get_editors_page())
            elif path == '/search':
                logger.debug("Serving search page")
                self.send_html_response(self.page_generator.get_search_page())
            else:
                logger.warning(f"404 Not Found: {path}")
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling GET request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
        finally:
            if self.request_start_time:
                request_time = time.time() - self.request_start_time
                logger.debug(f"Request processed in {request_time:.4f} seconds")

    def do_POST(self):
        """Handle POST requests"""
        self.request_start_time = time.time()
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            logger.info(f"POST request for {self.path} from {self.client_address}")

            # Parse form data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))
            logger.debug(f"POST data: {post_data}")

            if path == '/update_preference':
                logger.debug("Handling update_preference request")
                self.handle_update_preference(post_data)
            elif path == '/update_work_preference':
                logger.debug("Handling update_work_preference request")
                self.handle_update_work_preference(post_data)
            elif path == '/update_century':
                logger.debug("Handling update_century request")
                self.handle_update_century(post_data)
            else:
                logger.warning(f"404 Not Found: {path}")
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
        finally:
            if self.request_start_time:
                request_time = time.time() - self.request_start_time
                logger.debug(f"Request processed in {request_time:.4f} seconds")

    def handle_update_preference(self, post_data):
        """Handle updating user preferences"""
        author_id = post_data.get('author_id', [''])[0]
        pref_type = post_data.get('pref_type', [''])[0]
        value = post_data.get('value', ['false'])[0].lower() == 'true'

        if not author_id or not pref_type:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current preferences using the method
            prefs = self.get_user_prefs()

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
            logger.error(f"Error updating preferences: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Error updating preferences: {str(e)}")

    def handle_update_work_preference(self, post_data):
        """Handle updating user preferences for works"""
        author_id = post_data.get('author_id', [''])[0]
        work_id = post_data.get('work_id', [''])[0]
        pref_type = post_data.get('pref_type', [''])[0]
        value = post_data.get('value', ['false'])[0].lower() == 'true'

        if not author_id or not work_id or not pref_type:
            self.send_error(400, "Missing required parameters")
            return

        try:
            # Load current preferences using the method
            prefs = self.get_user_prefs()

            # Ensure work preference keys exist
            for key in ['work_favorites', 'work_archived', 'work_deleted']:
                if key not in prefs:
                    prefs[key] = []

            # Create a unique work identifier
            work_identifier = f"{author_id}/{work_id}"
            
            # Determine which preference list to update
            work_pref_key = f"work_{pref_type}"
            
            # Update preference
            if value and work_identifier not in prefs[work_pref_key]:
                prefs[work_pref_key].append(work_identifier)
            elif not value and work_identifier in prefs[work_pref_key]:
                prefs[work_pref_key].remove(work_identifier)

            # Save updated preferences
            with open('user_preferences.json', 'w') as f:
                json.dump(prefs, f, indent=2)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())

        except Exception as e:
            logger.error(f"Error updating work preferences: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Error updating work preferences: {str(e)}")

    def handle_update_century(self, post_data):
        """Handle updating author century"""
        global AUTHORS_DATA  # Directly reference the global AUTHORS_DATA
        author_id = post_data.get('author_id', [''])[0]
        century_input = post_data.get('century', [''])[0]
        
        logger.info(f"Century update request: author_id='{author_id}', century_input='{century_input}'")

        if not author_id or not century_input:
            logger.warning(f"Missing required parameters: author_id={author_id}, century_input={century_input}")
            self.send_error(400, "Missing required parameters")
            return
            
        # Process century input - convert to integer
        try:
            # Check if the input contains "BCE" or "CE" and convert accordingly
            if "BCE" in century_input.upper():
                # Remove "BCE" and convert to negative integer
                century_value = -int(century_input.upper().replace("BCE", "").strip())
            elif "CE" in century_input.upper():
                # Remove "CE" and convert to positive integer
                century_value = int(century_input.upper().replace("CE", "").strip())
            else:
                # Try to directly convert to integer
                century_value = int(century_input.strip())
        except ValueError:
            logger.error(f"Invalid century format: {century_input}")
            self.send_error(400, "Invalid century format. Use integer values (negative for BCE, positive for CE)")
            return

        logger.info(f"Parsed century value: {century_value}")

        try:
            # Make a backup of the current data
            try:
                backup_path = 'authors_data.json.bak'
                if os.path.exists('authors_data.json'):
                    import shutil
                    logger.debug(f"Creating backup at {os.path.abspath(backup_path)}")
                    shutil.copy2('authors_data.json', backup_path)
            except Exception as e:
                logger.warning(f"Could not create backup: {str(e)}")
                # Continue anyway
            
            # First, try to update the global variable directly
            if author_id in AUTHORS_DATA:
                old_century = AUTHORS_DATA[author_id].get('century', 'None')
                logger.info(f"Updating global AUTHORS_DATA: {author_id} century from '{old_century}' to '{century_value}'")
                AUTHORS_DATA[author_id]['century'] = century_value
            
            # Next, handle the file-based update
            authors_data = {}
            try:
                authors_data_path = 'authors_data.json'
                logger.debug(f"Loading author data from {os.path.abspath(authors_data_path)}")
                
                # Read the existing file with explicit UTF-8 encoding
                with open(authors_data_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    logger.debug(f"File loaded, size: {len(file_content)} bytes")
                    authors_data = json.loads(file_content)
                    logger.debug(f"JSON parsed successfully with {len(authors_data)} authors")
            except FileNotFoundError:
                logger.error(f"File not found: {authors_data_path}")
                # Use the global data if file not found
                authors_data = AUTHORS_DATA.copy()
                logger.info(f"Using global data with {len(authors_data)} entries")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Content excerpt: {file_content[:100]}...")
                self.send_error(500, "Error parsing author data")
                return
            
            # Update century in the loaded data
            if author_id in authors_data:
                old_century = authors_data[author_id].get('century', 'None')
                logger.info(f"Updating author '{author_id}' century from '{old_century}' to '{century_value}'")
                authors_data[author_id]['century'] = century_value
                
                # Write to file with atomic operation to prevent partial writes
                try:
                    # Write to a temporary file first
                    temp_path = f"{authors_data_path}.tmp"
                    logger.debug(f"Writing to temporary file {temp_path}")
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(authors_data, f, indent=2, ensure_ascii=False)
                    
                    # Rename the temporary file to the target file (atomic operation)
                    logger.debug(f"Renaming {temp_path} to {authors_data_path}")
                    os.replace(temp_path, authors_data_path)
                    
                    # Set permissions to ensure it's writable
                    try:
                        os.chmod(authors_data_path, 0o644)  # Read/write for owner, read for others
                        logger.debug(f"Set permissions on {authors_data_path} to 0o644")
                    except Exception as e:
                        logger.warning(f"Could not set permissions: {str(e)}")
                    
                    # Verify the file was updated
                    time.sleep(0.1)  # Small delay to ensure file system sync
                    if os.path.exists(authors_data_path):
                        file_size = os.path.getsize(authors_data_path)
                        logger.info(f"File saved successfully, size: {file_size} bytes")
                        
                        # Update global AUTHORS_DATA to match the file
                        AUTHORS_DATA = authors_data
                        logger.info("Updated global AUTHORS_DATA from file")
                        
                        # Update the PageGenerator's data to ensure consistency
                        if hasattr(self, 'page_generator'):
                            self.page_generator.authors_data = authors_data
                            logger.debug("Updated PageGenerator's in-memory data")
                        
                        # Send success response with cache-busting headers
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Expires', '0')
                        self.end_headers()
                        
                        response_data = {
                            'success': True, 
                            'author_id': author_id, 
                            'century': century_value,
                            'timestamp': time.time()
                        }
                        self.wfile.write(json.dumps(response_data).encode())
                        
                        logger.info(f"Century update successful for {author_id}: {century_value}")
                    else:
                        logger.error(f"File does not exist after save: {authors_data_path}")
                        self.send_error(500, "File disappeared after saving")
                except PermissionError as e:
                    logger.error(f"Permission denied: {str(e)}")
                    self.send_error(500, f"Permission denied: {str(e)}")
                except OSError as e:
                    logger.error(f"OS error during file save: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.send_error(500, f"File system error: {str(e)}")
            else:
                logger.warning(f"Author not found in data: {author_id}")
                self.send_error(404, f"Author '{author_id}' not found")
        except Exception as e:
            logger.error(f"Unhandled error in handle_update_century: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Error updating century: {str(e)}")
            
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
            logger.debug(f"Successfully sent {len(content)} bytes")
        except Exception as e:
            logger.error(f"Error serving static file {path}: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(404, f"File not found: {str(e)}")

    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        if file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.html'):
            return 'text/html'
        elif file_path.endswith('.json'):
            return 'application/json'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        elif file_path.endswith('.gif'):
            return 'image/gif'
        else:
            return 'application/octet-stream'

    def send_html_response(self, html):
        """Send an HTML response"""
        try:
            encoded_html = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(encoded_html))
            # Add cache-busting headers to ensure fresh content
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(encoded_html)
            logger.debug(f"Sending HTML response, length: {len(encoded_html)}")
            logger.debug(f"Successfully sent {len(encoded_html)} bytes")
        except Exception as e:
            logger.error(f"Error sending HTML response: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Error sending response: {str(e)}")
            
    def send_json_response(self, data):
        """Send a JSON response"""
        try:
            encoded_json = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(encoded_json))
            # Add cache-busting headers to ensure fresh content
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(encoded_json)
            logger.debug(f"Sending JSON response, length: {len(encoded_json)}")
        except Exception as e:
            logger.error(f"Error sending JSON response: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Error sending response: {str(e)}")
            
def main():
    """Main function to start the server"""
    global server_instance, PORT, DEBUG
    
    # Start time for server
    start_time = time.time()
    
    # Parse command line arguments only when running as main
    args = parse_args()
    PORT = args.port
    DEBUG = args.debug
    
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
                server_start = time.time()
                server_instance = socketserver.TCPServer((HOST, current_port), CustomHTTPRequestHandler)
                logger.info(f"Server started at http://{HOST}:{current_port} (took {time.time() - server_start:.3f}s)")
                
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
                    logger.error(traceback.format_exc())
                    raise
                    
    except KeyboardInterrupt:
        logger.info("\nServer shutdown requested.")
        shutdown_time = time.time()
        if server_instance:
            try:
                server_instance.shutdown()
                logger.info(f"Server has been shut down gracefully (took {time.time() - shutdown_time:.3f}s)")
            except Exception as e:
                logger.error(f"Error during shutdown: {str(e)}")
                logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # Log total runtime
        total_time = time.time() - start_time
        logger.info(f"Server process finished. Total runtime: {total_time:.2f} seconds")

def handle_shutdown(sig, frame):
    """Handle external shutdown signals"""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    if server_instance:
        try:
            server_instance.shutdown()
            logger.info("Server has been shut down via signal handler")
        except Exception as e:
            logger.error(f"Error during signal-triggered shutdown: {str(e)}")

if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Start the server
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in main program: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 