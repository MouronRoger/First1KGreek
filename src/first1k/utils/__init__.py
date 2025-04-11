"""
Utility functions for the First1KGreek Browser.

This package contains utility functions used throughout the application:
- Network utilities for handling ports and connections
- Command-line interface utilities
"""

# Network utilities
from .network import is_port_in_use, find_available_port

# CLI utilities
from .cli import parse_args

# Import api_handler for compatibility with routers
from ..handlers import api as api_handler

__all__ = [
    # Network utilities
    'is_port_in_use',
    'find_available_port',
    
    # CLI utilities
    'parse_args',
    
    # API handlers
    'api_handler',
]
