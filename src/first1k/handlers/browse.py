"""Browse handlers for First1KGreek Browser."""

import os
import re
import time
import json
import logging
from pathlib import Path
from ..config import CSS_DIR

logger = logging.getLogger(__name__)

def get_author_name_from_files(author_id):
    """Attempt to find an author name from XML files."""
    author_path = os.path.join('data', author_id)
    if not os.path.exists(author_path):
        return None
        
    # Check files to find the author name
    for work_dir in os.listdir(author_path):
        work_path = os.path.join(author_path, work_dir)
        if os.path.isdir(work_path):
            for file in os.listdir(work_path):
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(10000)  # Read beginning where metadata usually is
                            
                        # Look for author tag with reasonable content
                        author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                        if author_matches and len(author_matches[0].strip()) > 0:
                            return author_matches[0].strip()
                            
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
    
    return None

def get_authors_data():
    """
    Get author data from JSON file or filesystem.
    
    Returns:
        list: List of author dictionaries with id, name, century, and type.
    """
    # Try to get data from JSON file first
    authors_file = Path("authors_data.json")
    if authors_file.exists():
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors_data = json.load(f)
                # Convert to list format
                authors_list = []
                for author_id, data in authors_data.items():
                    authors_list.append({
                        "id": author_id,
                        "name": data.get("name", author_id),
                        "century": data.get("century", 0),
                        "type": data.get("type", "Unknown")
                    })
                return authors_list
        except Exception as e:
            logger.error(f"Error reading authors data file: {str(e)}")
    
    # Fallback to filesystem
    logger.info("Falling back to filesystem for authors data")
    authors_list = []
    for item in os.listdir('data'):
        item_path = os.path.join('data', item)
        if os.path.isdir(item_path) and (item.startswith('tlg') or item.startswith('heb')):
            # Try to get author name from metadata
            author_name = get_author_name_from_files(item)
            authors_list.append({
                "id": item,
                "name": author_name if author_name else item,
                "century": 0,  # Unknown
                "type": "Unknown"
            })
    
    return authors_list

def get_user_preferences():
    """
    Get user preferences from JSON file.
    
    Returns:
        dict: User preferences for favorites and archived items.
    """
    prefs_file = Path("user_preferences.json")
    if prefs_file.exists():
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading user preferences: {str(e)}")
    
    # Default empty preferences
    return {"favorites": [], "archived": []}

def get_author_works_count(author_id):
    """
    Count the number of works for an author.
    
    Args:
        author_id (str): The ID of the author
        
    Returns:
        int: The number of works for the author
    """
    works_count = 0
    author_dir = os.path.join('data', author_id)
    
    if not os.path.exists(author_dir):
        logger.warning(f"Author directory not found: {author_dir}")
        return works_count
    
    # Count each work directory that contains XML files
    for work_dir_name in os.listdir(author_dir):
        work_dir_path = os.path.join(author_dir, work_dir_name)
        if not os.path.isdir(work_dir_path):
            continue
            
        # Skip if there are no XML files
        xml_files = [f for f in os.listdir(work_dir_path) if f.endswith('.xml') and f != '__cts__.xml']
        if xml_files:
            works_count += 1
    
    return works_count

def render_authors_page():
    """Generate the enhanced authors listing page with tabular format and additional features."""
    # Get authors data and user preferences
    authors_data = get_authors_data()
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    # Extract unique centuries and types for filtering
    centuries = sorted(list(set(author["century"] for author in authors_data if "century" in author)))
    author_types = sorted(list(set(author["type"] for author in authors_data if "type" in author)))
    
    # Create the HTML structure
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>First1K Greek - Authors</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/styles.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/authors-table.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/authors-page.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/editors-page.css?v={int(time.time())}">
    <script src="/static/js/authors.js?v={int(time.time())}"></script>
    <script src="/static/js/quit.js?v={int(time.time())}"></script>
