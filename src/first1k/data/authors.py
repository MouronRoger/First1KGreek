"""Authors data access module for First1KGreek.

This module provides functions for accessing and manipulating author data
in the First1KGreek browser application.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any

from ..config import AUTHORS_DATA_FILE

# Setup logging
logger = logging.getLogger(__name__)

# Global cache for author data
_AUTHORS_DATA = None


def load_authors_data() -> Dict[str, Any]:
    """Load authors data from disk.
    
    Returns:
        dict: Dictionary of author data keyed by author ID
    
    Raises:
        FileNotFoundError: If authors data file is not found
        json.JSONDecodeError: If authors data file contains invalid JSON
    """
    global _AUTHORS_DATA
    
    if _AUTHORS_DATA is None:
        logger.info(f"Loading authors data from {AUTHORS_DATA_FILE}")
        try:
            with open(AUTHORS_DATA_FILE, 'r', encoding='utf-8') as f:
                _AUTHORS_DATA = json.load(f)
                logger.info(f"Loaded data for {len(_AUTHORS_DATA)} authors")
        except FileNotFoundError:
            logger.error(f"Authors data file not found: {AUTHORS_DATA_FILE}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing authors data file: {e}")
            raise
    
    return _AUTHORS_DATA


def reload_authors_data() -> Dict[str, Any]:
    """Force reload of authors data from disk.
    
    Returns:
        dict: Dictionary of author data keyed by author ID
    """
    global _AUTHORS_DATA
    _AUTHORS_DATA = None
    return load_authors_data()


def get_author(author_id: str) -> Optional[Dict[str, Any]]:
    """Get data for a specific author.
    
    Args:
        author_id: Author ID (e.g., 'tlg0001')
        
    Returns:
        Optional[Dict[str, Any]]: Author data or None if not found
    """
    authors_data = load_authors_data()
    return authors_data.get(author_id)


def get_all_authors() -> List[Dict[str, Any]]:
    """Get data for all authors.
    
    Returns:
        List[Dict[str, Any]]: List of author data dictionaries
    """
    authors_data = load_authors_data()
    return [
        {"id": author_id, **author_data} 
        for author_id, author_data in authors_data.items()
    ]


def get_filtered_authors(
    century: Optional[int] = None,
    author_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get filtered list of authors.
    
    Args:
        century: Optional filter by century
        author_type: Optional filter by author type
        skip: Number of authors to skip (for pagination)
        limit: Maximum number of authors to return
        
    Returns:
        List[Dict[str, Any]]: Filtered list of author data dictionaries
    """
    authors = get_all_authors()
    
    # Apply filters
    if century is not None:
        authors = [a for a in authors if a.get('century') == century]
    
    if author_type is not None:
        authors = [a for a in authors if a.get('type') == author_type]
    
    # Apply pagination
    return authors[skip:skip + limit]


async def async_load_authors_data() -> Dict[str, Any]:
    """Async wrapper for load_authors_data.
    
    Returns:
        dict: Dictionary of author data keyed by author ID
    """
    return load_authors_data()


async def async_get_author(author_id: str) -> Optional[Dict[str, Any]]:
    """Async wrapper for get_author.
    
    Args:
        author_id: Author ID (e.g., 'tlg0001')
        
    Returns:
        Optional[Dict[str, Any]]: Author data or None if not found
    """
    return get_author(author_id)


async def async_get_all_authors() -> List[Dict[str, Any]]:
    """Async wrapper for get_all_authors.
    
    Returns:
        List[Dict[str, Any]]: List of author data dictionaries
    """
    return get_all_authors()


async def async_get_filtered_authors(
    century: Optional[int] = None,
    author_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Async wrapper for get_filtered_authors.
    
    Args:
        century: Optional filter by century
        author_type: Optional filter by author type
        skip: Number of authors to skip (for pagination)
        limit: Maximum number of authors to return
        
    Returns:
        List[Dict[str, Any]]: Filtered list of author data dictionaries
    """
    return get_filtered_authors(century, author_type, skip, limit) 