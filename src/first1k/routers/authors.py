"""Authors API router for First1KGreek FastAPI implementation.

This module implements API endpoints for accessing author data in the First1KGreek corpus.
"""

import logging
import os
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel

from ..models import Author, Work, APIResponse, WorkFile
from ..data import authors as authors_dao
from ..utils import api_handler
from ..utils.path import is_valid_path, robust_author_path
from ..config import DATA_DIR

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/authors",
    tags=["authors"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Author])
async def list_authors(
    skip: int = Query(0, description="Number of authors to skip"),
    limit: int = Query(100, description="Maximum number of authors to return"), 
    century: Optional[int] = Query(None, description="Filter by century"),
    type: Optional[str] = Query(None, description="Filter by author type")
):
    """List authors with optional filtering and pagination.
    
    Args:
        skip: Number of authors to skip (for pagination)
        limit: Maximum number of authors to return
        century: Optional filter by century
        type: Optional filter by author type
        
    Returns:
        List[Author]: List of author objects
    """
    logger.info(f"Listing authors with skip={skip}, limit={limit}, century={century}, type={type}")
    
    try:
        authors = await authors_dao.async_get_filtered_authors(
            century=century,
            author_type=type,
            skip=skip,
            limit=limit
        )
        
        # Convert to Pydantic models
        return [
            Author(
                id=author["id"],
                name=author["name"],
                century=author["century"],
                type=author.get("type", "unknown")
            )
            for author in authors
        ]
    except Exception as e:
        logger.error(f"Error listing authors: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing authors: {str(e)}")


@router.get("/{author_id}", response_model=Author)
async def get_author(
    author_id: str = Path(..., description="The ID of the author to get")
):
    """Get details for a specific author.
    
    Args:
        author_id: Author ID (e.g., 'tlg0001')
        
    Returns:
        Author: Author details
        
    Raises:
        HTTPException: If author is not found
    """
    logger.info(f"Getting author details for {author_id}")
    
    try:
        author = await authors_dao.async_get_author_by_id(author_id)
        
        if not author:
            raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
        
        # Convert to Pydantic model
        return Author(
            id=author_id,
            name=author["name"],
            century=author["century"],
            type=author.get("type", "unknown")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting author {author_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting author: {str(e)}")


@router.get("/{author_id}/works", response_model=List[Work])
async def get_author_works(
    author_id: str = Path(..., description="The ID of the author")
):
    """Get works for a specific author.
    
    Args:
        author_id: Author ID (e.g., 'tlg0001')
        
    Returns:
        List[Work]: List of works by the author
        
    Raises:
        HTTPException: If author is not found
    """
    logger.info(f"API Router - Getting works for author {author_id}")
    
    try:
        # Use the robust path utility instead
        author_dir = robust_author_path(author_id)
        
        logger.info(f"API Router - Author dir absolute path: {author_dir}")
        logger.info(f"API Router - Current working directory: {os.getcwd()}")
        logger.info(f"API Router - Does author_dir exist? {os.path.exists(author_dir)}")
        
        if not author_dir or not os.path.exists(author_dir):
            logger.warning(f"API Router - Author {author_id} directory not found at {author_dir}")
            raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
        
        # Get works directly using the handler function
        works = api_handler.get_author_works_for_api(author_id)
        
        # Convert to Pydantic models
        return [
            Work(
                id=work["id"],
                title=work["title"],
                author_id=work.get("author_id", author_id),
                language=work["language"],
                file_path=work["file_path"],
                is_favorite=work.get("is_favorite", False),
                is_archived=work.get("is_archived", False),
                files=[WorkFile(**file) for file in work.get("files", [])]
            )
            for work in works
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API Router - Error getting works for author {author_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting author works: {str(e)}") 