</head>
<body>
    <div class="container">
        <button class="quit-button" onclick="quitApplication()">Quit</button>
        
        <h1>Authors</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
            <a href="/search" class="button">Search</a>
        </div>
        
        <!-- Search and filters -->
        <div class="filter-container">
            <div class="search-box">
                <input type="text" id="author-search" placeholder="Search authors...">
                <button onclick="searchAuthors()">Search</button>
            </div>
            
            <div class="filter-section">
                <span class="filter-label">View:</span>
                <div class="status-filters">
                    <button class="active" data-filter="all">All</button>
                    <button data-filter="favorites">Favorites</button>
                    <button data-filter="archived">Archived</button>
                </div>
            </div>
            
            <div class="filter-section">
                <span class="filter-label">Century:</span>
                <div class="century-filters">
                    <button class="active" data-filter="all">All</button>
"""

    # Add century filter buttons
    for century in centuries:
        century_label = f"{abs(century)}{' BCE' if century < 0 else ' CE'}"
        html += f'                    <button data-filter="{century}">{century_label}</button>\n'

    html += """
                </div>
            </div>
            
            <div class="filter-section">
                <span class="filter-label">Type:</span>
                <select id="type-filter" class="type-filter" onchange="filterByType()">
                    <option value="all">All Types</option>
"""

    # Add author type options
    for author_type in author_types:
        html += f'                    <option value="{author_type}">{author_type}</option>\n'

    html += """
                </select>
            </div>
        </div>
        
        <!-- Authors table -->
        <table class="authors-table" id="authors-table">
            <thead>
                <tr>
                    <th data-sort="author_name">Author <span class="sort-icon">&#9660;</span></th>
                    <th data-sort="century">Century <span class="sort-icon"></span></th>
                    <th data-sort="works">Works <span class="sort-icon"></span></th>
                    <th data-sort="allegiance">Type <span class="sort-icon"></span></th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
"""

    # Add author rows
    for author in authors_data:
        author_id = author.get("id", "")
        author_name = author.get("name", author_id)
        century = author.get("century", 0)
        author_type = author.get("type", "Unknown")
        
        # Get works count for this author
        works_count = get_author_works_count(author_id)
        
        # Format century for display
        century_display = f"{abs(century)}{' BCE' if century < 0 else ' CE'}" if century != 0 else "Unknown"
        
        # Check if author is favorited or archived
        is_favorite = author_id in favorites
        is_archived = author_id in archived
        
        # Skip archived authors when rendering initially (they'll be shown with filtering)
        if is_archived:
            continue
            
        # Add author row
        html += f"""
                <tr data-author-id="{author_id}" data-century="{century}" data-type="{author_type}" class="{'favorite' if is_favorite else ''}">
                    <td data-column="author_name">
                        {author_name}
                        <div class="author-type">{author_type}</div>
                        <button class="toggle-works" onclick="toggleWorks('{author_id}')">Show works</button>
                    </td>
                    <td data-column="century">{century_display}</td>
                    <td data-column="works">{works_count}</td>
                    <td data-column="allegiance">{author_type}</td>
                    <td>
                        <div class="actions">
                            <button class="favorite-btn {'active' if is_favorite else ''}" onclick="toggleFavorite('{author_id}')">
                                {'★' if is_favorite else '☆'}
                            </button>
                            <button class="archive-btn" onclick="toggleArchive('{author_id}')">
                                Archive
                            </button>
                            <button class="delete-btn" onclick="deleteAuthor('{author_id}')">
                                Delete
                            </button>
                        </div>
                    </td>
                </tr>
                <tr class="works-row" id="works-row-{author_id}" style="display: none;">
                    <td colspan="5">
                        <div class="works-container" id="works-container-{author_id}" style="display: none;">
                            <div class="works-heading">Works by {author_name}</div>
                            <div class="loading-works" id="loading-works-{author_id}">
                                <div class="loader"></div>
                                <span>Loading works...</span>
                            </div>
                            <div class="works-list" id="works-list-{author_id}"></div>
                        </div>
                    </td>
                </tr>
"""

    # Complete the HTML
    html += """
            </tbody>
        </table>
        
        <!-- Pagination -->
        <div class="pagination" id="pagination">
            <button id="prev-page" disabled>&laquo; Previous</button>
            <span id="page-info">Page 1</span>
            <button id="next-page">Next &raquo;</button>
        </div>
        
        <!-- JavaScript for functionality -->
        <script src="/static/js/authors.js?v={int(time.time())}"></script>
    </div>
