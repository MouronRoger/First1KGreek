"""Pydantic models for First1KGreek index data."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TextVersion(BaseModel):
    """A specific version of a text in a particular language."""
    
    id: str = Field(..., description="Unique identifier for the text version")
    language: str = Field(..., description="Language of the text (Greek or English)")
    path: str = Field(..., description="Path to the XML file")


class WorkTitles(BaseModel):
    """Titles for a work in different languages."""
    
    latin: Optional[str] = Field(None, description="Latin title")
    english: Optional[str] = Field(None, description="English title")
    greek: Optional[str] = Field(None, description="Greek title")


class Work(BaseModel):
    """A literary work by an author."""
    
    id: str = Field(..., description="Work identifier (e.g., 'tlg008')")
    titles: WorkTitles = Field(..., description="Titles in different languages")
    texts: List[TextVersion] = Field(default_factory=list, description="Available text versions")


class Author(BaseModel):
    """An author in the First1KGreek corpus."""
    
    id: str = Field(..., description="Author identifier (e.g., 'tlg0032')")
    name: str = Field(..., description="Author name")
    century: Optional[int] = Field(None, description="Century (negative for BCE, positive for CE)")
    type: Optional[str] = Field(None, description="Author type (e.g., 'Historian')")
    works: Dict[str, Work] = Field(default_factory=dict, description="Works by this author")


class Index(BaseModel):
    """The complete First1KGreek index."""
    
    authors: Dict[str, Author] = Field(default_factory=dict, description="Authors by ID")
    version: str = Field("1.0.0", description="Index format version")
    generated_at: str = Field(..., description="Timestamp when index was generated") 