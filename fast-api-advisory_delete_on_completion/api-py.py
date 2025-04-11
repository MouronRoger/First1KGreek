from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Optional
from . import config
from .models import Author, Work, UserPreferences
from .handlers import api as api_handlers

# Create FastAPI app
app = FastAPI(
    title="First1KGreek API",
    description="API for browsing and searching ancient Greek texts",
    version=config.VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": config.VERSION}

# Authors endpoints
@app.get("/api/authors", response_model=List[Author])
async def get_authors(
    search: Optional[str] = None,
    century: Optional[int] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100)
):
    """Get list of authors with optional filtering"""
    return api_handlers.get_authors_list(search, century, type, page, limit)

@app.get("/api/authors/{author_id}", response_model=Author)
async def get_author(author_id: str):
    """Get details for a specific author"""
    author = api_handlers.get_author_details(author_id)
    if not author:
        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
    return author

@app.get("/api/authors/{author_id}/works", response_model=List[Work])
async def get_author_works(author_id: str):
    """Get works for a specific author (converted from existing /get_author_works endpoint)"""
    works = api_handlers.get_author_works_for_api(author_id)
    if not works and not api_handlers.author_exists(author_id):
        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
    return works

# Preferences endpoints
@app.post("/api/preferences/work")
async def update_work_preference(preference_data: dict):
    """Update preference for a specific work (converted from existing /update_work_preference endpoint)"""
    result = api_handlers.update_work_preference(preference_data)
    return result

@app.post("/api/preferences/batch")
async def update_batch_preferences(preferences_data: UserPreferences):
    """Bulk update preferences (converted from existing /update_preferences endpoint)"""
    result = api_handlers.update_bulk_preferences(preferences_data.dict())
    return result

# Search endpoint
@app.get("/api/search")
async def search_texts(q: str):
    """Search texts for a specific term"""
    return api_handlers.search_corpus(q)

# View endpoints
@app.get("/api/view/xml")
async def view_xml(path: str):
    """Get XML content for a file"""
    content = api_handlers.get_xml_content(path)
    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return {"content": content}

@app.get("/api/view/reader")
async def view_reader(path: str):
    """Get reader-friendly content for a file"""
    content = api_handlers.get_reader_content(path)
    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return {"content": content}

# Run the server directly (for development)
if __name__ == "__main__":
    uvicorn.run("first1k.api:app", host=config.HOST, port=config.PORT, reload=True)
