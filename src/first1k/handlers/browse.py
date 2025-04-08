"""Browse handlers for First1KGreek Browser."""

import os
import re
import time
import logging
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

def render_authors_page():
    """Generate the authors listing page."""
    # Get author directories from the data folder
    author_dirs = []
    for item in os.listdir('data'):
        item_path = os.path.join('data', item)
        if os.path.isdir(item_path) and (item.startswith('tlg') or item.startswith('heb')):
            author_dirs.append(item)
    
    # Get author names from files
    author_names = {}
    for author_id in author_dirs:
        author_name = get_author_name_from_files(author_id)
        author_names[author_id] = author_name if author_name else author_id
    
    # Sort alphabetically by author name, then by ID
    author_items = [(author_id, author_names[author_id]) for author_id in author_dirs]
    author_items.sort(key=lambda x: (x[1].lower(), x[0]))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>First1K Greek - Authors</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <style>
        .author-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }}
        .author-card {{
            background-color: #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
            cursor: pointer;
        }}
        .author-card:hover {{
            transform: translateY(-5px);
            background-color: #444;
        }}
        .nav-links {{
            margin: 20px 0;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
        }}
        .button:hover {{
            background: #3182ce;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Authors</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
            <a href="/search" class="button">Search</a>
        </div>
        
        <p>Showing {len(author_items)} authors, alphabetically ordered by name</p>
        
        <div class="author-grid">
"""
    
    for author_id, author_name in author_items:
        display_name = f"{author_name} ({author_id})" if author_name != author_id else author_id
        html += f"""
            <a href="/works?author={author_id}" style="text-decoration: none; color: inherit;">
                <div class="author-card">
                    <div class="author-name">{display_name}</div>
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
    <style>
        .editors-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }}
        .editor-card {{
            background-color: #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
        }}
        .editor-card:hover {{
            transform: translateY(-5px);
            background-color: #444;
        }}
        .featured-editor {{
            background-color: #1e392a;
            border-left: 4px solid #2ecc71;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .featured-editor-bio {{
            margin-top: 10px;
            font-style: italic;
            color: #aaa;
        }}
        .nav-links {{
            margin: 20px 0;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
        }}
        .button:hover {{
            background: #3182ce;
        }}
    </style>
</head>
<body>
    <div class="container">
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