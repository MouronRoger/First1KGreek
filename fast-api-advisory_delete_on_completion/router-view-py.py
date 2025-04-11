"""View router for First1KGreek FastAPI application.

This module provides API routes for viewing text content.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models import XMLViewResponse, ReaderViewResponse
from ..handlers import api as api_handlers

# Create router for view endpoints
router = APIRouter(
    prefix="/api/view",
    tags=["view"],
    responses={404: {"description": "Not found"}},
)

@router.get("/xml", response_model=XMLViewResponse)
async def view_xml(
    path: str = Query(..., description="Path to XML file")
):
    """Get XML content for a file"""
    content = api_handlers.get_xml_content(path)
    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return content

@router.get("/reader", response_model=ReaderViewResponse)
async def view_reader(
    path: str = Query(..., description="Path to XML file")
):
    """Get reader-friendly content for a file"""
    content = api_handlers.get_reader_content(path)
    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return content