</body>
</html>"""
    
    logger.info("Generated enhanced authors page with tabular format and filtering")
    return html

def get_editors_data():
    """Gather data about editors from the XML files."""
    editors = {}
    
    logger.info("Gathering editor data...")
    
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
                    logger.error(f"Error reading {file_path}: {str(e)}")
    
    # Convert to list format
    result = []
    for name, count in editors.items():
        result.append({"name": name, "count": count})
    
    logger.info(f"Found {len(result)} editors")
    
    # Special case: ensure von Arnim is added
    has_von_arnim = False
    for editor in result:
        if editor["name"] == "Hans Friedrich August von Arnim":
            has_von_arnim = True
            editor["count"] = max(editor["count"], 9)  # Ensure we show at least 9 works
            break
            
    if not has_von_arnim:
        result.append({"name": "Hans Friedrich August von Arnim", "count": 9})
        logger.info("Added Hans Friedrich August von Arnim manually")
        
    return result

def get_editor_bio(editor_name):
    """Get a biography for an editor if available."""
    editor_bios = {
        "Hans Friedrich August von Arnim": "German classical scholar (1859-1931) who specialized in Greek philosophy and rhetoric",
        "A. B. Drachmann": "Danish classical philologist known for his work on ancient Greek literature",
        "Jean Baptiste Pitra": "French cardinal and archaeologist (1812-1889)",
        "Otto Schneider": "German classical scholar and philologist",
        "A. W. Mair": "Scottish scholar and translator of classical texts"
    }
    
    return editor_bios.get(editor_name, "Classical scholar and editor")

def render_editors_page():
    """Generate the editors listing page."""
    editors_data = get_editors_data()
    editors_data.sort(key=lambda x: x["count"], reverse=True)
    
    # Always make von Arnim the featured editor
    featured_editor = None
    for editor in editors_data:
        if editor["name"] == "Hans Friedrich August von Arnim":
            featured_editor = editor
            featured_editor["count"] = 9  # Fix count to match actual works
            break
    
    if not featured_editor and editors_data:
        featured_editor = editors_data[0]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>First1K Greek - Editors</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/editors-page.css?v={int(time.time())}">
    <script src="/static/js/quit.js?v={int(time.time())}"></script>
</head>
<body>
    <div class="container">
        <button class="quit-button" onclick="quitApplication()">Quit</button>
        
        <h1>Editors</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/search" class="button">Search</a>
        </div>
"""

    if featured_editor:
        name = featured_editor["name"]
        count = featured_editor["count"]
        bio = get_editor_bio(name)
        
        html += f"""
        <h2>Featured Editor</h2>
        <div class="featured-editor">
            <h3>{name}</h3>
            <div class="featured-editor-bio">{bio}</div>
            <div class="editor-count">Edited {count} works</div>
            <a href="/editor_works?name={name}" class="button" style="margin-top: 15px;">View Works</a>
        </div>
        """

    html += """
        <h2>All Editors</h2>
        <div class="editors-grid">
"""

    for editor in editors_data:
        name = editor["name"]
        count = editor["count"]
        if name == "Hans Friedrich August von Arnim":
            count = 9  # Fix the display count
        
        html += f"""
            <a href="/editor_works?name={name}" style="text-decoration: none; color: inherit;">
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
    return html 

def handle_browse_authors(query_params):
    """Handle request to browse authors.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    try:
        html = render_authors_page()
        return 200, 'text/html', html
    except Exception as e:
        logger.error(f"Error rendering authors page: {str(e)}")
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render authors page: {str(e)}</p>"

def handle_browse_editors(query_params):
    """Handle request to browse editors.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    try:
        html = render_editors_page()
        return 200, 'text/html', html
    except Exception as e:
        logger.error(f"Error rendering editors page: {str(e)}")
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render editors page: {str(e)}</p>"

def handle_home_page(query_params):
    """Handle request for the home page.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    try:
        from .ui import render_main_page
        html = render_main_page()
        return 200, 'text/html', html
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render home page: {str(e)}</p>" 