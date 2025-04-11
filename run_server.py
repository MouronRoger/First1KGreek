#!/usr/bin/env python3
"""
Main run script for First1KGreek.

This script has been updated to use FastAPI as the primary server,
while maintaining backward compatibility with the original HTTP server.
"""

import argparse
import logging
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from src.first1k.config import PORT, HOST, VERSION, VERSION_NAME
from src.first1k.utils.network import is_port_in_use, find_available_port

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run First1KGreek Browser")
    
    parser.add_argument(
        "--host",
        type=str,
        default=HOST,
        help=f"Host to bind the server to (default: {HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help=f"Port to bind the server to (default: {PORT})"
    )
    
    parser.add_argument(
        "--mode",
        choices=["fastapi", "http", "hybrid"],
        default="fastapi",
        help="Server mode to run (default: fastapi)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for FastAPI (only in fastapi or hybrid mode)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
    return parser.parse_args()


def run_fastapi_server(host, port, debug, reload, no_browser):
    """Run the FastAPI server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to enable debug mode
        reload: Whether to enable auto-reload
        no_browser: Whether to open browser automatically
    """
    import uvicorn
    
    # Configure log level
    log_level = "debug" if debug else "info"
    
    logger.info(f"Starting First1KGreek FastAPI Server {VERSION} - {VERSION_NAME}")
    logger.info(f"Server will be available at http://{host}:{port}")
    logger.info(f"API documentation will be available at http://{host}:{port}/docs")
    
    # Open browser if requested
    if not no_browser:
        url = f"http://{host}:{port}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    # Start the FastAPI server
    try:
        uvicorn.run(
            "src.first1k.api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except Exception as e:
        logger.error(f"Error running FastAPI server: {e}")
        raise


def run_http_server(host, port, debug, no_browser):
    """Run the traditional HTTP server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to enable debug mode
        no_browser: Whether to open browser automatically
    """
    from http.server import HTTPServer
    from src.first1k.server.server import CustomHTTPRequestHandler
    
    logger.info(f"Starting First1KGreek HTTP Server {VERSION} - {VERSION_NAME}")
    logger.info(f"Server will be available at http://{host}:{port}")
    
    # Set debug mode if specified
    if debug:
        CustomHTTPRequestHandler.DEBUG = True
    
    # Create and configure HTTP server
    try:
        server = HTTPServer((host, port), CustomHTTPRequestHandler)
        
        # Open browser if requested
        if not no_browser:
            url = f"http://{host}:{port}"
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        
        # Start the server
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")
        raise


def run_hybrid_server(host, port, debug, reload, no_browser):
    """Run the hybrid server with both HTTP and FastAPI.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to enable debug mode
        reload: Whether to enable auto-reload
        no_browser: Whether to open browser automatically
    """
    from src.first1k.server.hybrid_server import run_hybrid_server
    
    # Use port+1 for FastAPI server in hybrid mode
    fastapi_port = port + 1
    
    logger.info(f"Starting First1KGreek Hybrid Server {VERSION} - {VERSION_NAME}")
    logger.info(f"HTTP server will be available at http://{host}:{port}")
    logger.info(f"FastAPI server will be available at http://{host}:{fastapi_port}")
    logger.info(f"API documentation will be available at http://{host}:{fastapi_port}/docs")
    
    # Open browser to HTTP server if requested
    if not no_browser:
        url = f"http://{host}:{port}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    # Start the hybrid server
    try:
        run_hybrid_server(
            http_host=host,
            http_port=port,
            fastapi_host=host,
            fastapi_port=fastapi_port,
            debug=debug,
            reload=reload
        )
    except Exception as e:
        logger.error(f"Error running hybrid server: {e}")
        raise


def main():
    """Run the server based on specified mode."""
    import threading
    
    args = parse_args()
    
    if args.version:
        print(f"First1KGreek Browser {VERSION} - {VERSION_NAME}")
        return 0
    
    # Check if port is available
    if is_port_in_use(args.port):
        if args.mode == "hybrid":
            logger.warning(f"Port {args.port} is already in use!")
            alt_port = find_available_port(args.port + 2)
            logger.info(f"Using alternative port {alt_port}")
            args.port = alt_port
        else:
            logger.warning(f"Port {args.port} is already in use!")
            alt_port = find_available_port(args.port + 1)
            logger.info(f"Using alternative port {alt_port}")
            args.port = alt_port
    
    # Check if hybrid mode requires additional port
    if args.mode == "hybrid" and is_port_in_use(args.port + 1):
        logger.warning(f"Port {args.port + 1} (for FastAPI in hybrid mode) is already in use!")
        alt_port = find_available_port(args.port + 2)
        logger.info(f"Using alternative port {alt_port}")
        args.port = alt_port
    
    try:
        if args.mode == "fastapi":
            run_fastapi_server(args.host, args.port, args.debug, args.reload, args.no_browser)
        elif args.mode == "http":
            run_http_server(args.host, args.port, args.debug, args.no_browser)
        elif args.mode == "hybrid":
            run_hybrid_server(args.host, args.port, args.debug, args.reload, args.no_browser)
        return 0
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 