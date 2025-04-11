"""FastAPI implementation for First1KGreek browser.

This module provides a FastAPI implementation for the First1KGreek browser,
enabling API access with automatic documentation and type validation.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Import routers
from .routers.authors import router as authors_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="First1KGreek API",
    description="API for accessing and interacting with the First1KGreek corpus",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema for API documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="First1KGreek API",
        version="1.0.0",
        description="API for accessing ancient Greek texts from the First1KGreek corpus",
        routes=app.routes,
    )
    
    # Add additional information to the schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/api/health")
async def health_check():
    """Check if the API is running.
    
    Returns:
        dict: Status information about the API
    """
    return {"status": "ok", "message": "API is running"}


# Include routers
app.include_router(authors_router)

# These will be implemented in separate modules
# app.include_router(works_router)
# app.include_router(preferences_router)
# app.include_router(search_router)
# app.include_router(view_router) 