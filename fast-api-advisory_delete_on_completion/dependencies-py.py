"""Dependencies for First1KGreek FastAPI application.

This module provides FastAPI dependency functions for reusable components.
"""

from fastapi import Depends, HTTPException, status
from typing import Dict, Optional
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

async def verify_file_exists(path: str) -> str:
    """
    Verify that a file exists.
    
    Args:
        path: The file path to verify
        
    Returns:
        The verified file path
        
    Raises:
        HTTPException: If the file does not exist
    """
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path}"
        )
    return path

async def verify_author_exists(author_id: str) -> str:
    """
    Verify that an author exists.
    
    Args:
        author_id: The author ID to verify
        
    Returns:
        The verified author ID
        
    Raises:
        HTTPException: If the author does not exist
    """
    author_dir = os.path.join('data', author_id)
    if not os.path.exists(author_dir):
        logger.error(f"Author not found: {author_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author {author_id} not found"
        )
    return author_id

def get_request_metadata(request_id: Optional[str] = None) -> Dict:
    """
    Get metadata for request logging and tracking.
    
    Args:
        request_id: Optional request ID for tracking
        
    Returns:
        Dictionary with request metadata
    """
    metadata = {
        "request_id": request_id or "unknown",
        "timestamp": "",  # Will be set by the logging middleware
    }
    return metadata
