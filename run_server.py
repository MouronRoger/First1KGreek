#!/usr/bin/env python3
"""
Run script for First1KGreek browser.

This script provides a unified entry point for running the First1KGreek browser
in different server modes (HTTP, FastAPI, or hybrid).
"""

import argparse
import logging
import os
import sys
import threading
import webbrowser
from http.server import HTTPServer

from src.first1k.config import PORT, HOST, VERSION, VERSION_NAME
from src.first1k.utils.network import is_port_in_use, find_available_port
from src.first1k.server.server import CustomHTTPRequestHandler

# Configure logging at module level
logging.basicConfig(level=logging.INFO)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run First1KGreek browser server")
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=PORT,
        help=f"Port to bind the server to (default: {PORT})"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=HOST,
        help=f"Host to bind the server to (default: {HOST})"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--no-browser", "-n",
        action="store_true",
        help="Do not automatically open a browser window"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information and exit"
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["http", "fastapi", "hybrid"],
        default="http",
        help="Server mode: http, fastapi, or hybrid (default: http)"
    )
    
    return parser.parse_args()


def main():
    """Run the server as a standalone application."""
    args = parse_args()
    
    if args.version:
        print(f"First1KGreek Browser {VERSION} - {VERSION_NAME}")
        return 0
    
    # Set up environment for logging config
    if args.debug:
        os.environ["DEBUG"] = "true"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    port = args.port
    
    # Check if port is already in use
    if is_port_in_use(port):
        alt_port = find_available_port(start_port=port + 1)
        logger.warning(f"Port {port} is already in use!")
        logger.info(f"Using alternative port {alt_port}")
        port = alt_port
    
    try:
        if args.mode == "fastapi":
            logger.info(f"Starting First1KGreek FastAPI Server {VERSION} - {VERSION_NAME}")
            logger.info(f"Server will be available at http://{args.host}:{port}")
            logger.info(f"API documentation will be available at http://{args.host}:{port}/docs")
            
            # Start FastAPI server
            import uvicorn
            uvicorn.run(
                "src.first1k.api:app",
                host=args.host,
                port=port,
                reload=False,
                log_level="debug" if args.debug else "info"
            )
        elif args.mode == "hybrid":
            logger.info(f"Starting First1KGreek Hybrid Server {VERSION} - {VERSION_NAME}")
            
            # Import hybrid server module
            from src.first1k.server.hybrid_server import run_hybrid_server
            
            # Start hybrid server
            run_hybrid_server(
                http_host=args.host,
                http_port=port,
                fastapi_host=args.host,
                fastapi_port=port + 1,
                debug=args.debug,
                reload=False
            )
        else:
            # Default to HTTP server
            logger.info(f"Starting First1KGreek HTTP Server {VERSION} - {VERSION_NAME}")
            logger.info(f"Server will be available at http://{args.host}:{port}")
            
            # Create and configure HTTP server
            server_address = (args.host, port)
            httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
            CustomHTTPRequestHandler.DEBUG = args.debug
            
            # Open browser after a short delay
            if not args.no_browser:
                threading.Timer(1.0, lambda: webbrowser.open(f"http://{args.host}:{port}")).start()
            
            # Start the server
            try:
                logger.info(f"Server started at http://{args.host}:{port}")
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("Server stopped by keyboard interrupt")
                httpd.server_close()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 