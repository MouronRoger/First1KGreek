"""
Network utility functions for the First1KGreek Browser.

This module provides functions for checking port availability and finding open ports.
"""

import socket
import logging

logger = logging.getLogger(__name__)


def is_port_in_use(port):
    """
    Check if a port is in use.
    
    Args:
        port (int): The port number to check
        
    Returns:
        bool: True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port)) == 0
        logger.debug(f"Port {port} is {'in use' if result else 'available'}")
        return result


def find_available_port(start_port=8000, max_attempts=10):
    """
    Find an available port starting from start_port.
    
    Args:
        start_port (int, optional): The port to start checking from. Defaults to 8000.
        max_attempts (int, optional): Maximum number of ports to check. Defaults to 10.
        
    Returns:
        int: An available port, or start_port if none found
    """
    logger.debug(f"Searching for available port starting from {start_port}")
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            logger.debug(f"Found available port: {port}")
            return port
    logger.warning(f"No available ports found in range {start_port}-{start_port+max_attempts-1}")
    return start_port 