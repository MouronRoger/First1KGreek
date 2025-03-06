#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver
import json
from html import escape
import webbrowser
from urllib.parse import parse_qs, urlparse

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
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
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1, h2, h3 { color: #333; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .text-display { border: 1px solid #ddd; padding: 20px; margin-top: 20px; }
                    .navigation { margin-bottom: 20px; }
                    .author-list { display: flex; flex-wrap: wrap; }
                    .author-item { margin: 10px; padding: 10px; border: 1px solid #eee; }
                    .xml-content { white-space: pre-wrap; font-family: monospace; }
                    .greek { font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', sans-serif; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>Welcome to the First 1K Greek Texts Browser</h2>
                        <p>This is a simple browser for the First 1K Greek Project texts. The project aims to provide digital versions of Greek texts from the first thousand years of Greek literature.</p>
                        <p>Use the navigation links above to explore the texts by author or browse the raw files.</p>
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
            authors = []
            if os.path.exists("data"):
                authors = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
                authors.sort()
            
            # Create HTML for author listing
            author_html = ""
            for author in authors:
                author_name = "Unknown"
                author_cts = os.path.join("data", author, "__cts__.xml")
                if os.path.exists(author_cts):
                    # Very simple XML parsing to get author name
                    with open(author_cts, 'r', encoding='utf-8') as f:
                        content = f.read()
                        name_start = content.find("<ti:groupname")
                        if name_start > 0:
                            name_end = content.find("</ti:groupname>", name_start)
                            if name_end > 0:
                                tag_end = content.find(">", name_start)
                                author_name = content[tag_end+1:name_end].strip()
                
                author_html += f'<div class="author-item"><h3><a href="/works?author={author}">{author_name} ({author})</a></h3></div>'
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Authors - First 1K Greek Texts</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ border: 1px solid #ddd; padding: 20px; margin-top: 20px; }}
                    .navigation {{ margin-bottom: 20px; }}
                    .author-list {{ display: flex; flex-wrap: wrap; }}
                    .author-item {{ margin: 10px; padding: 10px; border: 1px solid #eee; width: 250px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a>
                    </div>
                    
                    <div class="text-display">
                        <h2>Authors</h2>
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
                works = []
                author_dir = os.path.join("data", author)
                if os.path.exists(author_dir):
                    works = [d for d in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, d)) and d != "__cts__"]
                    works.sort()
                
                # Create HTML for works listing
                works_html = ""
                for work in works:
                    work_title = work
                    work_cts = os.path.join("data", author, work, "__cts__.xml")
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
                    work_dir = os.path.join("data", author, work)
                    if os.path.exists(work_dir):
                        editions = [f for f in os.listdir(work_dir) if f.endswith(".xml") and f != "__cts__.xml"]
                    
                    editions_html = ""
                    for edition in editions:
                        editions_html += f'<li><a href="/view?path=data/{author}/{work}/{edition}">{edition}</a></li>'
                    
                    works_html += f"""
                    <div class="work-item">
                        <h3>{work_title} ({work})</h3>
                        <p>Available editions:</p>
                        <ul>
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
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                        h1, h2, h3 {{ color: #333; }}
                        .container {{ max-width: 1200px; margin: 0 auto; }}
                        .text-display {{ border: 1px solid #ddd; padding: 20px; margin-top: 20px; }}
                        .navigation {{ margin-bottom: 20px; }}
                        .work-item {{ margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>First 1K Greek Texts Browser</h1>
                        
                        <div class="navigation">
                            <a href="/">Home</a> | 
                            <a href="/authors">Browse Authors</a> | 
                            <a href="/raw">Browse Raw Files</a> | 
                            <a href="/about">About</a>
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
                            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                            h1, h2, h3 {{ color: #333; }}
                            .container {{ max-width: 1200px; margin: 0 auto; }}
                            .text-display {{ border: 1px solid #ddd; padding: 20px; margin-top: 20px; overflow: auto; }}
                            .navigation {{ margin-bottom: 20px; }}
                            .xml-content {{ white-space: pre-wrap; font-family: monospace; }}
                            .greek {{ font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', sans-serif; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>First 1K Greek Texts Browser</h1>
                            
                            <div class="navigation">
                                <a href="/">Home</a> | 
                                <a href="/authors">Browse Authors</a> | 
                                <a href="/raw">Browse Raw Files</a> | 
                                <a href="/about">About</a>
                            </div>
                            
                            <div class="text-display">
                                <h2>{os.path.basename(file_path)}</h2>
                                <p>Path: {file_path}</p>
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
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1, h2, h3 { color: #333; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .text-display { border: 1px solid #ddd; padding: 20px; margin-top: 20px; }
                    .navigation { margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a>
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
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .text-display {{ border: 1px solid #ddd; padding: 20px; margin-top: 20px; }}
                    .navigation {{ margin-bottom: 20px; }}
                    .raw-list {{ display: flex; flex-wrap: wrap; }}
                    .raw-item {{ margin: 10px; padding: 10px; border: 1px solid #eee; width: 250px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>First 1K Greek Texts Browser</h1>
                    
                    <div class="navigation">
                        <a href="/">Home</a> | 
                        <a href="/authors">Browse Authors</a> | 
                        <a href="/raw">Browse Raw Files</a> | 
                        <a href="/about">About</a>
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
                    
                    items_html = "<ul>"
                    for item in items:
                        item_path = os.path.join(dir_path, item)
                        if os.path.isdir(item_path):
                            items_html += f'<li><a href="/raw_browse?dir={item_path}">{item}/</a></li>'
                        elif item.endswith(".xml"):
                            items_html += f'<li><a href="/view?path={item_path}">{item}</a></li>'
                        else:
                            items_html += f'<li>{item}</li>'
                    items_html += "</ul>"
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Raw Browse - {dir_path} - First 1K Greek Texts</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                            h1, h2, h3 {{ color: #333; }}
                            .container {{ max-width: 1200px; margin: 0 auto; }}
                            .text-display {{ border: 1px solid #ddd; padding: 20px; margin-top: 20px; }}
                            .navigation {{ margin-bottom: 20px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>First 1K Greek Texts Browser</h1>
                            
                            <div class="navigation">
                                <a href="/">Home</a> | 
                                <a href="/authors">Browse Authors</a> | 
                                <a href="/raw">Browse Raw Files</a> | 
                                <a href="/about">About</a>
                            </div>
                            
                            <div class="text-display">
                                <h2>Directory: {dir_path}</h2>
                                {items_html}
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    self.wfile.write(html.encode())
                    return
        
        # Default: let the SimpleHTTPRequestHandler handle it
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_server():
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        webbrowser.open(f"http://localhost:{PORT}/")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server() 