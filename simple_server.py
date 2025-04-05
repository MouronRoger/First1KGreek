#!/usr/bin/env python3
"""
Simple HTTP server for testing First1KGreek
"""

import http.server
import socketserver
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
    return parser.parse_args()

# Use the standard SimpleHTTPRequestHandler
Handler = http.server.SimpleHTTPRequestHandler

if __name__ == "__main__":
    args = parse_args()
    PORT = args.port
    
    print(f"Starting simple HTTP server on port {PORT}...")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever() 