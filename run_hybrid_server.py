#!/usr/bin/env python3
"""
Run script for First1KGreek Hybrid Server.

This script starts both the HTTP and FastAPI servers simultaneously during the transition period.
"""

import argparse
import logging
import sys

from src.first1k.config import PORT, HOST, VERSION, VERSION_NAME
from src.first1k.server.hybrid_server import run_hybrid_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("hybrid_server.log")
    ]
)

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run First1KGreek Hybrid Server")
    
    parser.add_argument(
        "--http-host",
        type=str,
        default=HOST,
        help=f"Host for the HTTP server (default: {HOST})"
    )
    
    parser.add_argument(
        "--http-port",
        type=int,
        default=PORT,
        help=f"Port for the HTTP server (default: {PORT})"
    )
    
    parser.add_argument(
        "--fastapi-host",
        type=str,
        default=HOST,
        help=f"Host for the FastAPI server (default: {HOST})"
    )
    
    parser.add_argument(
        "--fastapi-port",
        type=int,
        default=PORT + 1,
        help=f"Port for the FastAPI server (default: {PORT + 1})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for FastAPI"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
    return parser.parse_args()


def main():
    """Run the hybrid server."""
    args = parse_args()
    
    if args.version:
        print(f"First1KGreek Hybrid Server {VERSION} - {VERSION_NAME}")
        return 0
    
    logger.info(f"Starting First1KGreek Hybrid Server {VERSION} - {VERSION_NAME}")
    
    try:
        run_hybrid_server(
            http_host=args.http_host,
            http_port=args.http_port,
            fastapi_host=args.fastapi_host,
            fastapi_port=args.fastapi_port,
            debug=args.debug,
            reload=args.reload
        )
        return 0
    except Exception as e:
        logger.error(f"Error running hybrid server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 