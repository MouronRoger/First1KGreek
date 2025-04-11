"""Path utilities for First1KGreek Browser.

This module provides utility functions for handling paths in the application,
ensuring consistent behavior between HTTP and FastAPI modes.
"""

import os
import logging
from ..config import DATA_DIR

# Set up logging
logger = logging.getLogger(__name__)


def normalize_path(path):
    """Normalize a path to ensure consistent behavior across the application.
    
    This function handles both absolute and relative paths, ensuring they
    are properly formatted for file system access.
    
    Args:
        path (str): The path to normalize
        
    Returns:
        tuple: (full_path, relative_path) where:
            full_path is the absolute path for file system access
            relative_path is the relative path for web URLs
    """
    if not path:
        logger.error("Empty path provided to normalize_path")
        return None, None
        
    logger.info(f"Normalizing path: {path}")
    
    # Convert absolute path to relative path if it contains the data directory
    relative_path = path
    if os.path.isabs(path) and DATA_DIR in path:
        # Extract the relative part of the path from the data directory
        relative_path = os.path.relpath(path, os.path.dirname(DATA_DIR))
        logger.info(f"Converted absolute path to relative: {relative_path}")
    
    # Ensure the path is properly formatted for the file system
    full_path = path
    if not os.path.isabs(path):
        # If it's already a relative path, make sure it's relative to data directory
        if not path.startswith("data/"):
            relative_path = os.path.join("data", path)
        full_path = os.path.join(os.path.dirname(DATA_DIR), relative_path)
    
    logger.info(f"Normalized path: full_path={full_path}, relative_path={relative_path}")
    return full_path, relative_path


def to_absolute_path(path):
    """Convert a path to an absolute path for file system access.
    
    Args:
        path (str): The path to convert
        
    Returns:
        str: The absolute path
    """
    full_path, _ = normalize_path(path)
    return full_path


def to_relative_path(path):
    """Convert a path to a relative path for web URLs.
    
    Args:
        path (str): The path to convert
        
    Returns:
        str: The relative path
    """
    _, relative_path = normalize_path(path)
    return relative_path


def is_valid_path(path):
    """Check if a path is valid and exists.
    
    Args:
        path (str): The path to check
        
    Returns:
        bool: True if the path is valid and exists, False otherwise
    """
    if not path:
        return False
        
    full_path, _ = normalize_path(path)
    return full_path is not None and os.path.exists(full_path)


def create_data_path(*parts):
    """Create a path relative to the data directory.
    
    Args:
        *parts: Path parts to join
        
    Returns:
        str: The relative path
    """
    return os.path.join("data", *parts)


def create_file_url(path):
    """Create a URL for a file path.
    
    Args:
        path (str): The path to convert to a URL
        
    Returns:
        str: The URL
    """
    _, relative_path = normalize_path(path)
    return f"/view?path={relative_path}" if relative_path else None 