"""Works listing handlers for First1KGreek Browser."""

import os
import re
import time
from ..config import CSS_DIR

def get_works_by_author(author_id):
    """Get list of works for an author."""
    works = []
    author_dir = os.path.join('data', author_id)
    
    if not os.path.exists(author_dir):
        return []
        
    # Get author name from metadata
    author_name = None
    author_cts_path = os.path.join(author_dir, '__cts__.xml')
    if os.path.exists(author_cts_path):
        try:
            with open(author_cts_path, 'r', encoding='utf-8') as f:
                content = f.read()
                name_match = re.search(r'<ti:groupname[^>]*>(.*?)</ti:groupname>', content)
                if name_match:
                    author_name = name_match.group(1).strip()
        except Exception as e:
            print(f"Error reading author metadata: {str(e)}")
    
    # If no name in metadata, try to get from files
    if not author_name:
        for work_dir in os.listdir(author_dir):
            work_path = os.path.join(author_dir, work_dir)
            if os.path.isdir(work_path):
                for file in os.listdir(work_path):
                    if file.endswith('.xml') and not file == '__cts__.xml':
                        file_path = os.path.join(work_path, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(10000)
                                author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                                if author_matches and len(author_matches[0].strip()) > 0:
                                    author_name = author_matches[0].strip()
                                    break
                        except Exception as e:
                            print(f"Error reading {file_path}: {str(e)}")
                if author_name:
                    break
    
    if not author_name:
        author_name = f"Author {author_id}"
    
    # Get works
    for work_dir in os.listdir(author_dir):
        work_path = os.path.join(author_dir, work_dir)
        if os.path.isdir(work_path):
            work_title = None
            work_language = None
            work_editor = None
            
            # Try to get metadata from work's __cts__.xml
            work_cts_path = os.path.join(work_path, '__cts__.xml')
            if os.path.exists(work_cts_path):
                try:
                    with open(work_cts_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                        if title_match:
                            work_title = title_match.group(1).strip()
                        lang_match = re.search(r'xml:lang="([^"]+)"', content)
                        if lang_match:
                            work_language = lang_match.group(1)
                except Exception as e:
                    print(f"Error reading work metadata: {str(e)}")
            
            # Get XML files in work directory
            for file in os.listdir(work_path):
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(10000)
                            
                        # Get title if not found in metadata
                        if not work_title:
                            title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                            if title_matches:
                                work_title = title_matches[0].strip()
                                
                        # Get editor
                        editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', content)
                        if editor_matches and len(editor_matches[0].strip()) > 0:
                            work_editor = editor_matches[0].strip()
                            
                        # Determine language from filename
                        file_language = None
                        if 'perseus-eng' in file:
                            file_language = 'eng'
                        elif 'perseus-grc' in file:
                            file_language = 'grc'

                        # Use file language if found, otherwise use work language or default to Greek
                        language = file_language or work_language or 'grc'
                            
                        works.append({
                            'id': work_dir,
                            'title': work_title or f"Work {work_dir}",
                            'language': language,
                            'editor': work_editor or 'Unknown',
                            'file_path': file_path
                        })
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
    
    return author_name, works

def get_works_by_editor(editor_name):
    """Get list of works edited by a specific editor."""
    works = []
    
    # Walk through all XML files
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.xml') and not file == '__cts__.xml':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(10000)
                        
                    # Check if this file was edited by our editor
                    editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', content)
                    if editor_matches:
                        for match in editor_matches:
                            if editor_name.lower() in match.lower():
                                # Get work details
                                author_name = "Unknown"
                                author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
                                if author_matches and len(author_matches[0].strip()) > 0:
                                    author_name = author_matches[0].strip()
                                    
                                work_title = "Unknown"
                                title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                                if title_matches:
                                    work_title = title_matches[0].strip()
                                    
                                works.append({
                                    'author': author_name,
                                    'title': work_title,
                                    'file_path': file_path
                                })
                                break
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
    
    return works

def get_author_works_for_api(author_id):
    """
    Get works for an author formatted for the API response.
    
    Args:
        author_id (str): The ID of the author
        
    Returns:
        list: A list of work dictionaries formatted for the API
    """
    _, works_data = get_works_by_author(author_id)
    api_works = []
    
    for work in works_data:
        # Extract the file name from the path
        file_name = os.path.basename(work['file_path'])
        
        # Convert language code to human-readable name
        language_display = "Greek"  # Default
        if 'language' in work:
            if work['language'] == 'eng':
                language_display = "English"
            elif work['language'] == 'grc':
                language_display = "Greek"
            # Add more language mappings as needed
        
        # Format the work for API response
        api_work = {
            'id': work['id'],
            'title': work['title'],
            'language': language_display,
            'files': [{
                'name': file_name,
                'type': file_name.split('.')[-1] if '.' in file_name else 'unknown'
            }]
        }
        
        api_works.append(api_work)
    
    return api_works

def render_works_page(author_id):
    """Generate works listing page for an author."""
    author_name, works = get_works_by_author(author_id)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Works by {author_name}</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/authors-table.css?v={int(time.time())}">
    <style>
        .works-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }}
        .work-card {{
            background-color: #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
        }}
        .work-card:hover {{
            transform: translateY(-5px);
            background-color: #444;
        }}
        .work-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #4299e1;
        }}
        .work-info {{
            color: #aaa;
            font-size: 0.9em;
            margin-bottom: 15px;
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
        .work-actions {{
            display: flex;
            gap: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Works by {author_name}</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
        </div>
        
        <p>Showing {len(works)} works</p>
        
        <div class="works-grid">
"""

    for work in works:
        html += f"""
            <div class="work-card">
                <div class="work-title">{work['title']}</div>
                <div class="work-info">
                    Language: {work['language']}<br>
                    Editor: {work['editor']}
                </div>
                <div class="work-actions">
                    <a href="/view?path={work['file_path']}" class="button">View XML</a>
                    <a href="/reader?path={work['file_path']}" class="button">Open in Reader</a>
                </div>
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>"""
    return html

def render_editor_works_page(editor_name):
    """Generate works listing page for an editor."""
    works = get_works_by_editor(editor_name)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Works edited by {editor_name}</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/authors-table.css?v={int(time.time())}">
    <style>
        .works-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }}
        .work-card {{
            background-color: #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
        }}
        .work-card:hover {{
            transform: translateY(-5px);
            background-color: #444;
        }}
        .work-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #4299e1;
        }}
        .work-info {{
            color: #aaa;
            font-size: 0.9em;
            margin-bottom: 15px;
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
        .work-actions {{
            display: flex;
            gap: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Works edited by {editor_name}</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
        </div>
        
        <p>Showing {len(works)} works</p>
        
        <div class="works-grid">
"""

    for work in works:
        html += f"""
            <div class="work-card">
                <div class="work-title">{work['title']}</div>
                <div class="work-info">
                    Author: {work['author']}
                </div>
                <div class="work-actions">
                    <a href="/view?path={work['file_path']}" class="button">View XML</a>
                    <a href="/reader?path={work['file_path']}" class="button">Open in Reader</a>
                </div>
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>"""
    return html 