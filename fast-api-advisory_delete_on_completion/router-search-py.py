"""Search router for First1KGreek FastAPI application.

This module provides API routes for search functionality.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models import SearchResponse, SearchResult
from ..handlers import api as api_handlers

# Create router for search endpoints
router = APIRouter(
    prefix="/api/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=SearchResponse)
async def search_texts(
    q: str = Query(..., min_length=1, description="Search query")
):
    """Search texts for a specific term"""
    results = api_handlers.search_corpus(q)
    return {
        "results": results,
        "total": len(results),
        "query": q
    }
