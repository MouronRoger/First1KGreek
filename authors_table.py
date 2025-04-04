#!/usr/bin/env python3
"""
Authors Table Viewer for First1KGreek Browser
"""

import os
import sys
import json
import http.server
import socketserver
import webbrowser
from urllib.parse import parse_qs, urlparse, quote
import shutil
import time

PORT = 8080

# Load the author centuries data
AUTHOR_CENTURIES = {}
try:
    with open('author_centuries.json', 'r', encoding='utf-8') as f:
        AUTHOR_CENTURIES = json.load(f)
except Exception as e:
    print(f"Warning: Could not load author_centuries.json: {e}")

# Define user preferences storage
USER_PREFS_FILE = 'user_preferences.json'
def load_user_preferences():
    try:
        with open(USER_PREFS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'favorites': [],
            'archived': [],
            'deleted': []
        }
    except Exception as e:
        print(f"Error loading user preferences: {e}")
        return {
            'favorites': [],
            'archived': [],
            'deleted': []
        }

def save_user_preferences(prefs):
    try:
        with open(USER_PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2)
    except Exception as e:
        print(f"Error saving user preferences: {e}")

# CSS styles for the table view
TABLE_STYLES = """
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    background-color: #1a1a1a;
    color: #ffffff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #2d2d2d;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    min-height: 100vh;
}

h1, h2, h3 {
    color: #4299e1;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

a {
    color: #4299e1;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.navigation {
    margin: 20px 0;
}

.navigation a {
    display: inline-block;
    margin-right: 15px;
    background: #3182ce;
    color: white;
    padding: 10px 15px;
    text-decoration: none;
    border-radius: 4px;
}

.navigation a:hover {
    background: #2c5282;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: #333;
    border-radius: 5px;
    overflow: hidden;
}

table th {
    padding: 12px 15px;
    text-align: left;
    background-color: #1a365d;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

table th:hover {
    background-color: #2a4365;
}

table td {
    padding: 10px 15px;
    border-bottom: 1px solid #444;
}

table tr:hover {
    background-color: #3a3a3a;
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

.status-filters {
    margin: 10px 0;
}

.status-filters button {
    padding: 8px 15px;
    margin-right: 10px;
    background-color: #2d3748;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.status-filters button:hover {
    background-color: #4a5568;
}

.status-filters button.active {
    background-color: #3182ce;
}

.century-filters {
    margin: 10px 0;
}

.century-filters button {
    padding: 8px 15px;
    margin-right: 10px;
    background-color: #2d3748;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.century-filters button:hover {
    background-color: #4a5568;
}

.century-filters button.active {
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

.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -60px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
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
"""

