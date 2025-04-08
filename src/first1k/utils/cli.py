#!/usr/bin/env python3
"""
Command line interface utilities for First1KGreek Browser.

This module provides functions for parsing command line arguments
and other CLI-related functionality.
"""

import argparse


def parse_args():
    """
    Parse command line arguments for the server.
    
    Returns:
        argparse.Namespace: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='First1KGreek Browser',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000, 
        help='Port to run the server on'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information and exit'
    )
    
    parser.add_argument(
        '--no-browser', 
        action='store_true',
        help='Do not automatically open a web browser'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind the server to (use 0.0.0.0 to allow external connections)'
    )
    
    return parser.parse_args() 