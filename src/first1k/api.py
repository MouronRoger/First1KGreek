"""FastAPI application for First1KGreek.

This module defines the FastAPI application for the First1KGreek browser.
"""

import logging
import sys
import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.openapi.utils import get_openapi

from .config import VERSION, VERSION_NAME, DATA_DIR, BASE_DIR
from .routers import authors, preferences, search, view
from .handlers import browse, ui, works, view as view_handler, search as search_handler
from .handlers import api as api_handler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log critical path information for debugging
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"DATA_DIR: {DATA_DIR}")
logger.info(f"Current working directory: {os.getcwd()}")

# Create FastAPI application
app = FastAPI(
    title="First1KGreek API",
    description="API for First1K Greek browser application",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory with absolute path
static_dir = os.path.join(BASE_DIR, "static")
logger.info(f"Mounting static files directory: {static_dir}")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory not found at {static_dir}")
    # Create the directory to avoid startup errors
    try:
        os.makedirs(static_dir, exist_ok=True)
        logger.info(f"Created static directory at {static_dir}")
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    except Exception as e:
        logger.error(f"Failed to create static directory: {e}")

# Include API routers
app.include_router(authors.router)
app.include_router(preferences.router)
app.include_router(search.router)
app.include_router(view.router)

# Add UI routes

@app.get("/", response_class=RedirectResponse)
async def home():
    """Redirect root to authors page."""
    return RedirectResponse(url="/browse/authors")

@app.get("/browse/authors", response_class=HTMLResponse)
async def browse_authors():
    """Render the authors page."""
    status_code, content_type, html = browse.handle_browse_authors({})
    return HTMLResponse(content=html)

@app.get("/browse/editors", response_class=HTMLResponse)
async def browse_editors():
    """Render the editors page."""
    status_code, content_type, html = browse.handle_browse_editors({})
    return HTMLResponse(content=html)

@app.get("/author/{author_id}", response_class=HTMLResponse)
async def author_detail(author_id: str):
    """Render the author detail page."""
    status_code, content_type, html = browse.handle_home_page({"author_id": author_id})
    return HTMLResponse(content=html)

@app.get("/works/{author_id}", response_class=HTMLResponse)
async def author_works(author_id: str):
    """Render the author works page."""
    # This endpoint should not use handle_get_author_works as it returns JSON, not HTML
    # Instead, it should use a handler that returns HTML for the works page
    # For now, redirect to the browse/authors page
    return RedirectResponse(url="/browse/authors")

@app.get("/xml", response_class=HTMLResponse)
async def xml_view(path: str):
    """Render the XML view page.
    
    Args:
        path (str): Path to the XML file
        
    Returns:
        HTMLResponse: The HTML content
    """
    logger.info(f"XML View requested for path: {path}")
    
    # Handle the request using the updated view handler
    status_code, content_type, html = await view_handler.async_handle_view_xml({"path": path})
    
    # If error, log it
    if status_code != 200:
        logger.error(f"Error rendering XML view: {status_code}")
        
    # Return the HTML response with appropriate status code
    return HTMLResponse(content=html, status_code=status_code)

@app.get("/reader", response_class=HTMLResponse)
async def reader_view(path: str):
    """Render the reader view page.
    
    Args:
        path (str): Path to the XML file
        
    Returns:
        HTMLResponse: The HTML content
    """
    logger.info(f"Reader View requested for path: {path}")
    
    # Handle the request using the updated view handler
    status_code, content_type, html = await view_handler.async_handle_view_reader({"path": path})
    
    # If error, log it
    if status_code != 200:
        logger.error(f"Error rendering reader view: {status_code}")
        
    # Return the HTML response with appropriate status code
    return HTMLResponse(content=html, status_code=status_code)

@app.get("/search", response_class=HTMLResponse)
async def search_page(q: str = None):
    """Render the search page."""
    query_params = {}
    if q:
        query_params["q"] = q
    status_code, content_type, html = search_handler.handle_search_request(query_params)
    return HTMLResponse(content=html)

# Add the missing legacy API endpoints
@app.get("/get_author_works")
async def get_author_works(author_id: str):
    """Legacy endpoint to get works for an author.
    
    Args:
        author_id: Author ID
        
    Returns:
        JSONResponse: List of author's works
    """
    logger.info(f"Handling /get_author_works request for author_id: {author_id}")
    
    try:
        # Check if author directory exists
        author_dir = os.path.join(DATA_DIR, author_id)
        logger.info(f"Looking for author directory at: {author_dir}")
        
        if not os.path.exists(author_dir):
            logger.warning(f"Author directory not found: {author_dir}")
            return JSONResponse(
                status_code=404,
                content={"error": f"Author {author_id} not found"}
            )
            
        # Get author works directly from the handler function
        works = api_handler.get_author_works_for_api(author_id)
        
        if not works:
            logger.warning(f"No works found for author: {author_id}")
            return JSONResponse(content=[])
            
        logger.info(f"Successfully retrieved {len(works)} works for author {author_id}")
        logger.debug(f"Works data: {works}")
        
        # Return works directly as JSON content
        return JSONResponse(content=works)
    except Exception as e:
        logger.error(f"Error retrieving works for {author_id}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error retrieving works: {str(e)}"}
        )

@app.post("/update_work_preference")
async def update_work_preference(request: Request):
    """Legacy endpoint to update work preference.
    
    Args:
        request: Request object with preference data
        
    Returns:
        JSONResponse: Result of the operation
    """
    post_data = await request.json()
    status_code, content_type, response_data = preferences.handle_update_work_preference({}, post_data)
    
    # Parse the JSON string if it's not already a dict/list
    if isinstance(response_data, str):
        response_data = json.loads(response_data)
        
    return JSONResponse(content=response_data)

@app.post("/update_preferences")
async def update_preferences(request: Request):
    """Legacy endpoint to update batch preferences.
    
    Args:
        request: Request object with preference data
        
    Returns:
        JSONResponse: Result of the operation
    """
    post_data = await request.json()
    status_code, content_type, response_data = preferences.handle_update_preference({}, post_data)
    
    # Parse the JSON string if it's not already a dict/list
    if isinstance(response_data, str):
        response_data = json.loads(response_data)
        
    return JSONResponse(content=response_data)

# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema.
    
    Returns:
        dict: OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/api/health")
async def health_check():
    """Check if the API is running.
    
    Returns:
        dict: Status information about the API
    """
    return {"status": "ok", "version": VERSION, "name": VERSION_NAME}

@app.get("/shutdown")
async def shutdown():
    """Shutdown the server (development only).
    
    Returns:
        dict: Shutdown message
    """
    if os.environ.get("PRODUCTION", "false").lower() == "true":
        return {"message": "Shutdown not available in production mode"}
    
    # Schedule the server shutdown
    def shutdown_server():
        logger.info("Shutting down server...")
        os._exit(0)
    
    # Use a thread to allow the response to be sent before shutdown
    import threading
    threading.Timer(1.0, shutdown_server).start()
    
    return {"message": "Server is shutting down..."} 