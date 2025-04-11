#!/usr/bin/env python3
"""
Run script for First1KGreek FastAPI server.

This script starts the FastAPI server using Uvicorn.
"""

import argparse
import logging
import sys
import uvicorn

from src.first1k.config import PORT, HOST, VERSION, VERSION_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fastapi_server.log")
    ]
)

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run First1KGreek FastAPI server")
    
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
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
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
    """Run the FastAPI server."""
    args = parse_args()
    
    if args.version:
        print(f"First1KGreek FastAPI Server {VERSION} - {VERSION_NAME}")
        return 0
    
    # Configure log level
    log_level = "debug" if args.debug else "info"
    
    logger.info(f"Starting First1KGreek FastAPI Server {VERSION} - {VERSION_NAME}")
    logger.info(f"Server will be available at http://{args.host}:{args.port}")
    logger.info(f"API documentation will be available at http://{args.host}:{args.port}/docs")
    
    try:
        uvicorn.run(
            "src.first1k.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=log_level
        )
        return 0
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 