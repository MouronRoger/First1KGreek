"""Preferences API router for First1KGreek FastAPI implementation.

This module implements API endpoints for managing user preferences in the First1KGreek corpus.
"""

import json
import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel

from ..models import UserPreference, BatchPreferences, APIResponse
from ..handlers import preferences as prefs_handlers

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}},
)


@router.post("/work", response_model=APIResponse)
async def update_work_preference(preference: UserPreference):
    """Update preference for a specific work.
    
    This endpoint handles adding/removing works from favorites, archived, and deleted lists.
    
    Args:
        preference: User preference data
        
    Returns:
        APIResponse: Result of the operation
    """
    logger.info(f"Updating work preference: {preference}")
    
    try:
        # Convert to the format expected by the handler
        post_data = {
            "work_id": preference.work_id or preference.author_id,
            "type": preference.preference_type,
            "action": "add" if preference.value else "remove"
        }
        
        # Call the existing handler (without query params)
        status_code, _, response_data = prefs_handlers.handle_update_work_preference({}, post_data)
        
        # Parse the JSON string if needed
        if isinstance(response_data, str):
            response_data = json.loads(response_data)
        
        if status_code == 200:
            return APIResponse(
                success=True,
                message=f"Updated {preference.preference_type} preference for {preference.work_id or preference.author_id}",
                data=None
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=response_data.get("error", "Failed to update preference")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating work preference: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating preference: {str(e)}")


@router.post("/batch", response_model=APIResponse)
async def update_batch_preferences(preferences: BatchPreferences):
    """Update multiple preferences in a single request.
    
    Args:
        preferences: Batch of user preferences to update
        
    Returns:
        APIResponse: Result of the operation
    """
    logger.info(f"Updating batch preferences: {len(preferences.preferences)} items")
    
    try:
        # Process each preference in the batch
        for pref in preferences.preferences:
            post_data = {
                "work_id": pref.work_id or pref.author_id,
                "type": pref.preference_type,
                "action": "add" if pref.value else "remove"
            }
            
            # Call the existing handler (passing the post_data directly)
            status_code, _, response_data = prefs_handlers.handle_update_work_preference({}, post_data)
            
            # Parse the JSON string if needed
            if isinstance(response_data, str):
                response_data = json.loads(response_data)
            
            if status_code != 200:
                error_message = response_data.get("error", f"Failed to update preference for {pref.work_id or pref.author_id}")
                raise HTTPException(status_code=400, detail=error_message)
                
        return APIResponse(
            success=True,
            message=f"Successfully updated {len(preferences.preferences)} preferences",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating batch preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.get("/", response_model=Dict)
async def get_preferences():
    """Get all user preferences.
    
    Returns:
        Dict: User preferences including favorites and archived items
    """
    logger.info("Getting user preferences")
    
    try:
        # Call the existing handler function
        user_prefs = prefs_handlers.get_user_preferences()
        return user_prefs
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting preferences: {str(e)}") 