# JavaScript for table features
TABLE_SCRIPT = """
document.addEventListener('DOMContentLoaded', function() {
    // Initial variables
    let authors = [];
    let filteredAuthors = [];
    let currentSort = {
        column: 'author_name',
        direction: 'asc'
    };
    let currentFilter = '';
    let currentPage = 1;
    const pageSize = 20;
    let activeStatusFilter = 'all'; // 'all', 'favorites', 'archived'
    let activeCenturyFilter = 'all'; // 'all', 'BCE', 'CE-1-3', 'CE-4-6'
    
    // Load user preferences
    const userPrefs = JSON.parse(document.getElementById('user-prefs').textContent);
    
    // Get all authors data from the table
    const table = document.getElementById('authors-table');
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    
    rows.forEach(row => {
        const authorId = row.getAttribute('data-id');
        const authorName = row.querySelector('[data-column="author_name"]').textContent;
        const century = row.querySelector('[data-column="century"]').textContent;
        const numWorks = parseInt(row.querySelector('[data-column="works"]').textContent);
        
        const author = {
            id: authorId,
            author_name: authorName,
            century: century,
            works: numWorks,
            favorite: userPrefs.favorites.includes(authorId),
            archived: userPrefs.archived.includes(authorId),
            deleted: userPrefs.deleted.includes(authorId),
            element: row
        };
        
        authors.push(author);
    });
    
    // Initialize filtered authors
    filteredAuthors = [...authors].filter(author => !author.deleted);
    
    // Sort function
    function sortAuthors(column, direction) {
        filteredAuthors.sort((a, b) => {
            let valueA = a[column];
            let valueB = b[column];
            
            // Handle numeric values
            if (column === 'works') {
                valueA = parseInt(valueA);
                valueB = parseInt(valueB);
            }
            
            if (valueA < valueB) {
                return direction === 'asc' ? -1 : 1;
            }
            if (valueA > valueB) {
                return direction === 'asc' ? 1 : -1;
            }
            return 0;
        });
        
        renderTable();
    }
    
    // Filter function
    function filterAuthors() {
        const searchText = document.getElementById('search-input').value.toLowerCase();
        
        filteredAuthors = authors.filter(author => {
            // Status filter
            if (activeStatusFilter === 'favorites' && !author.favorite) return false;
            if (activeStatusFilter === 'archived' && !author.archived) return false;
            if (activeStatusFilter === 'normal' && (author.favorite || author.archived)) return false;
            
            // Century filter
            if (activeCenturyFilter === 'BCE' && !author.century.includes('BCE')) return false;
            if (activeCenturyFilter === 'CE-1-3' && 
                !(author.century.includes('1 CE') || 
                  author.century.includes('2 CE') || 
                  author.century.includes('3 CE'))) return false;
            if (activeCenturyFilter === 'CE-4-6' && 
                !(author.century.includes('4 CE') || 
                  author.century.includes('5 CE') || 
                  author.century.includes('6 CE'))) return false;
            
            // Exclude deleted
            if (author.deleted) return false;
            
            // Text search
            if (searchText) {
                return author.author_name.toLowerCase().includes(searchText) || 
                       author.century.toLowerCase().includes(searchText) ||
                       author.id.toLowerCase().includes(searchText);
            }
            
            return true;
        });
        
        // Reset to first page when filtering
        currentPage = 1;
        
        // Apply current sort
        sortAuthors(currentSort.column, currentSort.direction);
    }
    
    // Render table with current filters, sort, and pagination
    function renderTable() {
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';
        
        // Calculate pagination
        const totalPages = Math.ceil(filteredAuthors.length / pageSize);
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = Math.min(startIndex + pageSize, filteredAuthors.length);
        
        // Update pagination UI
        updatePagination(totalPages);
        
        // Show visible authors for current page
        for (let i = startIndex; i < endIndex; i++) {
            const author = filteredAuthors[i];
            const row = author.element.cloneNode(true);
            
            // Update favorite and archive buttons to reflect current state
            const favoriteBtn = row.querySelector('.favorite-btn');
            const archiveBtn = row.querySelector('.archive-btn');
            
            if (author.favorite) {
                favoriteBtn.classList.add('active');
                favoriteBtn.textContent = 'Unfavorite';
                // Add star icon
                const nameCell = row.querySelector('[data-column="author_name"]');
                if (!nameCell.innerHTML.includes('★')) {
                    nameCell.innerHTML = '<span class="favorites-star">★</span> ' + nameCell.innerHTML;
                }
            } else {
                favoriteBtn.classList.remove('active');
                favoriteBtn.textContent = 'Favorite';
            }
            
            if (author.archived) {
                archiveBtn.classList.add('active');
                archiveBtn.textContent = 'Unarchive';
                // Add archive icon
                const nameCell = row.querySelector('[data-column="author_name"]');
                if (!nameCell.innerHTML.includes('📦')) {
                    nameCell.innerHTML = '<span class="archived-icon">📦</span> ' + nameCell.innerHTML;
                }
            } else {
                archiveBtn.classList.remove('active');
                archiveBtn.textContent = 'Archive';
            }
            
            // Add event listeners to the buttons
            setupButtonListeners(row, author);
            
            tbody.appendChild(row);
        }
    }
    
    function setupButtonListeners(row, author) {
        // Favorite button
        const favoriteBtn = row.querySelector('.favorite-btn');
        favoriteBtn.addEventListener('click', function() {
            author.favorite = !author.favorite;
            updateUserPreference(author.id, 'favorites', author.favorite);
            renderTable();
        });
        
        // Archive button
        const archiveBtn = row.querySelector('.archive-btn');
        archiveBtn.addEventListener('click', function() {
            author.archived = !author.archived;
            updateUserPreference(author.id, 'archived', author.archived);
            renderTable();
        });
        
        // Delete button
        const deleteBtn = row.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', function() {
            if (confirm(`Are you sure you want to delete ${author.author_name}?`)) {
                author.deleted = true;
                updateUserPreference(author.id, 'deleted', true);
                filterAuthors(); // Re-filter to remove this author
            }
        });
    }
    
    function updateUserPreference(authorId, prefType, value) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/update_preference', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log('Preference updated successfully');
            }
        };
        xhr.send(`author_id=${authorId}&pref_type=${prefType}&value=${value}`);
    }
    
    function updatePagination(totalPages) {
        const pagination = document.querySelector('.pagination');
        pagination.innerHTML = '';
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '←';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });
        pagination.appendChild(prevBtn);
        
        // Page numbers
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        // Adjust start if we're near the end
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === currentPage);
            pageBtn.addEventListener('click', function() {
                currentPage = i;
                renderTable();
            });
            pagination.appendChild(pageBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '→';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });
        pagination.appendChild(nextBtn);
    }
    
    // Setup event listeners for sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            let direction = 'asc';
            
            // If already sorted by this column, toggle direction
            if (currentSort.column === column) {
                direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            }
            
            // Remove sort indicators from all headers
            document.querySelectorAll('th[data-sort]').forEach(header => {
                header.textContent = header.textContent.replace(' ↑', '').replace(' ↓', '');
            });
            
            // Add indicator to current header
            this.textContent += direction === 'asc' ? ' ↑' : ' ↓';
            
            currentSort.column = column;
            currentSort.direction = direction;
            
            sortAuthors(column, direction);
        });
    });
    
    // Setup search input
    document.getElementById('search-btn').addEventListener('click', filterAuthors);
    document.getElementById('search-input').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            filterAuthors();
        }
    });
    
    // Setup status filter buttons
    document.querySelectorAll('.status-filters button').forEach(button => {
        button.addEventListener('click', function() {
            activeStatusFilter = this.getAttribute('data-filter');
            
            // Update active button
            document.querySelectorAll('.status-filters button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            filterAuthors();
        });
    });
    
    // Setup century filter buttons
    document.querySelectorAll('.century-filters button').forEach(button => {
        button.addEventListener('click', function() {
            activeCenturyFilter = this.getAttribute('data-filter');
            
            // Update active button
            document.querySelectorAll('.century-filters button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            filterAuthors();
        });
    });
    
    // Initial sort and render
    sortAuthors('author_name', 'asc');
});
"""

class AuthorsTableRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for authors table view"""
    
    def send_response_with_headers(self, content_type='text/html'):
        """Send response with appropriate headers"""
        self.send_response(200)
        self.send_header('Content-type', f'{content_type}; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
    
    def send_html(self, html_content):
        """Send HTML response"""
        self.send_response_with_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/' or path == '/authors_table':
            self.send_html(self.get_authors_table())
        elif path.startswith('/data/'):
            # Serve files from data directory
            super().do_GET()
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/update_preference':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            author_id = params.get('author_id', [''])[0]
            pref_type = params.get('pref_type', [''])[0]
            value = params.get('value', ['false'])[0].lower() == 'true'
            
            if author_id and pref_type:
                self.update_user_preference(author_id, pref_type, value)
                self.send_response_with_headers()
                self.wfile.write(b'{"status": "ok"}')
            else:
                self.send_error(400, "Bad Request")
        else:
            self.send_error(404, "Not Found")
    
    def update_user_preference(self, author_id, pref_type, value):
        """Update user preference"""
        prefs = load_user_preferences()
        
        if pref_type in ['favorites', 'archived', 'deleted']:
            if value and author_id not in prefs[pref_type]:
                prefs[pref_type].append(author_id)
            elif not value and author_id in prefs[pref_type]:
                prefs[pref_type].remove(author_id)
            
            save_user_preferences(prefs)
    
    def get_authors_table(self):
        """Generate the authors table HTML"""
        # Get author data
        authors_data = self.get_authors_data()
        
        # Load user preferences
        user_prefs = load_user_preferences()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>First1K Greek - Authors Table</title>
            <style>
                {TABLE_STYLES}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>First1K Greek - Authors Table</h1>
                
                <div class="navigation">
                    <a href="http://localhost:8000/">Back to Main Browser</a>
                </div>
                
                <div class="search-filter">
                    <input type="text" id="search-input" placeholder="Search authors...">
                    <button id="search-btn">Search</button>
                    
                    <div class="status-filters">
                        <b>Status:</b>
                        <button data-filter="all" class="active">All</button>
                        <button data-filter="favorites">Favorites</button>
                        <button data-filter="archived">Archived</button>
                        <button data-filter="normal">Normal</button>
                    </div>
                    
                    <div class="century-filters">
                        <b>Century:</b>
                        <button data-filter="all" class="active">All</button>
                        <button data-filter="BCE">BCE</button>
                        <button data-filter="CE-1-3">1-3 CE</button>
                        <button data-filter="CE-4-6">4-6 CE</button>
                    </div>
                </div>
                
                <table id="authors-table">
                    <thead>
                        <tr>
                            <th data-sort="author_name">Author</th>
                            <th data-sort="century">Century</th>
                            <th data-sort="works">Works</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add author rows
        for author in authors_data:
            author_id = author['id']
            is_favorite = author_id in user_prefs['favorites']
            is_archived = author_id in user_prefs['archived']
            is_deleted = author_id in user_prefs['deleted']
            
            if is_deleted:
                continue  # Skip deleted authors
            
            html += f"""
                        <tr data-id="{author_id}">
                            <td data-column="author_name">
                                {"<span class='favorites-star'>★</span> " if is_favorite else ""}
                                {"<span class='archived-icon'>📦</span> " if is_archived else ""}
                                <a href="http://localhost:8000/works?author={author_id}">{author['name']}</a>
                            </td>
                            <td data-column="century">{author['century']}</td>
                            <td data-column="works">{author['works']}</td>
                            <td>
                                <button class="action-btn favorite-btn{' active' if is_favorite else ''}">{
                                    "Unfavorite" if is_favorite else "Favorite"}</button>
                                <button class="action-btn archive-btn{' active' if is_archived else ''}">{
                                    "Unarchive" if is_archived else "Archive"}</button>
                                <button class="action-btn delete-btn">Delete</button>
                            </td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
                
                <div class="pagination">
                    <!-- Pagination will be added by JavaScript -->
                </div>
                
                <script id="user-prefs" type="application/json">
                """
        html += json.dumps(user_prefs)
        html += """
                </script>
                
                <script>
                """
        html += TABLE_SCRIPT
        html += """
                </script>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_authors_data(self):
        """Get data about authors and their works"""
        authors = []
        data_dir = 'data'
        
        if not os.path.exists(data_dir):
            return []
        
        for item in os.listdir(data_dir):
            author_path = os.path.join(data_dir, item)
            if os.path.isdir(author_path) and (item.startswith('tlg') or item.startswith('heb')):
                # Count works
                work_count = 0
                author_name = item
                
                # Look for author name in __cts__.xml
                author_cts_path = os.path.join(author_path, '__cts__.xml')
                if os.path.exists(author_cts_path):
                    try:
                        with open(author_cts_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            import re
                            name_match = re.search(r'<ti:groupname[^>]*>(.*?)</ti:groupname>', content)
                            if name_match:
                                author_name = name_match.group(1).strip()
                    except Exception as e:
                        print(f"Error reading {author_cts_path}: {e}")
                
                # Count works (subdirectories)
                for work_item in os.listdir(author_path):
                    work_path = os.path.join(author_path, work_item)
                    if os.path.isdir(work_path):
                        work_count += 1
                
                # Get century
                century = AUTHOR_CENTURIES.get(item, "Unknown")
                
                authors.append({
                    'id': item,
                    'name': author_name,
                    'century': century,
                    'works': work_count
                })
        
        # Sort by name
        authors.sort(key=lambda x: x['name'])
        
        return authors

def run_server():
    """Run the HTTP server"""
    # Find available port
    port = PORT
    while True:
        try:
            with socketserver.TCPServer(("", port), AuthorsTableRequestHandler) as httpd:
                print(f"Serving authors table at http://localhost:{port}/")
                webbrowser.open(f"http://localhost:{port}/")
                httpd.serve_forever()
        except OSError:
            port += 1
            if port > PORT + 10:
                print("Could not find available port, please close some applications and try again")
                sys.exit(1)
        except KeyboardInterrupt:
            print("Server stopped.")
            sys.exit(0)

if __name__ == "__main__":
    run_server() 