"""Core server functionality for First1KGreek Browser."""

import http.server
import json
import os
import shutil
import socketserver
import threading
import time
import webbrowser
from urllib.parse import parse_qs, unquote, urlparse

from ..config import BACKUP_FILE
from ..handlers.browse import render_authors_page, render_editors_page
from ..handlers.import_text import (
    import_text_from_scaife,
    render_import_error_page,
    render_import_page,
    render_import_success_page,
)
from ..handlers.search import render_search_page
from ..handlers.ui import render_main_page
from ..handlers.view import render_reader_view_page, render_xml_view_page
from ..handlers.works import render_editor_works_page, render_works_page
from ..utils.network import find_available_port, is_port_in_use

# Global reference to the server
server_instance = None


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP server handler for browsing and viewing texts."""

    def send_html_response(self, html_content):
        """Helper method to send HTML response with correct headers."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def send_json_response(self, data):
        """Helper method to send JSON response."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == "/" or path == "/index.html":
            self.send_html_response(render_main_page())

        elif path == "/browse/authors":
            self.send_html_response(render_authors_page())

        elif path == "/browse/editors":
            self.send_html_response(render_editors_page())

        elif path == "/search":
            search_term = query_params.get("q", [""])[0]
            self.send_html_response(render_search_page(search_term))

        elif path == "/import":
            self.send_html_response(render_import_page())

        elif path == "/works":
            author_id = query_params.get("author", [""])[0]
            if not author_id:
                self.send_error(400, "Missing author parameter")
                return
            self.send_html_response(render_works_page(author_id))

        elif path == "/editor_works":
            editor_name = query_params.get("name", [""])[0]
            if not editor_name:
                self.send_error(400, "Missing editor name parameter")
                return
            self.send_html_response(render_editor_works_page(editor_name))

        elif path == "/view":
            file_path = query_params.get("path", [""])[0]
            if not file_path:
                self.send_error(400, "Missing path parameter")
                return
            self.send_html_response(render_xml_view_page(unquote(file_path)))

        elif path == "/reader":
            file_path = query_params.get("path", [""])[0]
            if not file_path:
                self.send_error(400, "Missing path parameter")
                return
            self.send_html_response(render_reader_view_page(unquote(file_path)))

        elif path == "/shutdown":
            self.send_html_response("<h1>Server shutting down...</h1>")
            threading.Thread(target=self.delayed_shutdown).start()

        else:
            try:
                super().do_GET()
            except Exception as e:
                self.send_error(404, f"File not found: {self.path}")
                print(f"Error serving {self.path}: {str(e)}")

    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/import_text":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(post_data)

            try:
                if params.get("import_type", [""])[0] == "single":
                    scaife_url = params.get("scaife_url", [""])[0]
                    author_name = params.get("author_name", [""])[0]
                    work_title = params.get("work_title", [""])[0]

                    if not scaife_url:
                        raise ValueError("Missing Scaife URL")

                    result = import_text_from_scaife(
                        scaife_url, author_name, work_title
                    )
                    self.send_html_response(render_import_success_page(result))

                else:  # batch import
                    scaife_urls = params.get("scaife_urls", [""])[0].split("\n")
                    default_author = params.get("default_author_name", [""])[0]

                    results = []
                    for url in scaife_urls:
                        url = url.strip()
                        if url:
                            try:
                                result = import_text_from_scaife(url, default_author)
                                results.append(f"✓ {result}")
                            except Exception as e:
                                results.append(f"✗ Error importing {url}: {str(e)}")

                    message = "<br>".join(results)
                    self.send_html_response(render_import_success_page(message))

            except Exception as e:
                self.send_html_response(render_import_error_page(str(e)))

        else:
            self.send_error(404, "Not Found")

    def delayed_shutdown(self):
        """Delay the shutdown to allow the response to be sent."""
        time.sleep(1)
        global server_instance
        if server_instance:
            print("Server stopping...")
            # Force the socket to close with a timeout
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
            print("Server closed successfully")


def run_server():
    """Run the HTTP server."""
    global server_instance, PORT

    # Create a backup of the file if it doesn't exist already
    if not os.path.exists(BACKUP_FILE):
        shutil.copy("browse_texts.py", BACKUP_FILE)

    # Print version info when starting
    print("Starting First1KGreek Browser - Fixed Version 1.2.0")
    print("With dark theme and improved editor detection")

    # Find an available port
    if is_port_in_use(PORT):
        PORT = find_available_port(PORT)

    # Create and start the server
    handler = CustomHTTPRequestHandler
    # Enable socket reuse to avoid "address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    server_instance = socketserver.TCPServer(("", PORT), handler)

    print(f"Server running at http://localhost:{PORT}/")

    # Open the browser
    webbrowser.open(f"http://localhost:{PORT}/")

    try:
        # Run the server until interrupted
        server_instance.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user via keyboard interrupt")
        if server_instance:
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
        print("Server closed")
    except Exception as e:
        print(f"Server error: {str(e)}")
        if server_instance:
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
