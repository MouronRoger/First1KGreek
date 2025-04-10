"""View handlers for First1KGreek Browser."""

import os
import re
import time
from xml.sax.saxutils import escape
from ..config import CSS_DIR

def render_xml_view_page(file_path):
    """Generate XML view page."""
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
            
        # Escape XML for display
        xml_display = escape(xml_content)
        
        # Add syntax highlighting
        xml_display = re.sub(r'(&lt;[^&]*&gt;)', r'<span class="tag">\1</span>', xml_display)
        xml_display = re.sub(r'(&lt;/[^&]*&gt;)', r'<span class="tag">\1</span>', xml_display)
        xml_display = re.sub(r'("[^"]*")', r'<span class="string">\1</span>', xml_display)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>XML View - {work_title}</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/reader.css?v={int(time.time())}">
    <link rel="stylesheet" href="/static/css/dark-theme.css?v={int(time.time())}">
    <style>
        .xml-container {{
            background: #1a1a1a;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            overflow-x: auto;
            font-family: monospace;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        .tag {{
            color: #4299e1;
        }}
        .string {{
            color: #48bb78;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>XML View</h1>
        
        <div class="nav-links">
            <a href="/" class="button">Home</a>
            <a href="/browse/authors" class="button">Browse Authors</a>
            <a href="/browse/editors" class="button">Browse Editors</a>
            <a href="/reader?path={file_path}" class="button">Open in Reader</a>
        </div>
        
        <div class="metadata">
            <p><strong>Author:</strong> {author_name}</p>
            <p><strong>Work:</strong> {work_title}</p>
            <p><strong>Language:</strong> {language}</p>
            <p><strong>File:</strong> {file_path}</p>
        </div>
        
        <div class="xml-container">
{xml_display}
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
        <h1>Error Loading XML</h1>
        <p>Could not load {file_path}: {str(e)}</p>
        <a href="/" class="button">Back to Home</a>
    </div>
</body>
</html>"""

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