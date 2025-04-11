from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Author(BaseModel):
    """Author model for API responses"""
    id: str
    name: str
    century: Optional[int] = None
    type: Optional[str] = None
    works_count: int = 0
    is_favorite: bool = False
    is_archived: bool = False

class Work(BaseModel):
    """Work model for API responses"""
    id: str
    title: str
    language: str = "Greek"
    file_path: str
    is_favorite: bool = False
    is_archived: bool = False
    
    class Config:
        """Pydantic config"""
        schema_extra = {
            "example": {
                "id": "tlg0007.tlg136.perseus-grc2",
                "title": "De Stoicorum Repugnantiis",
                "language": "Greek",
                "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
                "is_favorite": False,
                "is_archived": False
            }
        }

class WorkPreference(BaseModel):
    """Work preference update model"""
    work_id: str
    type: str = Field(..., description="Type of preference: 'favorite', 'archive', or 'delete'")
    action: str = Field(..., description="Action to perform: 'add' or 'remove'")

class UserPreferences(BaseModel):
    """User preferences model for bulk updates"""
    favorites: List[str] = Field(default_factory=list)
    archived: List[str] = Field(default_factory=list)

class SearchResult(BaseModel):
    """Search result model"""
    file_path: str
    author: str
    title: str
    editor: Optional[str] = None
    context: str
    occurrence_count: int

class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    total: int
    query: str

class XMLViewResponse(BaseModel):
    """XML view response model"""
    content: str
    author: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = None
    file_path: str

class ReaderViewResponse(BaseModel):
    """Reader view response model"""
    content: str
    author: Optional[str] = None
    title: Optional[str] = None
    language: Optional[str] = None
    file_path: str
