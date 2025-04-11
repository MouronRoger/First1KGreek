"""Hybrid server mode for First1KGreek.

This module provides a hybrid server mode that runs both the HTTP server and FastAPI server
simultaneously during the transition period.
"""

import logging
import multiprocessing
import os
import signal
import subprocess
import sys
import threading
import time
from typing import Optional, Tuple

import uvicorn
from http.server import HTTPServer

from ..config import PORT, HOST, VERSION, VERSION_NAME
from .server import CustomHTTPRequestHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridServer:
    """Class for running both HTTP and FastAPI servers simultaneously.
    
    This class manages the lifecycle of both servers, allowing them to run
    in parallel during the transition period from HTTP to FastAPI.
    
    Attributes:
        http_host: Host for the HTTP server
        http_port: Port for the HTTP server
        fastapi_host: Host for the FastAPI server
        fastapi_port: Port for the FastAPI server
        debug: Whether to enable debug mode
        reload: Whether to enable auto-reload for FastAPI
        http_server: HTTP server instance
        http_process: Process for the HTTP server
        fastapi_process: Process for the FastAPI server
    """
    
    def __init__(
        self,
        http_host: str = HOST,
        http_port: int = PORT,
        fastapi_host: str = HOST,
        fastapi_port: Optional[int] = None,
        debug: bool = False,
        reload: bool = False
    ):
        """Initialize the hybrid server.
        
        Args:
            http_host: Host for the HTTP server
            http_port: Port for the HTTP server
            fastapi_host: Host for the FastAPI server
            fastapi_port: Port for the FastAPI server (defaults to http_port + 1)
            debug: Whether to enable debug mode
            reload: Whether to enable auto-reload for FastAPI
        """
        self.http_host = http_host
        self.http_port = http_port
        self.fastapi_host = fastapi_host
        self.fastapi_port = fastapi_port or (http_port + 1)
        self.debug = debug
        self.reload = reload
        
        self.http_server = None
        self.http_process = None
        self.fastapi_process = None
        
        self._shutdown_event = threading.Event()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
    
    def _start_http_server(self):
        """Start the HTTP server in a separate process."""
        logger.info(f"Starting HTTP server at http://{self.http_host}:{self.http_port}")
        
        try:
            # Create and configure HTTP server
            server_address = (self.http_host, self.http_port)
            self.http_server = HTTPServer(server_address, CustomHTTPRequestHandler)
            
            # Set debug mode if specified
            if hasattr(CustomHTTPRequestHandler, 'DEBUG'):
                CustomHTTPRequestHandler.DEBUG = self.debug
            
            # Start the server
            self.http_server.serve_forever()
        except Exception as e:
            logger.error(f"Error in HTTP server: {e}")
            raise
    
    def _start_fastapi_server(self):
        """Start the FastAPI server using uvicorn."""
        logger.info(f"Starting FastAPI server at http://{self.fastapi_host}:{self.fastapi_port}")
        
        try:
            # Configure log level
            log_level = "debug" if self.debug else "info"
            
            # Start uvicorn
            uvicorn.run(
                "src.first1k.api:app",
                host=self.fastapi_host,
                port=self.fastapi_port,
                reload=self.reload,
                log_level=log_level
            )
        except Exception as e:
            logger.error(f"Error in FastAPI server: {e}")
            raise
    
    def start(self):
        """Start both HTTP and FastAPI servers in separate processes."""
        logger.info(f"Starting First1KGreek Hybrid Server {VERSION} - {VERSION_NAME}")
        logger.info(f"Running in hybrid mode with both HTTP and FastAPI servers")
        
        # Start HTTP server in a separate process
        self.http_process = multiprocessing.Process(
            target=self._start_http_server,
            daemon=True
        )
        self.http_process.start()
        
        # Start FastAPI server in a separate process
        self.fastapi_process = multiprocessing.Process(
            target=self._start_fastapi_server,
            daemon=True
        )
        self.fastapi_process.start()
        
        logger.info(f"HTTP server available at http://{self.http_host}:{self.http_port}")
        logger.info(f"FastAPI server available at http://{self.fastapi_host}:{self.fastapi_port}")
        logger.info(f"API documentation available at http://{self.fastapi_host}:{self.fastapi_port}/docs")
        
        try:
            # Keep the main process running until shutdown is requested
            while not self._shutdown_event.is_set():
                # Check if processes are still alive
                if not self.http_process.is_alive() or not self.fastapi_process.is_alive():
                    logger.error("One of the server processes has died, shutting down...")
                    self.stop()
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            self.stop()
    
    def stop(self):
        """Stop both HTTP and FastAPI servers."""
        logger.info("Stopping servers...")
        self._shutdown_event.set()
        
        # Terminate HTTP server process
        if self.http_process and self.http_process.is_alive():
            logger.info("Stopping HTTP server...")
            self.http_process.terminate()
            self.http_process.join(timeout=5)
            if self.http_process.is_alive():
                logger.warning("HTTP server did not terminate gracefully, killing...")
                self.http_process.kill()
        
        # Terminate FastAPI server process
        if self.fastapi_process and self.fastapi_process.is_alive():
            logger.info("Stopping FastAPI server...")
            self.fastapi_process.terminate()
            self.fastapi_process.join(timeout=5)
            if self.fastapi_process.is_alive():
                logger.warning("FastAPI server did not terminate gracefully, killing...")
                self.fastapi_process.kill()
        
        logger.info("All servers stopped")


def run_hybrid_server(
    http_host: str = HOST,
    http_port: int = PORT,
    fastapi_host: str = HOST,
    fastapi_port: Optional[int] = None,
    debug: bool = False,
    reload: bool = False
):
    """Run the hybrid server with both HTTP and FastAPI.
    
    Args:
        http_host: Host for the HTTP server
        http_port: Port for the HTTP server
        fastapi_host: Host for the FastAPI server
        fastapi_port: Port for the FastAPI server
        debug: Whether to enable debug mode
        reload: Whether to enable auto-reload for FastAPI
    """
    server = HybridServer(
        http_host=http_host,
        http_port=http_port,
        fastapi_host=fastapi_host,
        fastapi_port=fastapi_port,
        debug=debug,
        reload=reload
    )
    
    server.start() 