"""First1KGreek Browser server module.

This module contains the HTTP server implementation for the First1KGreek Browser.
"""

from .server import run_server, CustomHTTPRequestHandler

__all__ = ['run_server', 'CustomHTTPRequestHandler']
