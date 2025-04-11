"""Search API router for First1KGreek FastAPI implementation.

This module implements API endpoints for searching the First1KGreek corpus.
"""

import logging
import time
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from ..models import SearchQuery, SearchResult, SearchResponse
from ..handlers import search as search_handler

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=SearchResponse)
async def search_corpus(
    query: str = Query(..., description="Text to search for"),
    authors: Optional[List[str]] = Query(None, description="Author IDs to limit search"),
    language: Optional[str] = Query(None, description="Language filter (grc, eng)"),
    max_results: int = Query(100, description="Maximum number of results to return")
):
    """Search the corpus for a text query.
    
    This endpoint searches all XML files in the corpus for the given query text.
    Results can be filtered by author and language.
    
    Args:
        query: Text to search for
        authors: Optional list of author IDs to limit search scope
        language: Optional language filter
        max_results: Maximum number of results to return
        
    Returns:
        SearchResponse: Search results with metadata
    """
    logger.info(f"Searching corpus for '{query}' (authors: {authors}, language: {language})")
    start_time = time.time()
    
    try:
        # Call the existing search function
        raw_results = search_handler.search_corpus(query)
        
        # Filter results if necessary
        if authors:
            filtered_results = []
            for result in raw_results:
                # Extract author ID from file path
                # Example: data/tlg0001/... -> tlg0001
                path_parts = result["file_path"].split('/')
                if len(path_parts) > 1:
                    author_id = path_parts[1]
                    if author_id in authors:
                        filtered_results.append(result)
            raw_results = filtered_results
            
        if language:
            filtered_results = []
            for result in raw_results:
                # Check if language matches
                result_language = "grc"  # Default to Greek
                if "perseus-eng" in result["file_path"]:
                    result_language = "eng"
                elif "perseus-grc" in result["file_path"]:
                    result_language = "grc"
                
                if result_language == language:
                    filtered_results.append(result)
            raw_results = filtered_results
        
        # Limit results
        raw_results = raw_results[:max_results]
        
        # Convert to Pydantic models
        results = []
        for result in raw_results:
            # Extract author ID and work ID from file path
            path_parts = result["file_path"].split('/')
            author_id = path_parts[1] if len(path_parts) > 1 else "unknown"
            work_id = path_parts[2] if len(path_parts) > 2 else "unknown"
            
            results.append(SearchResult(
                author_id=author_id,
                work_id=work_id,
                file_path=result["file_path"],
                excerpt=result["context"],
                language="eng" if "perseus-eng" in result["file_path"] else "grc"
            ))
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            query=query,
            results=results,
            total_found=len(raw_results),
            executed_in=execution_time
        )
    except Exception as e:
        logger.error(f"Error searching corpus: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching corpus: {str(e)}") 