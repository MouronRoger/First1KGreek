#!/usr/bin/env python3
"""
First1KGreek Browser - Standalone Server Runner

This script provides a simple way to run the First1KGreek Browser application
without having to install the package. It serves as the main entry point
for the application in production.

Usage:
    python run_server.py [--port PORT] [--debug] [--help]
"""

import sys
import os
import argparse
import logging
import traceback
import time

# Add the current directory to the Python path to ensure imports work
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Run First1KGreek Browser Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--port', type=int, default=8000, 
                        help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', 
                        help='Enable debug mode with additional logging')
    parser.add_argument('--version', action='store_true',
                        help='Show version information and exit')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not automatically open a web browser')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host to bind the server to (use 0.0.0.0 to allow external connections)')
    return parser.parse_args()

def show_version():
    """Display version information and exit."""
    try:
        from src.first1k import __version__
        version = __version__
    except ImportError:
        version = "unknown"
    
    print(f"First1KGreek Browser version {version}")
    print("A tool for browsing and analyzing ancient Greek texts")
    print("© 2025")
    sys.exit(0)

def main():
    """
    Main entry point for the application.
    
    Parses command line arguments and starts the server.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Show version information if requested
    if args.version:
        show_version()
    
    # Set debug level based on arguments
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('src.first1k').setLevel(logging.DEBUG)
    
    # Import the server module from src.first1k
    try:
        from src.first1k.server.server import run_server
        logger.info("Starting First1KGreek Browser...")
        
        # Display connection information
        port = args.port
        host = args.host
        open_browser = not args.no_browser
        
        # Log configuration
        logger.info(f"Server configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port} (will try other ports if busy)")
        logger.info(f"  Debug mode: {args.debug}")
        logger.info(f"  Open browser: {open_browser}")
        
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the server
        start_time = time.time()
        run_server(
            port=port, 
            debug=args.debug, 
            host=host, 
            open_browser=open_browser
        )
        
        # Log server runtime on shutdown
        runtime = time.time() - start_time
        logger.info(f"Server ran for {runtime:.1f} seconds")
    
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        logger.error("Ensure the src/first1k package is properly installed")
        logger.error("Try running: PYTHONPATH=. python run_server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt)")
    except SystemExit:
        pass  # Normal exit
    except Exception as e:
        logger.error(f"Error running server: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 