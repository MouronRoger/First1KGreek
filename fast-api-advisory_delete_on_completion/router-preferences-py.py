"""Preferences router for First1KGreek FastAPI application.

This module provides API routes for user preferences functionality.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from ..models import UserPreferences, WorkPreference
from ..handlers import api as api_handlers

# Create router for preferences endpoints
router = APIRouter(
    prefix="/api/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}},
)

@router.post("/work")
async def update_work_preference(preference_data: WorkPreference):
    """Update preference for a specific work"""
    result = api_handlers.update_work_preference(preference_data.dict())
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.post("/batch")
async def update_batch_preferences(preferences_data: UserPreferences):
    """Bulk update preferences"""
    result = api_handlers.update_bulk_preferences(preferences_data.dict())
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.get("/")
async def get_preferences():
    """Get current user preferences"""
    return api_handlers.get_user_preferences()
