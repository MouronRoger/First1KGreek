"""FastAPI application for First1KGreek Browser.

This module provides the FastAPI application for the First1KGreek Browser,
replacing the original HTTP server with a modern API server.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from . import config
from .middleware import LoggingMiddleware
from .routers import authors, preferences, search, view

# Create FastAPI app
app = FastAPI(
    title="First1KGreek API",
    description="API for browsing and searching ancient Greek texts",
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(authors.router)
app.include_router(preferences.router)
app.include_router(search.router)
app.include_router(view.router)

# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """Check API health status"""
    return {
        "status": "ok",
        "version": config.VERSION,
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/", tags=["info"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "First1KGreek API",
        "version": config.VERSION,
        "description": "API for browsing and searching ancient Greek texts",
        "documentation": "/docs"
    }

# Example enhanced endpoint showcasing FastAPI features
@app.get("/api/info", tags=["info"])
async def info(request: Request):
    """Get detailed API information"""
    return {
        "name": "First1KGreek API",
        "version": config.VERSION,
        "features": config.FEATURES,
        "last_updated": config.LAST_UPDATED,
        "client": {
            "host": request.client.host if request.client else "unknown",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    }

# Run the server directly (for development)
if __name__ == "__main__":
    uvicorn.run("src.first1k.api:app", host=config.HOST, port=config.PORT, reload=True)
