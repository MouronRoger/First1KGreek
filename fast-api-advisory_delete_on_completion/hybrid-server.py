#!/usr/bin/env python3
"""
First1KGreek Hybrid Server

This script starts both the original HTTP server and the new FastAPI server,
allowing for a gradual migration from one to the other.
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from src.first1k import config
from src.first1k.utils.network import find_available_port

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='First1KGreek Hybrid Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--http-port', 
        type=int, 
        default=config.PORT, 
        help='Port to run the HTTP server on'
    )
    
    parser.add_argument(
        '--api-port', 
        type=int, 
        default=config.PORT + 1, 
        help='Port to run the FastAPI server on'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=config.HOST,
        help='Host to bind the servers to'
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
    
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Run only the FastAPI server'
    )
    
    parser.add_argument(
        '--http-only',
        action='store_true',
        help='Run only the HTTP server'
    )
    
    return parser.parse_args()

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
    log_file = os.path.join(log_dir, f"hybrid-server-{timestamp}.log")
    
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

def run_http_server(host, port, debug):
    """
    Run the original HTTP server in a subprocess.
    
    Args:
        host (str): Host to bind to
        port (int): Port to run on
        debug (bool): Whether to enable debug mode
    
    Returns:
        subprocess.Popen: The subprocess running the server
    """
    cmd = [
        sys.executable,
        "browse_texts_fixed.py",
        "--port", str(port),
        "--host", host
    ]
    
    if debug:
        cmd.append("--debug")
    
    logger.info(f"Starting HTTP server with command: {' '.join(cmd)}")
    
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

def run_api_server(host, port, debug):
    """
    Run the FastAPI server in a subprocess.
    
    Args:
        host (str): Host to bind to
        port (int): Port to run on
        debug (bool): Whether to enable debug mode
    
    Returns:
        subprocess.Popen: The subprocess running the server
    """
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "src.first1k.api:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if debug:
        cmd.append("--reload")
        cmd.append("--log-level=debug")
    else:
        cmd.append("--log-level=info")
    
    logger.info(f"Starting FastAPI server with command: {' '.join(cmd)}")
    
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

def log_subprocess_output(process, name):
    """
    Log output from a subprocess to the main logger.
    
    Args:
        process (subprocess.Popen): The subprocess
        name (str): Name to use in log messages
    """
    while True:
        # Read stdout
        stdout_line = process.stdout.readline()
        if stdout_line:
            logger.info(f"{name}: {stdout_line.strip()}")
        
        # Read stderr
        stderr_line = process.stderr.readline()
        if stderr_line:
            logger.error(f"{name}: {stderr_line.strip()}")
        
        # Check if process is still running
        if process.poll() is not None:
            # Process has terminated
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                logger.info(f"{name} (final output): {remaining_stdout.strip()}")
            if remaining_stderr:
                logger.error(f"{name} (final output): {remaining_stderr.strip()}")
            break

def show_version():
    """Display version information and exit."""
    print(f"First1KGreek Browser {config.VERSION} ({config.VERSION_NAME})")
    print("A tool for browsing and analyzing ancient Greek texts")
    print(f"Last Updated: {config.LAST_UPDATED}")
    print(f"Features: {config.FEATURES}")
    sys.exit(0)

def main():
    """Run both servers and manage their lifecycle."""
    # Parse command line arguments
    args = parse_args()
    
    # Show version if requested
    if args.version:
        show_version()
    
    # Configure logging
    logger = configure_logging(args.debug)
    
    # Find available ports
    http_port = args.http_port
    api_port = args.api_port
    
    # Ensure we don't try to use the same port for both servers
    if http_port == api_port and not (args.api_only or args.http_only):
        logger.warning(f"HTTP and API ports cannot be the same. Using {http_port} for HTTP and {http_port + 1} for API.")
        api_port = http_port + 1
    
    # Log startup information
    logger.info(f"Starting First1KGreek Hybrid Server {config.VERSION} ({config.VERSION_NAME})")
    logger.info(f"HTTP Server: port={http_port}, API Server: port={api_port}, host={args.host}, debug={args.debug}")
    
    # Start servers
    http_process = None
    api_process = None
    
    try:
        # Measure server runtime
        start_time = time.time()
        
        # Start HTTP server if requested
        if not args.api_only:
            http_process = run_http_server(args.host, http_port, args.debug)
            threading.Thread(target=log_subprocess_output, args=(http_process, "HTTP Server"), daemon=True).start()
        
        # Start API server if requested
        if not args.http_only:
            api_process = run_api_server(args.host, api_port, args.debug)
            threading.Thread(target=log_subprocess_output, args=(api_process, "API Server"), daemon=True).start()
        
        # Open browser if requested
        if not args.no_browser:
            if args.api_only:
                # If API only, open the API docs
                url = f"http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{api_port}/docs"
            else:
                # Otherwise, open the HTTP server
                url = f"http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{http_port}"
            
            logger.info(f"Opening browser at {url}")
            webbrowser.open(url)
        
        # Wait for KeyboardInterrupt
        try:
            while True:
                # Check if processes are still running
                if http_process and http_process.poll() is not None:
                    logger.error(f"HTTP server exited with code {http_process.returncode}")
                    break
                
                if api_process and api_process.poll() is not None:
                    logger.error(f"API server exited with code {api_process.returncode}")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt, shutting down servers...")
        
        # Gracefully terminate processes
        if http_process:
            logger.info("Terminating HTTP server...")
            http_process.terminate()
            http_process.wait(timeout=5)
        
        if api_process:
            logger.info("Terminating API server...")
            api_process.terminate()
            api_process.wait(timeout=5)
        
        # Log server runtime
        runtime = time.time() - start_time
        logger.info(f"Servers ran for {runtime:.1f} seconds")
        
    except Exception as e:
        logger.error(f"Error running servers: {str(e)}")
        
        # Ensure processes are terminated
        if http_process:
            http_process.terminate()
        
        if api_process:
            api_process.terminate()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
