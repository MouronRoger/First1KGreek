#!/usr/bin/env python3
"""
First1KGreek Browser FastAPI Server

This script starts the FastAPI server for the First1KGreek Browser application.
It replaces the original HTTP server with a modern, high-performance API server.
"""

import argparse
import logging
import os
import sys
import time
import webbrowser
import uvicorn
from src.first1k import config
from src.first1k.utils.network import find_available_port

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='First1KGreek Browser API Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=config.PORT, 
        help='Port to run the server on'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with verbose logging and auto-reload'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=config.HOST,
        help='Host to bind the server to (use 0.0.0.0 to allow external connections)'
    )
    
    parser.add_argument(
        '--no-browser', 
        action='store_true',
        help='Do not automatically open a web browser'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information and exit'
    )
    
    return parser.parse_args()

def show_version():
    """Display version information and exit."""
    print(f"First1KGreek Browser API {config.VERSION} ({config.VERSION_NAME})")
    print("A tool for browsing and analyzing ancient Greek texts")
    print(f"Last Updated: {config.LAST_UPDATED}")
    print(f"Features: {config.FEATURES}")
    sys.exit(0)

def configure_logging(debug=False):
    """
    Configure logging with appropriate level and handlers.
    
    Args:
        debug (bool): Whether to enable debug-level logging
    """
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create log directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create timestamp for log file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"first1k-api-{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    
    # Get main logger
    logger = logging.getLogger(__name__)
    
    if debug:
        logger.debug("Debug logging enabled")
    
    return logger

def main():
    """Run the FastAPI server."""
    # Parse command line arguments
    args = parse_args()
    
    # Show version if requested
    if args.version:
        show_version()
    
    # Configure logging
    logger = configure_logging(args.debug)
    
    # Find available port if specified port is in use
    host = args.host
    port = args.port
    debug = args.debug
    open_browser = not args.no_browser
    
    logger.info(f"Starting First1KGreek API Server v{config.VERSION}")
    logger.info(f"Configuration: port={port}, host={host}, debug={debug}, open_browser={open_browser}")
    
    # Measure server runtime
    start_time = time.time()
    
    try:
        # Open browser if requested
        if open_browser:
            webbrowser.open(f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
        
        uvicorn.run(
            "src.first1k.api:app",
            host=host,
            port=port,
            reload=debug,
            log_level="debug" if debug else "info"
        )
    except OSError as e:
        if e.errno == 48:  # Address already in use
            new_port = find_available_port(start_port=port + 1)
            logger.warning(f"Port {port} is in use. Trying port {new_port} instead.")
            
            if open_browser:
                webbrowser.open(f"http://{host if host != '0.0.0.0' else 'localhost'}:{new_port}/docs")
                
            uvicorn.run(
                "src.first1k.api:app", 
                host=host, 
                port=new_port,
                reload=debug,
                log_level="debug" if debug else "info"
            )
        else:
            logger.error(f"Error starting server: {str(e)}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user via keyboard interrupt")
        
        # Log server runtime on shutdown
        runtime = time.time() - start_time
        logger.info(f"Server ran for {runtime:.1f} seconds")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
