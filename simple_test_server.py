#!/usr/bin/env python3
"""
Simple test server to verify basic functionality.
This doesn't rely on the refactored structure.
"""

import http.server
import socketserver
import webbrowser

PORT = 8888
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever() 