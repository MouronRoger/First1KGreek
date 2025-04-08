"""
Main entry point for First1KGreek Browser.

This module serves as the main entry point for the application, handling
command line arguments and initializing the server.

Usage:
    python -m src.first1k [--port PORT] [--debug]
"""

import logging
from .server import run_server
from .config import PORT, DEBUG
from .utils import parse_args

logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the First1KGreek Browser application.
    
    Parses command line arguments, configures the application,
    and starts the HTTP server.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Update global configuration based on arguments
    port = args.port if args.port else PORT
    debug = args.debug
    
    logger.info(f"Starting First1KGreek Browser with port={port}, debug={debug}")
    
    try:
        run_server(port=port, debug=debug)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"Error: Port {port} is already in use.")
            logger.error("Try closing any running instances or use the following command to force close:")
            logger.error(f"lsof -i :{port} | grep Python | awk '{{print $2}}' | xargs kill -9")
        else:
            logger.error(f"Error starting server: {str(e)}")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")

if __name__ == "__main__":
    main() 