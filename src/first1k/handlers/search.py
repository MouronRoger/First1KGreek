"""Search handlers for First1KGreek Browser."""

import os
import re
import time
from ..config import CSS_DIR

def search_corpus(search_term):
    """Search for the given term in all XML files."""
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
                            "context": context,
                            "occurrence_count": len(positions)
                        })
                except Exception as e:
                    print(f"Error searching {file_path}: {str(e)}")
    
    # Sort results by number of occurrences
    results.sort(key=lambda x: x["occurrence_count"], reverse=True)
    
    return results

async def async_search_corpus(search_term):
    """Async wrapper for search_corpus.
    
    Args:
        search_term: Text to search for
        
    Returns:
        list: List of search results
    """
    return search_corpus(search_term)

def handle_search_request(query_params, post_data=None):
    """Handle search request from the user.
    
    Args:
        query_params: Query parameters from the request
        post_data: POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    search_term = query_params.get('q', None)
    
    if not search_term:
        # Show empty search page if no query
        html = render_search_page()
        return 200, 'text/html', html
    
    try:
        # Perform search and render results
        html = render_search_page(search_term)
        return 200, 'text/html', html
    except Exception as e:
        error_html = f"""
        <html>
        <head><title>Search Error</title></head>
        <body>
            <h1>Search Error</h1>
            <p>An error occurred while searching: {str(e)}</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """
        return 500, 'text/html', error_html

def render_search_page(search_term=None):
    """Generate search results page."""
    results = []
    
    if search_term:
        results = search_corpus(search_term)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>First1K Greek - Search</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/styles.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
    <style>
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
            border-radius: 4px;
        }}
        .search-box button {{
            padding: 10px 20px;
            background: #3182ce;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 4px;
            margin-left: 10px;
        }}
        .search-box button:hover {{
            background: #2c5282;
        }}
        .result-item {{
            margin: 15px 0;
            padding: 15px;
            background: #333;
            border-radius: 5px;
        }}
        .result-item:hover {{
            background: #444;
        }}
        .result-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #4299e1;
        }}
        .result-info {{
            color: #aaa;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .result-context {{
            margin-top: 10px;
            padding: 10px;
            background: #2d2d2d;
            border-radius: 3px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        .highlight {{
            background-color: #2c5282;
            color: white;
            padding: 2px 4px;
            border-radius: 2px;
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
        <h1>Search</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
        </div>
        
        <div class="search-box">
            <form action="/search" method="get">
                <input type="text" name="q" value="{search_term or ''}" placeholder="Enter search term...">
                <button type="submit">Search</button>
            </form>
        </div>
"""

    if search_term:
        html += f"<h2>Results for: {search_term}</h2>"
        
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
                    <a href="/view?path={result["file_path"]}" class="button">View XML</a>
                    <a href="/reader?path={result["file_path"]}" class="button">Open in Reader</a>
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
    return html 