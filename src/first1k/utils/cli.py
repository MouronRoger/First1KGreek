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
    parser = argparse.ArgumentParser(description='First1KGreek Browser')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args() 