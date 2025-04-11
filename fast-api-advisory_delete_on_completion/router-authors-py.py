"""Authors router for First1KGreek FastAPI application.

This module provides API routes for author-related functionality.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..models import Author, Work
from ..handlers import api as api_handlers

# Create router for authors endpoints
router = APIRouter(
    prefix="/api/authors",
    tags=["authors"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Author])
async def get_authors(
    search: Optional[str] = None,
    century: Optional[int] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100)
):
    """Get list of authors with optional filtering"""
    return api_handlers.get_authors_list(search, century, type, page, limit)

@router.get("/{author_id}", response_model=Author)
async def get_author(author_id: str):
    """Get details for a specific author"""
    author = api_handlers.get_author_details(author_id)
    if not author:
        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
    return author

@router.get("/{author_id}/works", response_model=List[Work])
async def get_author_works(author_id: str):
    """Get works for a specific author"""
    works = api_handlers.get_author_works_for_api(author_id)
    if not works and not api_handlers.author_exists(author_id):
        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
    return works
