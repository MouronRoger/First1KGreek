"""View handlers for First1KGreek Browser."""

import os
import re
import time
import json
import logging
from xml.sax.saxutils import escape
from ..config import CSS_DIR, DATA_DIR

# Set up logging
logger = logging.getLogger(__name__)

def handle_view_xml(query_params):
    """
    Handle request to view XML file.
    
    Args:
        query_params (dict): Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, html)
    """
    path = query_params.get('path', '')
    
    # Normalize paths - handle both absolute and relative paths
    if not path:
        return 400, 'text/html', "<h1>Error: No path specified</h1>"
    
    # Convert absolute path to relative path if it's an absolute path containing the data directory
    # This is crucial for compatibility between HTTP and FastAPI modes
    logger.info(f"Original path requested: {path}")
    
    # If it's an absolute path that contains our data directory
    if os.path.isabs(path) and DATA_DIR in path:
        # Extract the relative part of the path from the data directory
        relative_path = os.path.relpath(path, os.path.dirname(DATA_DIR))
        logger.info(f"Converted absolute path to relative: {relative_path}")
        path = relative_path
    
    # Ensure the path is properly formatted for the file system
    if not os.path.isabs(path):
        # If it's already a relative path, make sure it's relative to data directory
        if not path.startswith("data/"):
            path = os.path.join("data", path)
        full_path = os.path.join(os.path.dirname(DATA_DIR), path)
    else:
        full_path = path
    
    logger.info(f"Resolved full path: {full_path}")
    
    if not os.path.exists(full_path):
        error_msg = f"<h1>Error: File not found</h1><p>Could not find file at path: {path}</p>"
        logger.error(f"File not found: {full_path}")
        return 404, 'text/html', error_msg
    
    # Try to read the file
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        error_msg = f"<h1>Error: Failed to read file</h1><p>Error: {str(e)}</p>"
        logger.error(f"Failed to read file {full_path}: {str(e)}")
        return 500, 'text/html', error_msg
    
    # Format the content for display
    html_content = format_xml_for_display(content)
    
    # Get metadata
    dirname = os.path.dirname(full_path)
    basename = os.path.basename(full_path)
    
    # Get author name and work title
    author_id = None
    work_id = None
    
    # Try to extract author_id and work_id from the path
    parts = dirname.split('/')
    for part in parts:
        if part.startswith('tlg') or part.startswith('ggm') or part.startswith('heb'):
            author_id = part
            break
    
    if author_id:
        for part in parts:
            if part.startswith('tlg') and part != author_id:
                work_id = part
                break
    
    author_name = author_id if not author_id else get_author_name(author_id)
    work_title = work_id if not work_id else get_work_title(author_id, work_id)
    
    # Determine language from filename or content
    language = "Greek"  # Default
    if "perseus-eng" in basename:
        language = "English"
    elif "perseus-grc" in basename:
        language = "Greek"
    else:
        # Try to detect from content
        if 'xml:lang="eng"' in content:
            language = "English"
        elif 'xml:lang="grc"' in content:
            language = "Greek"
    
    # Render the page
    html = generate_xml_view_html(
        html_content,
        path,
        author_name,
        work_title,
        language,
        full_path
    )
    
    return 200, 'text/html', html

def handle_view_text(query_params, post_data=None):
    """Handle request to view plain text content.
    
    Args:
        query_params: Query parameters from the request
        post_data: POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    file_path = query_params.get('path', None)
    
    if not file_path:
        return 400, 'text/html', "<h1>Error</h1><p>No file path specified</p>"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove XML tags
        text_content = re.sub(r'<[^>]+>', '', content)
        return 200, 'text/plain', text_content
    except Exception as e:
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render text view: {str(e)}</p>"

def handle_view_reader(query_params, post_data=None):
    """Handle request to view content in reader mode.
    
    Args:
        query_params: Query parameters from the request
        post_data: POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    file_path = query_params.get('path', None)
    
    if not file_path:
        return 400, 'text/html', "<h1>Error</h1><p>No file path specified</p>"
    
    try:
        html = render_reader_view_page(file_path)
        return 200, 'text/html', html
    except Exception as e:
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render reader view: {str(e)}</p>"

