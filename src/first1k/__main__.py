"""
Main entry point for First1KGreek Browser.

This module serves as the main entry point for the application, handling
command line arguments and initializing the server.

Usage:
    python -m src.first1k [--port PORT] [--debug] [--version]
"""

import logging
import sys
import os
import time
import traceback

from .server import run_server
from .config import PORT, DEBUG, VERSION, VERSION_NAME
from .utils import parse_args

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
    log_file = os.path.join(log_dir, f"first1k-browser-{timestamp}.log")
    
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

def show_version():
    """Display version information and exit."""
    print(f"First1KGreek Browser {VERSION} ({VERSION_NAME})")
    print("A tool for browsing and analyzing ancient Greek texts")
    print("© 2025")
    sys.exit(0)

def main():
    """
    Main entry point for the First1KGreek Browser application.
    
    Parses command line arguments, configures the application,
    and starts the HTTP server.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Show version if requested
    if args.version:
        show_version()
    
    # Configure logging
    logger = configure_logging(args.debug)
    
    # Update global configuration based on arguments
    port = args.port if args.port else PORT
    debug = DEBUG or args.debug
    host = args.host
    open_browser = not args.no_browser
    
    # Log startup information
    logger.info(f"Starting First1KGreek Browser {VERSION} ({VERSION_NAME})")
    logger.info(f"Configuration: port={port}, host={host}, debug={debug}, open_browser={open_browser}")
    
    try:
        # Measure server runtime
        start_time = time.time()
        
        # Run the server
        run_server(
            port=port, 
            debug=debug, 
            host=host, 
            open_browser=open_browser
        )
        
        # Log server runtime on shutdown
        runtime = time.time() - start_time
        logger.info(f"Server ran for {runtime:.1f} seconds")
        
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"Error: Port {port} is already in use.")
            logger.error("Try closing any running instances or use the following command to force close:")
            logger.error(f"lsof -i :{port} | grep Python | awk '{{print $2}}' | xargs kill -9")
        else:
            logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user via keyboard interrupt")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 