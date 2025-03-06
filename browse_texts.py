#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver
import json
from html import escape
import webbrowser
from urllib.parse import parse_qs, urlparse, quote
import re
import threading
import time

PORT = 8000

# Global reference to the server
server_instance = None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Handle shutdown request
        if path == "/shutdown":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="5;url=about:blank" />
                <title>Server Shutdown - First 1K Greek Texts</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0;
                        text-align: center;
                        padding-top: 100px;
                    }
                    h1, h2, h3 { color: #ffffff; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .shutdown-message {
                        padding: 30px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                        margin-top: 30px;
                    }
                    .countdown {
                        font-size: 24px;
                        font-weight: bold;
                        margin-top: 20px;
                        color: #03dac6;
                    }
                </style>
                <script>
                    let countdown = 5;
                    function updateCountdown() {
                        document.getElementById('countdown').innerText = countdown;
                        countdown--;
                        if (countdown >= 0) {
                            setTimeout(updateCountdown, 1000);
                        }
                    }
                    window.onload = function() {
                        updateCountdown();
                    };
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>Server Shutting Down</h1>
                    <div class="shutdown-message">
                        <p>The First 1K Greek Texts server is shutting down.</p>
                        <p>This window will close automatically in <span id="countdown">5</span> seconds.</p>
                        <p>Thank you for using the application!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            
            # Start a separate thread to shut down the server after a short delay
            # to allow the page to be displayed
            shutdown_thread = threading.Thread(target=self.delayed_shutdown)
            shutdown_thread.daemon = True
            shutdown_thread.start()
            
            return
        
        # Serve the HTML interface for the root path
        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>First 1K Greek Texts Browser</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }
                    h1, h2, h3 { color: #ffffff; }
                    a { color: #ffffff; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .text-display { 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px; 
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }
                    .navigation { 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }
                    .author-list { display: flex; flex-wrap: wrap; }
                    .author-item { 
                        margin: 10px; 
                        padding: 15px; 
                        border: 1px solid #333; 
                        background-color: #252525;
                        border-radius: 6px;
                        transition: transform 0.2s;
                    }
                    .author-item:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    }
                    .xml-content { 
                        white-space: pre-wrap; 
                        font-family: monospace; 
                        background-color: #1e1e1e;
                        padding: 10px;
                        border-radius: 4px;
                        border: 1px solid #333;
                    }
                    .greek { 
                        font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', sans-serif; 
                    }
                    .search-form {
                        margin: 20px 0;
                        padding: 15px;
                        background-color: #252525;
                        border-radius: 8px;
                    }
                    .search-form input[type="text"] {
                        width: 70%;
                        padding: 8px;
                        border: 1px solid #555;
                        background-color: #1e1e1e;
                        color: #e0e0e0;
                        border-radius: 4px;
                    }
                    .search-form input[type="submit"] {
                        padding: 8px 16px;
                        background-color: #03dac6;
                        color: #000;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .shutdown-btn {
                        color: #ff5252 !important;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/editors">Browse by Editor</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/search">Search Corpus</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="search-form">
                        <form action="/search" method="get">
                            <input type="text" name="q" placeholder="Search for a phrase in the corpus...">
                            <input type="submit" value="Search">
                        </form>
                    </div>
                    
                    <div class="text-display">
                        <h2>Welcome to the First 1K Greek Texts Browser</h2>
                        <p>This is a simple browser for the First 1K Greek Project texts. The project aims to provide digital versions of Greek texts from the first thousand years of Greek literature.</p>
                        <p>Use the navigation links above to explore the texts by author, editor, or browse the raw files.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
            
        # Serve the authors listing
        elif path == "/authors":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Get authors from data directory
            authors_data = []
            if os.path.exists("data"):
                author_dirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
                
                # Get author names and IDs
                for author_id in author_dirs:
                    author_name = "Unknown"
                    author_cts = os.path.join("data", author_id, "__cts__.xml")
                    if os.path.exists(author_cts):
                        # Very simple XML parsing to get author name
                        try:
                            with open(author_cts, 'r', encoding='utf-8') as f:
                                content = f.read()
                                name_start = content.find("<ti:groupname")
                                if name_start > 0:
                                    name_end = content.find("</ti:groupname>", name_start)
                                    if name_end > 0:
                                        tag_end = content.find(">", name_start)
                                        author_name = content[tag_end+1:name_end].strip()
                        except Exception:
                            pass  # Use default "Unknown" if error
                    
                    # Add to authors data list
                    authors_data.append({"id": author_id, "name": author_name})
                
                # Sort by name (alphabetical)
                authors_data.sort(key=lambda x: x["name"].lower())
            
            # Create HTML for author listing
            author_html = ""
            for author in authors_data:
                author_html += f'<div class="author-item"><h3><a href="/works?author={author["id"]}">{author["name"]} ({author["id"]})</a></h3></div>'
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Authors - First 1K Greek Texts</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }}
                    h1, h2, h3 {{ color: #ffffff; }}
                    a {{ color: #bb86fc; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }}
                    .navigation {{ 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }}
                    .author-list {{ display: flex; flex-wrap: wrap; }}
                    .author-item {{ 
                        margin: 10px; 
                        padding: 15px; 
                        border: 1px solid #333; 
                        background-color: #252525;
                        border-radius: 6px;
                        width: 250px;
                        transition: transform 0.2s;
                    }}
                    .author-item:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>Authors</h2>
                        <p>Showing {len(authors_data)} authors, alphabetically ordered by name</p>
                        <div class="author-list">
                            {author_html}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
            
        # Serve works for a specific author
        elif path == "/works":
            query = parse_qs(parsed_url.query)
            if "author" in query:
                author = query["author"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Get author info
                author_name = author
                author_cts = os.path.join("data", author, "__cts__.xml")
                if os.path.exists(author_cts):
                    with open(author_cts, 'r', encoding='utf-8') as f:
                        content = f.read()
                        name_start = content.find("<ti:groupname")
                        if name_start > 0:
                            name_end = content.find("</ti:groupname>", name_start)
                            if name_end > 0:
                                tag_end = content.find(">", name_start)
                                author_name = content[tag_end+1:name_end].strip()
                
                # Get works
                works_data = []
                author_dir = os.path.join("data", author)
                if os.path.exists(author_dir):
                    work_dirs = [d for d in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, d)) and d != "__cts__"]
                    
                    # Get work titles
                    for work_id in work_dirs:
                        work_title = work_id
                        work_cts = os.path.join("data", author, work_id, "__cts__.xml")
                        if os.path.exists(work_cts):
                            with open(work_cts, 'r', encoding='utf-8') as f:
                                content = f.read()
                                title_start = content.find("<ti:title")
                                if title_start > 0:
                                    title_end = content.find("</ti:title>", title_start)
                                    if title_end > 0:
                                        tag_end = content.find(">", title_start)
                                        work_title = content[tag_end+1:title_end].strip()
                        
                        # Find editions
                        editions = []
                        work_dir = os.path.join("data", author, work_id)
                        if os.path.exists(work_dir):
                            editions = [f for f in os.listdir(work_dir) if f.endswith(".xml") and f != "__cts__.xml"]
                        
                        works_data.append({
                            "id": work_id,
                            "title": work_title,
                            "editions": editions
                        })
                
                    # Sort works alphabetically by title
                    works_data.sort(key=lambda x: x["title"].lower())
                
                # Create HTML for works listing
                works_html = ""
                for work in works_data:
                    editions_html = ""
                    for edition in work["editions"]:
                        editions_html += f'<li><a href="/view?path=data/{author}/{work["id"]}/{edition}">{edition}</a></li>'
                    
                    works_html += f"""
                    <div class="work-item">
                        <h3>{work["title"]} ({work["id"]})</h3>
                        <p>Available editions:</p>
                        <ul class="editions-list">
                            {editions_html}
                        </ul>
                    </div>
                    """
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{author_name} - Works - First 1K Greek Texts</title>
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            margin: 0; 
                            padding: 20px; 
                            line-height: 1.6; 
                            background-color: #121212; 
                            color: #e0e0e0; 
                        }}
                        h1, h2, h3 {{ color: #ffffff; }}
                        a {{ color: #bb86fc; text-decoration: none; }}
                        a:hover {{ text-decoration: underline; }}
                        .container {{ max-width: 1200px; margin: 0 auto; }}
                        .text-display {{ 
                            border: 1px solid #333; 
                            padding: 20px; 
                            margin-top: 20px;
                            background-color: #1e1e1e;
                            border-radius: 8px;
                        }}
                        .navigation {{ 
                            margin-bottom: 20px; 
                            padding: 12px;
                            background-color: #1e1e1e;
                            border-radius: 8px;
                            border: 1px solid #333;
                        }}
                        .work-item {{ 
                            margin-bottom: 25px; 
                            padding-bottom: 20px; 
                            border-bottom: 1px solid #333;
                        }}
                        .work-item:last-child {{
                            border-bottom: none;
                        }}
                        .editions-list {{ 
                            list-style-type: square;
                            padding-left: 20px;
                        }}
                        .editions-list li {{
                            margin: 5px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>First 1K Greek Texts Browser</h1>
                        
                        <div class="navigation">
                            <a href="/">Home</a> | 
                            <a href="/authors">Browse Authors</a> | 
                            <a href="/raw">Browse Raw Files</a> | 
                            <a href="/about">About</a> | 
                            <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                        </div>
                        
                        <div class="text-display">
                            <h2>Works by {author_name} ({author})</h2>
                            {works_html}
                        </div>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
                return
        
        # Search functionality
        elif path == "/search":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            query = parse_qs(parsed_url.query)
            search_term = query.get("q", [""])[0].strip()
            
            search_results = []
            if search_term:
                search_results = self.search_corpus(search_term)
            
            # Create HTML for search results
            results_html = ""
            if search_term:
                if search_results:
                    for result in search_results:
                        # Create a snippet with context
                        context = result["context"]
                        # Highlight the search term
                        highlighted_context = context.replace(search_term, f'<span style="background-color: #03dac6; color: #000; padding: 2px 4px; border-radius: 3px;">{search_term}</span>')
                        
                        results_html += f"""
                        <div class="result-item">
                            <h3><a href="/view?path={result['file_path']}">{result['title']}</a></h3>
                            <p>Author: {result['author']}</p>
                            <p>Editor: {result.get('editor', 'Unknown')}</p>
                            <div class="result-context greek">{highlighted_context}</div>
                            <p class="view-links">
                                <a href="/view?path={result['file_path']}">View in default mode</a> | 
                                <a href="/reader?path={result['file_path']}">View in reader mode</a>
                            </p>
                        </div>
                        """
                else:
                    results_html = "<p>No results found for your search term.</p>"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Search Results - First 1K Greek Texts</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }}
                    h1, h2, h3 {{ color: #ffffff; }}
                    a {{ color: #ffffff; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }}
                    .navigation {{ 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }}
                    .search-form {{
                        margin: 20px 0;
                        padding: 15px;
                        background-color: #252525;
                        border-radius: 8px;
                    }}
                    .search-form input[type="text"] {{
                        width: 70%;
                        padding: 8px;
                        border: 1px solid #555;
                        background-color: #1e1e1e;
                        color: #e0e0e0;
                        border-radius: 4px;
                    }}
                    .search-form input[type="submit"] {{
                        padding: 8px 16px;
                        background-color: #03dac6;
                        color: #000;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }}
                    .result-item {{ 
                        margin-bottom: 30px; 
                        padding: 20px; 
                        background-color: #252525;
                        border-radius: 8px;
                        border-left: 4px solid #03dac6;
                    }}
                    .result-context {{
                        padding: 15px;
                        margin: 10px 0;
                        background-color: #1e1e1e;
                        border-radius: 4px;
                        font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', sans-serif;
                    }}
                    .view-links {{
                        margin-top: 10px;
                        font-size: 0.9em;
                    }}
                    .shutdown-btn {
                        color: #ff5252 !important;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/editors">Browse by Editor</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/search">Search Corpus</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="search-form">
                        <form action="/search" method="get">
                            <input type="text" name="q" value="{escape(search_term)}" placeholder="Search for a phrase in the corpus...">
                            <input type="submit" value="Search">
                        </form>
                    </div>
                    
                    <div class="text-display">
                        <h2>Search Results</h2>
                        <p>{f'Showing {len(search_results)} results for "{escape(search_term)}"' if search_term else 'Enter a search term to find texts in the corpus'}</p>
                        {results_html}
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
        
        # Reader mode for XML files
        elif path == "/reader":
            query = parse_qs(parsed_url.query)
            if "path" in query:
                file_path = query["path"][0]
                if os.path.exists(file_path) and file_path.endswith(".xml"):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Process XML content for readability
                            processed_content = self.process_xml_for_reading(content)
                            
                            # Get metadata
                            author_name = "Unknown"
                            work_title = os.path.basename(file_path)
                            editor_name = "Unknown"
                            
                            # Extract editor from XML if possible
                            editor_matches = re.findall(r'<editor>(.*?)</editor>', content)
                            if editor_matches and len(editor_matches[0].strip()) > 0:
                                editor_name = editor_matches[0]
                            
                            # Try to get the author and work info from the file path
                            path_parts = file_path.split(os.sep)
                            if len(path_parts) >= 4 and path_parts[0] == "data":
                                author_id = path_parts[1]
                                work_id = path_parts[2]
                                
                                # Get author name
                                author_cts = os.path.join("data", author_id, "__cts__.xml")
                                if os.path.exists(author_cts):
                                    with open(author_cts, 'r', encoding='utf-8') as f_author:
                                        author_content = f_author.read()
                                        name_start = author_content.find("<ti:groupname")
                                        if name_start > 0:
                                            name_end = author_content.find("</ti:groupname>", name_start)
                                            if name_end > 0:
                                                tag_end = author_content.find(">", name_start)
                                                author_name = author_content[tag_end+1:name_end].strip()
                                
                                # Get work title
                                work_cts = os.path.join("data", author_id, work_id, "__cts__.xml")
                                if os.path.exists(work_cts):
                                    with open(work_cts, 'r', encoding='utf-8') as f_work:
                                        work_content = f_work.read()
                                        title_start = work_content.find("<ti:title")
                                        if title_start > 0:
                                            title_end = work_content.find("</ti:title>", title_start)
                                            if title_end > 0:
                                                tag_end = work_content.find(">", title_start)
                                                work_title = work_content[tag_end+1:title_end].strip()
                    except Exception as e:
                        processed_content = f"Error reading file: {str(e)}"
                        author_name = "Error"
                        work_title = "Error"
                        editor_name = "Error"
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>{work_title} - Reader Mode - First 1K Greek Texts</title>
                        <style>
                            body {{ 
                                font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
                                margin: 0; 
                                padding: 0;
                                line-height: 1.8; 
                                background-color: #f9f9f9; 
                                color: #000000; 
                            }}
                            h1, h2, h3 {{ 
                                color: #333;
                                font-family: Arial, sans-serif;
                            }}
                            a {{ color: #0066cc; text-decoration: none; }}
                            a:hover {{ text-decoration: underline; }}
                            .container {{ 
                                max-width: 800px; 
                                margin: 0 auto; 
                                padding: 20px;
                                background-color: #ffffff;
                                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                                min-height: 100vh;
                            }}
                            .header {{
                                margin-bottom: 30px;
                                border-bottom: 1px solid #eee;
                                padding-bottom: 20px;
                            }}
                            .metadata {{
                                margin-bottom: 20px;
                                font-style: italic;
                                color: #666;
                            }}
                            .reader-content {{ 
                                font-size: 18px;
                                line-height: 1.8;
                            }}
                            .navigation {{ 
                                margin-bottom: 20px; 
                                padding: 12px;
                                border-bottom: 1px solid #eee;
                            }}
                            .toggle-view {{
                                background-color: #f0f0f0;
                                padding: 10px;
                                border-radius: 4px;
                                margin-top: 20px;
                                text-align: center;
                            }}
                            .xml-section {{
                                margin-bottom: 30px;
                            }}
                            .view-links {
                                margin-top: 10px;
                                font-size: 0.9em;
                            }
                            .shutdown-btn {
                                color: #ff5252 !important;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="navigation">
                                <a href="/">Home</a> | 
                                <a href="/authors">Browse Authors</a> | 
                                <a href="/editors">Browse by Editor</a> | 
                                <a href="/raw">Browse Raw Files</a> | 
                                <a href="/search">Search Corpus</a> | 
                                <a href="/about">About</a> | 
                                <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                            </div>
                            
                            <div class="header">
                                <h1>{work_title}</h1>
                                <div class="metadata">
                                    <p>Author: {author_name}</p>
                                    <p>Editor: {editor_name}</p>
                                </div>
                            </div>
                            
                            <div class="reader-content">
                                {processed_content}
                            </div>
                            
                            <div class="toggle-view">
                                <a href="/view?path={file_path}">Switch to Default View</a>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    self.wfile.write(html.encode())
                    return
        
        # View a specific XML file
        elif path == "/view":
            query = parse_qs(parsed_url.query)
            if "path" in query:
                file_path = query["path"][0]
                if os.path.exists(file_path) and file_path.endswith(".xml"):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            escaped_content = escape(content)
                    except Exception as e:
                        escaped_content = f"Error reading file: {str(e)}"
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>{os.path.basename(file_path)} - First 1K Greek Texts</title>
                        <style>
                            body {{ 
                                font-family: Arial, sans-serif; 
                                margin: 0; 
                                padding: 20px; 
                                line-height: 1.6; 
                                background-color: #121212; 
                                color: #e0e0e0; 
                            }}
                            h1, h2, h3 {{ color: #ffffff; }}
                            a {{ color: #ffffff; text-decoration: none; }}
                            a:hover {{ text-decoration: underline; }}
                            .container {{ max-width: 1200px; margin: 0 auto; }}
                            .text-display {{ 
                                border: 1px solid #333; 
                                padding: 20px; 
                                margin-top: 20px; 
                                overflow: auto;
                                background-color: #1e1e1e;
                                border-radius: 8px;
                            }}
                            .navigation {{ 
                                margin-bottom: 20px; 
                                padding: 12px;
                                background-color: #1e1e1e;
                                border-radius: 8px;
                                border: 1px solid #333;
                            }}
                            .xml-content {{ 
                                white-space: pre-wrap; 
                                font-family: monospace; 
                                background-color: #252525;
                                padding: 15px;
                                border-radius: 4px;
                                border: 1px solid #333;
                                color: #e0e0e0;
                            }}
                            .greek {{ 
                                font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', sans-serif; 
                            }}
                            .path-info {{
                                background-color: #252525;
                                padding: 10px;
                                border-radius: 4px;
                                font-family: monospace;
                                margin-bottom: 15px;
                            }}
                            .toggle-view {{
                                margin-top: 15px;
                                text-align: right;
                            }}
                            .view-links {
                                margin-top: 10px;
                                font-size: 0.9em;
                            }
                            .shutdown-btn {
                                color: #ff5252 !important;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>First 1K Greek Texts Browser</h1>
                            
                            <div class="navigation">
                                <a href="/">Home</a> | 
                                <a href="/authors">Browse Authors</a> | 
                                <a href="/editors">Browse by Editor</a> | 
                                <a href="/raw">Browse Raw Files</a> | 
                                <a href="/search">Search Corpus</a> | 
                                <a href="/about">About</a> | 
                                <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                            </div>
                            
                            <div class="text-display">
                                <h2>{os.path.basename(file_path)}</h2>
                                <div class="path-info">Path: {file_path}</div>
                                <div class="toggle-view">
                                    <a href="/reader?path={file_path}">Switch to Reader Mode</a>
                                </div>
                                <div class="xml-content greek">{escaped_content}</div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    self.wfile.write(html.encode())
                    return
        
        # About page
        elif path == "/about":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>About - First 1K Greek Texts</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }
                    h1, h2, h3 { color: #ffffff; }
                    a { color: #bb86fc; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .text-display { 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }
                    .navigation { 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }
                    .view-links {
                        margin-top: 10px;
                        font-size: 0.9em;
                    }
                    .shutdown-btn {
                        color: #ff5252 !important;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>About the First 1K Greek Project</h2>
                        <p>The First Thousand Years of Greek Project aims to provide digital versions of Greek texts from the first thousand years of Greek literature.</p>
                        <p>The texts are encoded using TEI (Text Encoding Initiative) XML format, providing rich metadata and markup for scholarly use.</p>
                        <p>The project is maintained by the Open Greek and Latin (OGL) initiative.</p>
                        <p>For more information, visit <a href="https://opengreekandlatin.github.io/First1KGreek/" target="_blank">the official project page</a>.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
            
        # Browse raw files
        elif path == "/raw":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Get raw files directory structure
            raw_dirs = []
            if os.path.exists("raw_files"):
                raw_dirs = [d for d in os.listdir("raw_files") if os.path.isdir(os.path.join("raw_files", d))]
                raw_dirs.sort()
            
            # Create HTML for raw directories listing
            raw_html = ""
            for raw_dir in raw_dirs:
                raw_html += f'<div class="raw-item"><h3><a href="/raw_browse?dir=raw_files/{raw_dir}">{raw_dir}</a></h3></div>'
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Raw Files - First 1K Greek Texts</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }}
                    h1, h2, h3 {{ color: #ffffff; }}
                    a {{ color: #bb86fc; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }}
                    .navigation {{ 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }}
                    .raw-list {{ display: flex; flex-wrap: wrap; }}
                    .raw-item {{ 
                        margin: 10px; 
                        padding: 15px; 
                        border: 1px solid #333; 
                        background-color: #252525;
                        border-radius: 6px;
                        width: 250px;
                        transition: transform 0.2s;
                    }}
                    .raw-item:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    }}
                    .view-links {
                        margin-top: 10px;
                        font-size: 0.9em;
                    }
                    .shutdown-btn {
                        color: #ff5252 !important;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>Raw Files</h2>
                        <div class="raw-list">
                            {raw_html}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
            
        # Browse specific raw directory
        elif path == "/raw_browse":
            query = parse_qs(parsed_url.query)
            if "dir" in query:
                dir_path = query["dir"][0]
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    
                    items = os.listdir(dir_path)
                    items.sort()
                    
                    items_html = "<ul class='directory-list'>"
                    for item in items:
                        item_path = os.path.join(dir_path, item)
                        if os.path.isdir(item_path):
                            items_html += f'<li class="dir-item"><a href="/raw_browse?dir={item_path}">{item}/</a></li>'
                        elif item.endswith(".xml"):
                            items_html += f'<li class="xml-item"><a href="/view?path={item_path}">{item}</a></li>'
                        else:
                            items_html += f'<li class="file-item">{item}</li>'
                    items_html += "</ul>"
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Raw Browse - {dir_path} - First 1K Greek Texts</title>
                        <style>
                            body {{ 
                                font-family: Arial, sans-serif; 
                                margin: 0; 
                                padding: 20px; 
                                line-height: 1.6; 
                                background-color: #121212; 
                                color: #e0e0e0; 
                            }}
                            h1, h2, h3 {{ color: #ffffff; }}
                            a {{ color: #bb86fc; text-decoration: none; }}
                            a:hover {{ text-decoration: underline; }}
                            .container {{ max-width: 1200px; margin: 0 auto; }}
                            .text-display {{ 
                                border: 1px solid #333; 
                                padding: 20px; 
                                margin-top: 20px;
                                background-color: #1e1e1e;
                                border-radius: 8px;
                            }}
                            .navigation {{ 
                                margin-bottom: 20px; 
                                padding: 12px;
                                background-color: #1e1e1e;
                                border-radius: 8px;
                                border: 1px solid #333;
                            }}
                            .directory-list {{
                                list-style-type: none;
                                padding-left: 0;
                            }}
                            .directory-list li {{
                                padding: 8px 12px;
                                margin: 4px 0;
                                border-radius: 4px;
                                background-color: #252525;
                            }}
                            .dir-item {{
                                border-left: 4px solid #bb86fc;
                            }}
                            .xml-item {{
                                border-left: 4px solid #03dac6;
                            }}
                            .file-item {{
                                border-left: 4px solid #555;
                            }}
                            .path-info {{
                                background-color: #252525;
                                padding: 10px;
                                border-radius: 4px;
                                font-family: monospace;
                                margin-bottom: 15px;
                            }}
                            .view-links {
                                margin-top: 10px;
                                font-size: 0.9em;
                            }
                            .shutdown-btn {
                                color: #ff5252 !important;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>First 1K Greek Texts Browser</h1>
                            
                            <div class="navigation">
                                <a href="/">Home</a> | 
                                <a href="/authors">Browse Authors</a> | 
                                <a href="/raw">Browse Raw Files</a> | 
                                <a href="/about">About</a> | 
                                <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                            </div>
                            
                            <div class="text-display">
                                <h2>Directory Contents</h2>
                                <div class="path-info">{dir_path}</div>
                                {items_html}
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    self.wfile.write(html.encode())
                    return
        
        # Browse by editors
        elif path == "/editors":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Get a list of all editors
            editors_data = self.get_editors_data()
            
            # Create HTML for editor listing
            editor_html = ""
            for editor in editors_data:
                work_count = len(editor["works"])
                if work_count > 0:
                    editor_html += f'''
                    <div class="editor-item">
                        <h3><a href="/editor_works?name={editor["name"]}">{editor["name"]}</a></h3>
                        <p>Edited {work_count} work{"s" if work_count != 1 else ""}</p>
                    </div>
                    '''
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Editors - First 1K Greek Texts</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6; 
                        background-color: #121212; 
                        color: #e0e0e0; 
                    }}
                    h1, h2, h3 {{ color: #ffffff; }}
                    a {{ color: #bb86fc; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ 
                        border: 1px solid #333; 
                        padding: 20px; 
                        margin-top: 20px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                    }}
                    .navigation {{ 
                        margin-bottom: 20px; 
                        padding: 12px;
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        border: 1px solid #333;
                    }}
                    .editor-list {{ display: flex; flex-wrap: wrap; }}
                    .editor-item {{ 
                        margin: 10px; 
                        padding: 15px; 
                        border: 1px solid #333; 
                        background-color: #252525;
                        border-radius: 6px;
                        width: 300px;
                        transition: transform 0.2s;
                    }}
                    .editor-item:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    }}
                    .featured {{ 
                        border-left: 4px solid #03dac6; 
                        background-color: #1e352f;
                    }}
                    .view-links {
                        margin-top: 10px;
                        font-size: 0.9em;
                    }
                    .shutdown-btn {
                        color: #ff5252 !important;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/editors">Browse by Editor</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a> | 
                        <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>Editors</h2>
                        <p>Showing {len(editors_data)} editors with their edited works</p>
                        
                        <h3 style="margin-top:20px;">Featured Editor</h3>
                        <div class="editor-item featured">
                            <h3><a href="/editor_works?name=Hans Friedrich August von Arnim">Hans Friedrich August von Arnim</a></h3>
                            <p>German classical scholar (1859-1931) who specialized in Greek philosophy and rhetoric</p>
                            <p>Click to view works edited by von Arnim</p>
                        </div>
                        
                        <h3 style="margin-top:20px;">All Editors</h3>
                        <div class="editor-list">
                            {editor_html}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            return
            
        # Show works by a specific editor
        elif path == "/editor_works":
            query = parse_qs(parsed_url.query)
            if "name" in query:
                editor_name = query["name"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Find works by this editor
                editors_data = self.get_editors_data()
                editor_works = []
                
                for editor in editors_data:
                    if editor["name"] == editor_name:
                        editor_works = editor["works"]
                        break
                
                # Sort works by title
                editor_works.sort(key=lambda x: x["title"].lower())
                
                # Create HTML for works listing
                works_html = ""
                for work in editor_works:
                    works_html += f"""
                    <div class="work-item">
                        <h3>{work["title"]}</h3>
                        <p>Author: {work["author_name"]} ({work["author_id"]})</p>
                        <p>Work ID: {work["work_id"]}</p>
                        <p><a href="/view?path={work["file_path"]}">View Text</a></p>
                    </div>
                    """
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Works by {editor_name} - First 1K Greek Texts</title>
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            margin: 0; 
                            padding: 20px; 
                            line-height: 1.6; 
                            background-color: #121212; 
                            color: #e0e0e0; 
                        }}
                        h1, h2, h3 {{ color: #ffffff; }}
                        a {{ color: #bb86fc; text-decoration: none; }}
                        a:hover {{ text-decoration: underline; }}
                        .container {{ max-width: 1200px; margin: 0 auto; }}
                        .text-display {{ 
                            border: 1px solid #333; 
                            padding: 20px; 
                            margin-top: 20px;
                            background-color: #1e1e1e;
                            border-radius: 8px;
                        }}
                        .navigation {{ 
                            margin-bottom: 20px; 
                            padding: 12px;
                            background-color: #1e1e1e;
                            border-radius: 8px;
                            border: 1px solid #333;
                        }}
                        .work-item {{ 
                            margin-bottom: 25px; 
                            padding: 20px; 
                            border-bottom: 1px solid #333;
                            background-color: #252525;
                            border-radius: 6px;
                        }}
                        .work-item:last-child {{
                            border-bottom: none;
                        }}
                        .view-links {
                            margin-top: 10px;
                            font-size: 0.9em;
                        }
                        .shutdown-btn {
                            color: #ff5252 !important;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>First 1K Greek Texts Browser</h1>
                        
                        <div class="navigation">
                            <a href="/">Home</a> | 
                            <a href="/authors">Browse Authors</a> | 
                            <a href="/editors">Browse by Editor</a> | 
                            <a href="/raw">Browse Raw Files</a> | 
                            <a href="/about">About</a> | 
                            <a href="/shutdown" class="shutdown-btn" onclick="return confirm('Are you sure you want to shut down the server?')">Shutdown Server</a>
                        </div>
                        
                        <div class="text-display">
                            <h2>Works edited by {editor_name}</h2>
                            <p>Found {len(editor_works)} works</p>
                            {works_html}
                        </div>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
                return
        
        # Default: let the SimpleHTTPRequestHandler handle it
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def get_editors_data(self):
        """Extract all editors and their edited works from the data directory"""
        editors = {}
        
        # Walk through all XML files in the data directory
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".xml") and file != "__cts__.xml":
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Extract editor information using regex for better matching
                            editor_matches = re.findall(r'<editor>(.*?)</editor>', content)
                            
                            if editor_matches:
                                for editor_name in editor_matches:
                                    # Skip empty or too short editor names
                                    if len(editor_name.strip()) < 3:
                                        continue
                                        
                                    # Create entry for this editor if it doesn't exist
                                    if editor_name not in editors:
                                        editors[editor_name] = []
                                    
                                    # Get author and work information
                                    path_parts = file_path.split(os.sep)
                                    if len(path_parts) >= 4 and path_parts[0] == "data":
                                        author_id = path_parts[1]
                                        work_id = path_parts[2]
                                        
                                        # Get author name
                                        author_name = author_id
                                        author_cts = os.path.join("data", author_id, "__cts__.xml")
                                        if os.path.exists(author_cts):
                                            with open(author_cts, 'r', encoding='utf-8') as f_author:
                                                author_content = f_author.read()
                                                name_start = author_content.find("<ti:groupname")
                                                if name_start > 0:
                                                    name_end = author_content.find("</ti:groupname>", name_start)
                                                    if name_end > 0:
                                                        tag_end = author_content.find(">", name_start)
                                                        author_name = author_content[tag_end+1:name_end].strip()
                                        
                                        # Get work title
                                        work_title = work_id
                                        work_cts = os.path.join("data", author_id, work_id, "__cts__.xml")
                                        if os.path.exists(work_cts):
                                            with open(work_cts, 'r', encoding='utf-8') as f_work:
                                                work_content = f_work.read()
                                                title_start = work_content.find("<ti:title")
                                                if title_start > 0:
                                                    title_end = work_content.find("</ti:title>", title_start)
                                                    if title_end > 0:
                                                        tag_end = work_content.find(">", title_start)
                                                        work_title = work_content[tag_end+1:title_end].strip()
                                        
                                        # Add work to this editor's list if not already present
                                        work_info = {
                                            "author_id": author_id,
                                            "author_name": author_name,
                                            "work_id": work_id,
                                            "title": work_title,
                                            "file_path": file_path
                                        }
                                        
                                        # Check if this work is already in the editor's list
                                        if not any(w["file_path"] == file_path for w in editors[editor_name]):
                                            editors[editor_name].append(work_info)
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
        
        # Convert to a list format for easier use
        editors_list = [{"name": name, "works": works} for name, works in editors.items()]
        
        # Sort editors by name
        editors_list.sort(key=lambda x: x["name"].lower())
        
        return editors_list
        
    def search_corpus(self, search_term):
        """Search for a phrase in all XML files and return results with context"""
        results = []
        
        # Walk through all XML files in the data directory
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".xml") and file != "__cts__.xml":
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Check if search term exists in the content
                            if search_term.lower() in content.lower():
                                # Get context around the search term (case insensitive search)
                                content_lower = content.lower()
                                positions = []
                                start_pos = 0
                                
                                while True:
                                    pos = content_lower.find(search_term.lower(), start_pos)
                                    if pos == -1:
                                        break
                                    positions.append(pos)
                                    start_pos = pos + len(search_term)
                                
                                # If found, get metadata and context
                                if positions:
                                    # Get author and work info
                                    path_parts = file_path.split(os.sep)
                                    if len(path_parts) >= 4 and path_parts[0] == "data":
                                        author_id = path_parts[1]
                                        work_id = path_parts[2]
                                        
                                        # Get author name
                                        author_name = author_id
                                        author_cts = os.path.join("data", author_id, "__cts__.xml")
                                        if os.path.exists(author_cts):
                                            with open(author_cts, 'r', encoding='utf-8') as f_author:
                                                author_content = f_author.read()
                                                name_start = author_content.find("<ti:groupname")
                                                if name_start > 0:
                                                    name_end = author_content.find("</ti:groupname>", name_start)
                                                    if name_end > 0:
                                                        tag_end = author_content.find(">", name_start)
                                                        author_name = author_content[tag_end+1:name_end].strip()
                                        
                                        # Get work title
                                        work_title = work_id
                                        work_cts = os.path.join("data", author_id, work_id, "__cts__.xml")
                                        if os.path.exists(work_cts):
                                            with open(work_cts, 'r', encoding='utf-8') as f_work:
                                                work_content = f_work.read()
                                                title_start = work_content.find("<ti:title")
                                                if title_start > 0:
                                                    title_end = work_content.find("</ti:title>", title_start)
                                                    if title_end > 0:
                                                        tag_end = work_content.find(">", title_start)
                                                        work_title = work_content[tag_end+1:title_end].strip()
                                        
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
        """Process XML content for reader-friendly display"""
        # This is a simplified XML processor for reading
        # You would likely want a more sophisticated parser for production use
        
        # First, escape the content to prevent script injection
        content = escape(xml_content)
        
        # Extract and format the actual text content more readably
        # This is a simplified approach - a real implementation would use a proper XML parser
        
        # Remove XML declaration and other processing instructions
        content = re.sub(r'<\?[^>]*\?>', '', content)
        
        # Replace line breaks with HTML line breaks
        content = content.replace('\n', '<br>')
        
        # Split into sections for better readability
        sections = []
        
        # Check for div type="textpart" elements
        parts = re.split(r'(&lt;div type="textpart"[^>]*&gt;)', content)
        
        if len(parts) > 1:
            current_section = ""
            for i, part in enumerate(parts):
                if i % 2 == 1:  # This is a div start tag
                    # Extract section number or label if available
                    section_label = re.search(r'n="([^"]*)"', part)
                    if section_label:
                        if current_section:  # Add the previous section
                            sections.append(f'<div class="xml-section">{current_section}</div>')
                        current_section = f'<h3>Section {section_label.group(1)}</h3>'
                    else:
                        current_section += part
                else:
                    current_section += part
            
            # Add the last section
            if current_section:
                sections.append(f'<div class="xml-section">{current_section}</div>')
        else:
            # If no section divs found, just use the whole content
            sections.append(f'<div class="xml-section">{content}</div>')
        
        return ''.join(sections)

    def delayed_shutdown(self):
        """Shut down the server after a short delay to allow the response to be sent"""
        time.sleep(2)  # Wait for the response to be sent
        print("Server shutting down...")
        global server_instance
        if server_instance:
            server_instance.shutdown()

def add_shutdown_button(html):
    """Add a shutdown button to the HTML navigation bar"""
    # Find the navigation div
    nav_start = html.find('<div class="navigation">')
    if nav_start > 0:
        nav_end = html.find('</div>', nav_start)
        if nav_end > 0:
            # Get the navigation content
            nav_content = html[nav_start:nav_end]
            # Add the shutdown button
            shutdown_button = ' | <a href="/shutdown" style="color: #ff5252;" onclick="return confirm(\'Are you sure you want to shut down the server?\')">Shutdown Server</a>'
            modified_nav = nav_content + shutdown_button
            # Replace the navigation content
            return html[:nav_start] + modified_nav + html[nav_end:]
    
    # If we couldn't find the navigation, return the original HTML
    return html

def run_server():
    global server_instance
    server_instance = socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler)
    print(f"Server running at http://localhost:{PORT}/")
    webbrowser.open(f"http://localhost:{PORT}/")
    
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        server_instance.server_close()
        print("Server closed")

if __name__ == "__main__":
    run_server() 