def handle_view_raw(query_params, post_data=None):
    """Handle request to view raw file content.
    
    Args:
        query_params: Query parameters from the request
        post_data: POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    file_path = query_params.get('path', None)
    
    if not file_path:
        return 400, 'text/html', "<h1>Error</h1><p>No file path specified</p>"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine content type based on file extension
        if file_path.endswith('.xml'):
            return 200, 'application/xml', content
        elif file_path.endswith('.txt'):
            return 200, 'text/plain', content
        elif file_path.endswith('.html') or file_path.endswith('.htm'):
            return 200, 'text/html', content
        else:
            return 200, 'text/plain', content
    except Exception as e:
        return 500, 'text/html', f"<h1>Error</h1><p>Failed to render raw view: {str(e)}</p>"

def format_xml_for_display(content):
    """
    Format XML content for display with syntax highlighting.
    
    Args:
        content (str): XML content to format
        
    Returns:
        str: HTML-formatted XML content
    """
    # Escape HTML entities
    content = escape(content)
    
    # Highlight XML tags
    content = re.sub(r'(&lt;[^&]*?&gt;)', r'<span class="tag">\1</span>', content)
    
    # Highlight attributes
    content = re.sub(r'(\s+\w+)(\s*=\s*"[^"]*")', r'<span class="attr-name">\1</span><span class="attr-value">\2</span>', content)
    
    # Format with line numbers
    lines = content.split('\n')
    formatted_lines = []
    for i, line in enumerate(lines):
        formatted_lines.append(f'<div class="line"><span class="line-number">{i+1}</span><span class="line-content">{line}</span></div>')
    
    return '<div class="xml-content">' + '\n'.join(formatted_lines) + '</div>'

def get_author_name(author_id):
    """
    Get author name from author_id.
    
    Args:
        author_id (str): Author ID like 'tlg0032'
        
    Returns:
        str: Author name or ID if not found
    """
    # Try to read from authors_data.json
    authors_file = os.path.join(os.path.dirname(DATA_DIR), "authors_data.json")
    if os.path.exists(authors_file):
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors_data = json.load(f)
                if author_id in authors_data:
                    return authors_data[author_id].get("name", author_id)
        except Exception as e:
            logger.error(f"Error reading authors data: {str(e)}")
    
    return author_id

def get_work_title(author_id, work_id):
    """
    Get work title from author_id and work_id.
    
    Args:
        author_id (str): Author ID like 'tlg0032'
        work_id (str): Work ID like 'tlg006'
        
    Returns:
        str: Work title or work_id if not found
    """
    # Try to read from __cts__.xml in the work directory
    cts_file = os.path.join(DATA_DIR, author_id, work_id, "__cts__.xml")
    if os.path.exists(cts_file):
        try:
            with open(cts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find the title element
                title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                if title_match:
                    return title_match.group(1).strip()
        except Exception as e:
            logger.error(f"Error reading work metadata: {str(e)}")
    
    return work_id

def generate_xml_view_html(content, path, author_name, work_title, language, full_path):
    """
    Generate HTML for XML view page.
    
    Args:
        content (str): Formatted XML content
        path (str): File path
        author_name (str): Author name
        work_title (str): Work title
        language (str): Language of the work
        full_path (str): Full path to the file
        
    Returns:
        str: Complete HTML page
    """
    timestamp = int(time.time())
    css_url = f"/static/css/xml-view.css?v={timestamp}"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML View - {os.path.basename(path)}</title>
    <link rel="stylesheet" href="{css_url}">
    <style>
        body {{
            background-color: #121212;
            color: #f8f8f8;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: #1e1e1e;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .metadata {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #1e1e1e;
            border-radius: 5px;
        }}
        .metadata table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .metadata td {{
            padding: 8px;
            border-bottom: 1px solid #333;
        }}
        .metadata td:first-child {{
            font-weight: bold;
            width: 150px;
        }}
        .xml-content {{
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .line {{
            display: flex;
            padding: 1px 0;
        }}
        .line:hover {{
            background-color: #333;
        }}
        .line-number {{
            color: #666;
            text-align: right;
            padding-right: 10px;
            user-select: none;
            min-width: 40px;
        }}
        .line-content {{
            flex: 1;
            white-space: pre;
        }}
        .tag {{
            color: #569cd6;
        }}
        .attr-name {{
            color: #9cdcfe;
        }}
        .attr-value {{
            color: #ce9178;
        }}
        .actions {{
            margin-bottom: 20px;
        }}
        .actions a {{
            display: inline-block;
            margin-right: 10px;
            padding: 8px 15px;
            background-color: #0366d6;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }}
        .actions a:hover {{
            background-color: #0256b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>XML View: {os.path.basename(path)}</h1>
        </header>
        
        <div class="actions">
            <a href="javascript:history.back()">Back</a>
            <a href="/reader?path={path}">Reader View</a>
        </div>
        
        <div class="metadata">
            <table>
                <tr>
                    <td>Author:</td>
                    <td>{author_name}</td>
                </tr>
                <tr>
                    <td>Work:</td>
                    <td>{work_title}</td>
                </tr>
                <tr>
                    <td>Language:</td>
                    <td>{language}</td>
                </tr>
                <tr>
                    <td>File:</td>
                    <td>{full_path}</td>
                </tr>
            </table>
        </div>
        
        {content}
    </div>
</body>
</html>"""

