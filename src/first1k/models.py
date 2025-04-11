"""Pydantic models for First1KGreek FastAPI implementation.

This module defines Pydantic models for request and response validation in the First1KGreek API.
Models are used for data validation, serialization, and documentation generation.
"""

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
import logging

# Set up logging
logger = logging.getLogger(__name__)


class Author(BaseModel):
    """Model representing an author in the First1KGreek corpus.
    
    Attributes:
        id: Unique identifier for the author (e.g., 'tlg0001')
        name: Full name of the author
        century: Century when the author lived (negative for BCE, positive for CE)
        type: Type or category of the author (e.g., 'historian', 'poet')
    """
    
    id: str = Field(..., description="Author identifier, e.g., 'tlg0001'")
    name: str = Field(..., description="Full name of the author")
    century: int = Field(..., description="Century (negative for BCE, positive for CE)")
    type: str = Field(..., description="Author type or category")


class Work(BaseModel):
    """Model representing a literary work in the First1KGreek corpus.
    
    Attributes:
        id: Unique identifier for the work (e.g., 'tlg001')
        title: Title of the work
        author_id: ID of the author who wrote this work
        language: Language of the work (e.g., 'grc' for Greek, 'eng' for English)
        files: List of available file formats for this work
    """
    
    id: str = Field(..., description="Work identifier, e.g., 'tlg001'")
    title: str = Field(..., description="Title of the work")
    author_id: str = Field(..., description="ID of the author of this work")
    language: str = Field("grc", description="Language code ('grc' for Greek, 'eng' for English)")
    files: List[str] = Field(default_factory=list, description="Available file formats")


class WorkFile(BaseModel):
    """Model for a work file."""
    name: str = Field(..., description="File name")
    type: str = Field(..., description="File type (e.g., 'xml')")
    path: str = Field(..., description="File path")


class UserPreference(BaseModel):
    """Model representing user preferences for authors and works.
    
    Attributes:
        author_id: Author identifier
        work_id: Optional work identifier (if preference applies to a specific work)
        preference_type: Type of preference ('favorite', 'archived', 'deleted')
        value: Boolean value of the preference
    """
    
    author_id: str = Field(..., description="Author identifier")
    work_id: Optional[str] = Field(None, description="Work identifier (if applicable)")
    preference_type: str = Field(..., description="Type of preference (favorite, archived, deleted)")
    value: bool = Field(..., description="Preference value (true/false)")


class BatchPreferences(BaseModel):
    """Model for batch updating user preferences.
    
    Attributes:
        preferences: List of UserPreference objects to update
    """
    
    preferences: List[UserPreference] = Field(..., description="List of preferences to update")


class SearchQuery(BaseModel):
    """Model for search requests.
    
    Attributes:
        query: Text to search for
        authors: Optional list of author IDs to limit search scope
        language: Optional language filter
        max_results: Maximum number of results to return
    """
    
    query: str = Field(..., description="Text to search for")
    authors: Optional[List[str]] = Field(None, description="Author IDs to limit search")
    language: Optional[str] = Field(None, description="Language filter (grc, eng)")
    max_results: int = Field(100, description="Maximum number of results to return")


class SearchResult(BaseModel):
    """Model for search result items.
    
    Attributes:
        author_id: Author identifier
        work_id: Work identifier
        file_path: Path to the file containing the match
        excerpt: Text excerpt containing the match
        language: Language of the content
    """
    
    author_id: str = Field(..., description="Author identifier")
    work_id: str = Field(..., description="Work identifier")
    file_path: str = Field(..., description="Path to the file")
    excerpt: str = Field(..., description="Text excerpt with match")
    language: str = Field(..., description="Language of the content")


class SearchResponse(BaseModel):
    """Model for search response.
    
    Attributes:
        query: Original search query
        results: List of search results
        total_found: Total number of matches found
        executed_in: Search execution time in milliseconds
    """
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of matches")
    executed_in: float = Field(..., description="Execution time in milliseconds")


class APIResponse(BaseModel):
    """Generic API response model.
    
    Attributes:
        success: Whether the request was successful
        message: Response message
        data: Optional response data
    """
    
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")


class Work(BaseModel):
    """Model for a work."""
    id: str = Field(..., description="Work ID")
    title: str = Field(..., description="Work title")
    author_id: str = Field(..., description="Author ID")
    language: str = Field(..., description="Work language")
    file_path: str = Field(..., description="Path to the work file")
    is_favorite: bool = Field(False, description="Whether the work is favorited")
    is_archived: bool = Field(False, description="Whether the work is archived")
    files: Optional[List[WorkFile]] = Field(None, description="List of files associated with the work") 