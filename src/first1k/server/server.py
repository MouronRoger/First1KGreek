"""Core server functionality for First1KGreek Browser."""

import http.server
import socketserver
import webbrowser
import threading
import time
import shutil
import os
import json
import signal
import sys
import logging
from urllib.parse import urlparse, parse_qs, unquote
from ..config import BACKUP_FILE
from ..utils.network import is_port_in_use, find_available_port
from ..handlers.ui import render_main_page
from ..handlers.browse import render_authors_page, render_editors_page
from ..handlers.search import render_search_page
from ..handlers.import_text import (
    render_import_page,
    render_import_success_page,
    render_import_error_page,
    import_text_from_scaife
)
from ..handlers.view import render_xml_view_page, render_reader_view_page
from ..handlers.works import render_works_page, render_editor_works_page
from ..handlers.api import handle_get_author_works
from ..handlers.preferences import handle_update_work_preference, handle_bulk_update_preferences

# Global reference to the server
server_instance = None
logger = logging.getLogger(__name__)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP server handler for browsing and viewing texts."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the HTTP request handler with request timing."""
        self.request_start_time = None
        super().__init__(*args, **kwargs)
    
    def send_html_response(self, html_content):
        """Helper method to send HTML response with correct headers."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data):
        """Helper method to send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        """Handle GET requests."""
        self.request_start_time = time.time()
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            logger.info(f"GET request: {self.path}")

            if path == '/' or path == '/index.html':
                self.send_html_response(render_main_page())
                
            elif path == '/browse/authors':
                self.send_html_response(render_authors_page())
                
            elif path == '/browse/editors':
                self.send_html_response(render_editors_page())
                
            elif path == '/search':
                search_term = query_params.get('q', [''])[0]
                self.send_html_response(render_search_page(search_term))
                
            elif path == '/import':
                self.send_html_response(render_import_page())
                
            elif path == '/works':
                author_id = query_params.get('author', [''])[0]
                if not author_id:
                    self.send_error(400, "Missing author parameter")
                    return
                self.send_html_response(render_works_page(author_id))
                
            elif path == '/editor_works':
                editor_name = query_params.get('name', [''])[0]
                if not editor_name:
                    self.send_error(400, "Missing editor name parameter")
                    return
                self.send_html_response(render_editor_works_page(editor_name))
                
            elif path == '/view':
                file_path = query_params.get('path', [''])[0]
                if not file_path:
                    self.send_error(400, "Missing path parameter")
                    return
                self.send_html_response(render_xml_view_page(unquote(file_path)))
                
            elif path == '/reader':
                file_path = query_params.get('path', [''])[0]
                if not file_path:
                    self.send_error(400, "Missing path parameter")
                    return
                self.send_html_response(render_reader_view_page(unquote(file_path)))
                
            elif path == '/get_author_works':
                status_code, content_type, response_data = handle_get_author_works(query_params)
                self.send_response(status_code)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
                
            elif path == '/shutdown':
                self.send_html_response("<h1>Server shutting down...</h1>")
                threading.Thread(target=self.delayed_shutdown).start()
                
            else:
                try:
                    super().do_GET()
                except Exception as e:
                    self.send_error(404, f"File not found: {self.path}")
                    logger.error(f"Error serving {self.path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
        finally:
            if self.request_start_time:
                request_time = time.time() - self.request_start_time
                logger.debug(f"Request processed in {request_time:.4f} seconds")

    def do_POST(self):
        """Handle POST requests."""
        self.request_start_time = time.time()
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            logger.info(f"POST request: {self.path}")
            
            if path == '/import_text':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = parse_qs(post_data)
                
                try:
                    if params.get('import_type', [''])[0] == 'single':
                        scaife_url = params.get('scaife_url', [''])[0]
                        author_name = params.get('author_name', [''])[0]
                        work_title = params.get('work_title', [''])[0]
                        
                        if not scaife_url:
                            raise ValueError("Missing Scaife URL")
                            
                        result = import_text_from_scaife(scaife_url, author_name, work_title)
                        self.send_html_response(render_import_success_page(result))
                        
                    else:  # batch import
                        scaife_urls = params.get('scaife_urls', [''])[0].split('\n')
                        default_author = params.get('default_author_name', [''])[0]
                        
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
                
            elif path == '/update_work_preference':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                status_code, content_type, response_data = handle_update_work_preference(query_params, post_data)
                self.send_response(status_code)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
                
            elif path == '/update_preferences':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                status_code, content_type, response_data = handle_bulk_update_preferences(query_params, post_data)
                self.send_response(status_code)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
                
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
        finally:
            if self.request_start_time:
                request_time = time.time() - self.request_start_time
                logger.debug(f"Request processed in {request_time:.4f} seconds")

    def delayed_shutdown(self):
        """Delay the shutdown to allow the response to be sent."""
        time.sleep(1)
        global server_instance
        if server_instance:
            logger.info("Server stopping...")
            # Force the socket to close with a timeout
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
            logger.info("Server closed successfully")

def handle_shutdown(sig, frame):
    """
    Handle external shutdown signals.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {sig}, initiating shutdown...")
    if server_instance:
        try:
            server_instance.shutdown()
            logger.info("Server has been shut down via signal handler")
            # Force exit after a short delay
            threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGKILL)).start()
        except Exception as e:
            logger.error(f"Error during signal-triggered shutdown: {str(e)}")
            # Force exit even if shutdown failed
            threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGKILL)).start()

def run_server(port=None, debug=False, host='localhost', open_browser=True):
    """
    Run the HTTP server.
    
    Args:
        port (int, optional): Port to run the server on. If None or already in use,
                             an available port will be found. Defaults to None.
        debug (bool, optional): Whether to run in debug mode. Defaults to False.
        host (str, optional): Host to bind the server to. Use '0.0.0.0' to allow
                             external connections. Defaults to 'localhost'.
        open_browser (bool, optional): Whether to automatically open a web browser.
                                      Defaults to True.
    """
    global server_instance
    
    # Use the provided port or find an available one
    if port is None:
        port = 8000  # Default port
    
    # Create a backup of the file if it doesn't exist already
    if not os.path.exists(BACKUP_FILE):
        shutil.copy('browse_texts.py', BACKUP_FILE)
    
    # Print version info when starting
    logger.info("Starting First1KGreek Browser - Fixed Version 1.2.0")
    logger.info("With dark theme and improved editor detection")
    
    if debug:
        logger.info("Running in debug mode")
    
    # Find an available port
    if is_port_in_use(port):
        port = find_available_port(port)
    
    # Create and start the server
    handler = CustomHTTPRequestHandler
    # Enable socket reuse to avoid "address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        server_instance = socketserver.TCPServer((host, port), handler)
        
        # Log server URL based on host binding
        if host == '0.0.0.0' or host == '':
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            logger.info(f"Server running at:")
            logger.info(f"  http://localhost:{port}/ (local access)")
            logger.info(f"  http://{ip}:{port}/ (network access)")
        else:
            logger.info(f"Server running at http://{host}:{port}/")
        
        # Register signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Open the browser if requested
        if open_browser:
            webbrowser.open(f"http://localhost:{port}/")
        
        # Run the server until interrupted
        server_instance.serve_forever()
    
    except OSError as e:
        logger.error(f"Error starting server: {str(e)}")
        if host != 'localhost' and host != '127.0.0.1':
            logger.error("If binding to a network interface, you may need root privileges.")
            logger.error("Try using --host=localhost for local-only access.")
        raise
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user via keyboard interrupt")
        if server_instance:
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
        logger.info("Server closed")
    
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        if server_instance:
            server_instance.socket.close()
            server_instance.server_close()
            server_instance.shutdown()
            server_instance = None
        raise 