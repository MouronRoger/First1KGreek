"""View API router for First1KGreek FastAPI implementation.

This module implements API endpoints for viewing content in the First1KGreek corpus.
"""

import logging
import os
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import HTMLResponse, PlainTextResponse

from ..handlers import view as view_handler
from ..utils.path import is_valid_path, to_absolute_path, normalize_path

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/view",
    tags=["view"],
    responses={404: {"description": "Not found"}},
)


@router.get("/xml", response_class=HTMLResponse)
async def view_xml(
    path: str = Query(..., description="Path to the XML file to view")
):
    """Get XML content with syntax highlighting.
    
    This endpoint returns HTML with the XML content and syntax highlighting.
    
    Args:
        path: Path to the XML file
        
    Returns:
        HTMLResponse: HTML with syntax-highlighted XML
        
    Raises:
        HTTPException: If file not found or invalid
    """
    logger.info(f"Viewing XML content for {path}")
    
    try:
        # Convert to absolute path and validate
        full_path = to_absolute_path(path)
        
        # Validate that the file exists and is an XML file
        if not is_valid_path(path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
            
        if not full_path.endswith('.xml'):
            raise HTTPException(status_code=400, detail="Only XML files are supported")
        
        # Call the async handler
        html_content = await view_handler.async_render_xml_view_page(full_path)
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing XML: {e}")
        raise HTTPException(status_code=500, detail=f"Error viewing XML: {str(e)}")


@router.get("/reader", response_class=HTMLResponse)
async def view_reader(
    path: str = Query(..., description="Path to the XML file to view in reader")
):
    """Get reader-friendly view of content.
    
    This endpoint returns HTML with a reader-friendly view of the content.
    
    Args:
        path: Path to the XML file
        
    Returns:
        HTMLResponse: HTML with reader-friendly content
        
    Raises:
        HTTPException: If file not found or invalid
    """
    logger.info(f"Viewing reader content for {path}")
    
    try:
        # Convert to absolute path and validate
        full_path = to_absolute_path(path)
        
        # Validate that the file exists and is an XML file
        if not is_valid_path(path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
            
        if not full_path.endswith('.xml'):
            raise HTTPException(status_code=400, detail="Only XML files are supported")
        
        # Call the async handler
        html_content = await view_handler.async_render_reader_view_page(full_path)
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing reader content: {e}")
        raise HTTPException(status_code=500, detail=f"Error viewing reader content: {str(e)}")


@router.get("/raw", response_class=PlainTextResponse)
async def view_raw(
    path: str = Query(..., description="Path to the file to view raw content")
):
    """Get raw file content.
    
    This endpoint returns the raw content of the file as plain text.
    
    Args:
        path: Path to the file
        
    Returns:
        PlainTextResponse: Raw file content
        
    Raises:
        HTTPException: If file not found
    """
    logger.info(f"Viewing raw content for {path}")
    
    try:
        # Convert to absolute path and validate
        full_path = to_absolute_path(path)
        
        # Validate that the file exists
        if not is_valid_path(path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # Read the file content using the async handler
        status_code, content_type, content = await view_handler.async_handle_view_raw({"path": full_path})
        
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail="Error reading file")
            
        return PlainTextResponse(content=content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing raw content: {e}")
        raise HTTPException(status_code=500, detail=f"Error viewing raw content: {str(e)}") 