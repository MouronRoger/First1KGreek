#!/usr/bin/env python3
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

# Create a backup of the file if it doesn't exist already
if not os.path.exists('browse_texts.py.bak'):
    shutil.copy('browse_texts.py', 'browse_texts.py.bak')

PORT = 8000

# Global reference to the server
server_instance = None

# Reader mode stylesheet
READER_STYLESHEET = """
body { 
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.8; 
    background-color: #f9f9f9; 
    color: #000000; 
}
h1, h2, h3 { 
    color: #333;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 800px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #ffffff;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    min-height: 100vh;
}
""" 

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
    
    # Add basic styling for readability
    html = f'''
    <div class="xml-content">
        <pre style="white-space: pre-wrap; font-family: monospace; line-height: 1.4; padding: 15px; background-color: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; overflow-x: auto;">{clean_content}</pre>
    </div>
    '''
    return html 

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
        # Parse the URL and get query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Handle different routes
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_home_page().encode())
        elif path == '/authors':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_authors_page().encode())
        elif path == '/editors':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_editors_page().encode())
        elif path == '/works' and 'author' in query_params:
            author_id = query_params['author'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_works_page(author_id).encode())
        elif path == '/editor_works' and 'name' in query_params:
            editor_name = query_params['name'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_editor_works_page(editor_name).encode())
        elif path == '/view' and 'path' in query_params:
            file_path = query_params['path'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_view_page(file_path).encode())
        elif path == '/reader' and 'path' in query_params:
            file_path = query_params['path'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_reader_page(file_path).encode())
        elif path == '/search':
            search_term = query_params.get('q', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_search_page(search_term).encode())
        elif path == '/shutdown':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head>
                <title>Server Shutdown</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    h1 { color: #333; }
                    .message { padding: 20px; background-color: #f0f0f0; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Server Shutdown</h1>
                <div class="message">
                    <p>The server is shutting down...</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            threading.Thread(target=self.delayed_shutdown).start()
        else:
            # Attempt to serve a static file
            try:
                super().do_GET()
            except Exception as e:
                self.send_error(404, f"File not found: {self.path}")
                print(f"Error serving {self.path}: {str(e)}")

    def delayed_shutdown(self):
        """Delay the shutdown to allow the response to be sent"""
        time.sleep(1)
        global server_instance
        if server_instance:
            print("Server stopped by user")
            server_instance.shutdown()
            print("Server closed")
            server_instance = None

    def get_home_page(self):
        """Generate the home page HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Text Browser</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }
                .container { max-width: 900px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .nav { margin: 20px 0; }
                .nav a { display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }
                .nav a:hover { background: #004080; }
                .search-box { margin: 30px 0; padding: 20px; background: #f8f8f8; border-radius: 5px; }
                .search-box input[type="text"] { padding: 10px; width: 70%; border: 1px solid #ddd; }
                .search-box button { padding: 10px 20px; background: #0066cc; color: white; border: none; cursor: pointer; }
                .about { margin-top: 40px; padding: 20px; background: #f0f0f0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>First1K Greek - Text Browser</h1>
                
                <div class="nav">
                    <a href="/authors">Browse Authors</a>
                    <a href="/editors">Browse Editors</a>
                    <a href="/search">Search</a>
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
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_authors_page(self):
        """Generate the authors listing page"""
        # Get author directories from the data folder
        author_dirs = []
        for item in os.listdir('data'):
            item_path = os.path.join('data', item)
            if os.path.isdir(item_path) and (item.startswith('tlg') or item.startswith('heb')):
                author_dirs.append(item)
        
        # Sort the author directories
        author_dirs.sort()
        
        # Build the HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Authors</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }
                .container { max-width: 900px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .nav { margin: 20px 0; }
                .nav a { display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }
                .nav a:hover { background: #004080; }
                .author-list { margin-top: 20px; }
                .author-item { padding: 10px; border-bottom: 1px solid #eee; }
                .author-item:hover { background: #f8f8f8; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Authors</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/editors">Browse Editors</a>
                    <a href="/search">Search</a>
                </div>
                
                <div class="author-list">
        """
        
        for author in author_dirs:
            html += f'<div class="author-item"><a href="/works?author={author}">{author}</a></div>\n'
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_works_page(self, author_id):
        """Generate the works listing page for an author"""
        author_path = os.path.join('data', author_id)
        works = []
        
        if os.path.exists(author_path):
            for item in os.listdir(author_path):
                item_path = os.path.join(author_path, item)
                if os.path.isdir(item_path):
                    works.append(item)
        
        works.sort()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Works for {author_id}</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .nav {{ margin: 20px 0; }}
                .nav a {{ display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
                .nav a:hover {{ background: #004080; }}
                .work-list {{ margin-top: 20px; }}
                .work-item {{ padding: 15px; border-bottom: 1px solid #eee; }}
                .work-item:hover {{ background: #f8f8f8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works for Author: {author_id}</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/authors">Back to Authors</a>
                </div>
                
                <div class="work-list">
        """
        
        for work in works:
            html += f'<div class="work-item"><strong>{work}</strong><br/>'
            
            # List the XML files in this work directory
            work_path = os.path.join(author_path, work)
            for item in os.listdir(work_path):
                if item.endswith('.xml') and not item == '__cts__.xml':
                    file_path = os.path.join('data', author_id, work, item)
                    html += f'<a href="/view?path={file_path}">{item}</a><br/>'
            
            html += '</div>\n'
        
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
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>First1K Greek - View XML</title>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
                    .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #333; }}
                    .nav {{ margin: 20px 0; }}
                    .nav a {{ display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                            padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
                    .reader-link {{ display: inline-block; margin-top: 10px; }}
                    pre {{ background: #f8f8f8; padding: 15px; border: 1px solid #ddd; overflow-x: auto; line-height: 1.4; }}
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
                    
                    <a href="/reader?path={file_path}" class="reader-link">Open in Reader Mode</a>
                    
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative information about the file
            parts = file_path.split('/')
            author_id = parts[1] if len(parts) > 1 else ""
            work_id = parts[2] if len(parts) > 2 else ""
            
            # Process the XML content for reader-friendly display
            processed_content = self.process_xml_for_reading(content)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>First1K Greek - Reader Mode</title>
                <meta charset="UTF-8">
                <style>
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

    def get_editors_page(self):
        """Generate the editors listing page"""
        # Get editor data
        editors_data = self.get_editors_data()
        editors_data.sort(key=lambda x: x["name"])
        
        # Build the HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Editors</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }
                .container { max-width: 900px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .nav { margin: 20px 0; }
                .nav a { display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }
                .nav a:hover { background: #004080; }
                .editor-list { margin-top: 20px; }
                .editor-item { padding: 10px; border-bottom: 1px solid #eee; }
                .editor-item:hover { background: #f8f8f8; }
                .editor-count { color: #666; font-size: 0.9em; }
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
                
                <div class="editor-list">
        """
        
        for editor in editors_data:
            name = editor["name"]
            count = editor["count"]
            html += f'<div class="editor-item"><a href="/editor_works?name={quote(name)}">{name}</a> <span class="editor-count">({count} works)</span></div>\n'
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        return add_shutdown_button(html)
    
    def get_editor_works_page(self, editor_name):
        """Generate page showing works by a specific editor"""
        # Find all works by this editor
        works = []
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if f'<editor>{editor_name}</editor>' in content or f'editor>{editor_name}</editor>' in content:
                            works.append({
                                "path": file_path,
                                "file": file
                            })
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
        
        # Sort works by path
        works.sort(key=lambda x: x["path"])
        
        # Build the HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First1K Greek - Works edited by {editor_name}</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .nav {{ margin: 20px 0; }}
                .nav a {{ display: inline-block; margin-right: 15px; background: #0066cc; color: white; 
                        padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
                .nav a:hover {{ background: #004080; }}
                .work-list {{ margin-top: 20px; }}
                .work-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .work-item:hover {{ background: #f8f8f8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Works edited by: {editor_name}</h1>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/editors">Back to Editors</a>
                </div>
                
                <div class="work-list">
        """
        
        for work in works:
            path = work["path"]
            file = work["file"]
            html += f'<div class="work-item"><a href="/view?path={path}">{file}</a></div>\n'
        
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
        
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract editor information
                        editor_matches = re.findall(r'<editor>(.*?)</editor>', content)
                        if not editor_matches:
                            editor_matches = re.findall(r'<editor[^>]*>(.*?)</editor>', content)
                            
                        for editor in editor_matches:
                            editor = editor.strip()
                            if editor:
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
                            if title_matches and len(title_matches[0].strip()) > 0:
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

def add_shutdown_button(html):
    """Add a shutdown button to the HTML pages"""
    shutdown_button = """
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
        <a href="/shutdown" style="display: inline-block; padding: 10px 15px; background-color: #f44336; color: white; text-decoration: none; border-radius: 4px; font-family: Arial, sans-serif; font-size: 14px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            Shutdown Server
        </a>
    </div>
    """
    # Insert before the closing body tag
    if "</body>" in html:
        return html.replace("</body>", f"{shutdown_button}</body>")
    else:
        return html + shutdown_button

def run_server():
    """Run the HTTP server"""
    global server_instance, PORT
    
    # Find an available port
    if is_port_in_use(PORT):
        PORT = find_available_port(PORT)
    
    # Create and start the server
    handler = CustomHTTPRequestHandler
    server_instance = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server running at http://localhost:{PORT}/")
    
    # Open the browser
    webbrowser.open(f"http://localhost:{PORT}/")
    
    try:
        # Run the server until interrupted
        server_instance.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
        server_instance.shutdown()
        print("Server closed")
        server_instance = None

if __name__ == "__main__":
    run_server() 