def render_xml_view_page(file_path):
    """
    Render XML file with syntax highlighting.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        str: HTML with syntax-highlighted XML
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"""<h1>Error: File not found</h1><p>Could not find file at path: {file_path}</p>"""
            
        # Read the XML file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Format XML for display
        html_content = format_xml_for_display(content)
        
        # Get metadata
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        # Try to extract author_id and work_id from path
        parts = dirname.split('/')
        author_id = None
        work_id = None
        
        for part in parts:
            if part.startswith('tlg') or part.startswith('ggm') or part.startswith('heb'):
                author_id = part
                break
                
        if author_id:
            for part in parts:
                if part.startswith('tlg') and part != author_id:
                    work_id = part
                    break
                    
        # Get author name and work title
        author_name = author_id if not author_id else get_author_name(author_id)
        work_title = work_id if not work_id else get_work_title(author_id, work_id)
        
        # Determine language from filename
        language = "Greek"  # Default
        if "perseus-eng" in basename:
            language = "English"
        elif "perseus-grc" in basename:
            language = "Greek"
        
        # Generate the HTML page
        return generate_xml_view_html(
            html_content,
            file_path,
            author_name,
            work_title,
            language,
            file_path
        )
        
    except Exception as e:
        return f"""<h1>Error Loading XML</h1><p>Could not load {file_path}: {str(e)}</p>"""

def render_reader_view_page(file_path):
    """Generate reader view page."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Extract metadata
        author_name = "Unknown"
        author_matches = re.findall(r'<author.*?>(.*?)</author>', xml_content)
        if author_matches and len(author_matches[0].strip()) > 0:
            author_name = author_matches[0]
            
        work_title = "Unknown"
        title_matches = re.findall(r'<title.*?>(.*?)</title>', xml_content)
        if title_matches:
            work_title = title_matches[0]
            
        # Determine language from filename for Perseus texts
        language = "Greek"  # Default
        if 'perseus-eng' in file_path:
            language = "English"
        elif 'perseus-grc' in file_path:
            language = "Greek"
            
        # Extract text content
        # Remove XML tags but preserve line breaks
        text_content = re.sub(r'<[^>]+>', '', xml_content)
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = text_content.strip()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Reader - {work_title}</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/reader.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
    <style>
        .reader-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            border-radius: 5px;
            line-height: 1.6;
            font-size: 18px;
        }}
        .reader-text {{
            white-space: pre-wrap;
            font-family: 'Times New Roman', serif;
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
        .metadata {{
            background: #2a4365;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(26, 32, 44, 0.9);
            padding: 10px;
            border-radius: 5px;
            display: flex;
            gap: 10px;
        }}
        .controls button {{
            background: #4299e1;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
        }}
        .controls button:hover {{
            background: #3182ce;
        }}
    </style>
    <script>
        function increaseFontSize() {{
            var text = document.querySelector('.reader-text');
            var style = window.getComputedStyle(text, null).getPropertyValue('font-size');
            var currentSize = parseFloat(style);
            text.style.fontSize = (currentSize + 2) + 'px';
        }}
        
        function decreaseFontSize() {{
            var text = document.querySelector('.reader-text');
            var style = window.getComputedStyle(text, null).getPropertyValue('font-size');
            var currentSize = parseFloat(style);
            if (currentSize > 12) {{
                text.style.fontSize = (currentSize - 2) + 'px';
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Reader View</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
            <a href="/view?path={file_path}" class="button">View XML</a>
        </div>
        
        <div class="metadata">
            <p><strong>Author:</strong> {author_name}</p>
            <p><strong>Work:</strong> {work_title}</p>
            <p><strong>Language:</strong> {language}</p>
        </div>
        
        <div class="reader-container">
            <div class="reader-text">
{text_content}
            </div>
        </div>
        
        <div class="controls">
            <button onclick="increaseFontSize()">A+</button>
            <button onclick="decreaseFontSize()">A-</button>
        </div>
    </div>
</body>
</html>"""
        return html
        
    except Exception as e:
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
</head>
<body>
    <div class="container">
        <h1>Error Loading Text</h1>
        <p>Could not load {file_path}: {str(e)}</p>
        <a href="/" class="button">Back to Home</a>
    </div>
</body>
</html>"""

async def async_render_xml_view_page(file_path):
    """Async wrapper for render_xml_view_page.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        str: HTML with syntax-highlighted XML
    """
    return render_xml_view_page(file_path)


async def async_render_reader_view_page(file_path):
    """Async wrapper for render_reader_view_page.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        str: HTML with reader-friendly content
    """
    return render_reader_view_page(file_path)


async def async_handle_view_xml(query_params):
    """Async wrapper for handle_view_xml.
    
    Args:
        query_params (dict): Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, html)
    """
    return handle_view_xml(query_params)


async def async_handle_view_reader(query_params):
    """Async wrapper for handle_view_reader.
    
    Args:
        query_params (dict): Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, html)
    """
    path = query_params.get('path', '')
    
    # Normalize paths - handle both absolute and relative paths
    if not path:
        return 400, 'text/html', "<h1>Error: No path specified</h1>"
    
    # Convert absolute path to relative path if it's an absolute path containing the data directory
    logger.info(f"Reader - Original path requested: {path}")
    
    # If it's an absolute path that contains our data directory
    if os.path.isabs(path) and DATA_DIR in path:
        # Extract the relative part of the path from the data directory
        relative_path = os.path.relpath(path, os.path.dirname(DATA_DIR))
        logger.info(f"Reader - Converted absolute path to relative: {relative_path}")
        path = relative_path
    
    # Ensure the path is properly formatted for the file system
    if not os.path.isabs(path):
        # If it's already a relative path, make sure it's relative to data directory
        if not path.startswith("data/"):
            path = os.path.join("data", path)
        full_path = os.path.join(os.path.dirname(DATA_DIR), path)
    else:
        full_path = path
    
    logger.info(f"Reader - Resolved full path: {full_path}")
    
    # Pass the updated path to the original reader handler
    query_params['path'] = full_path
    return handle_view_reader(query_params)


async def async_handle_view_raw(query_params, post_data=None):
    """Async wrapper for handle_view_raw.
    
    Args:
        query_params: Query parameters from the request
        post_data: POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    return handle_view_raw(query_params, post_data) 