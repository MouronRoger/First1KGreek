"""Static file handling for First1KGreek FastAPI application.

This module provides functionality for serving static files and HTML templates.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

def setup_static_files(app: FastAPI) -> None:
    """
    Set up static file serving for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Mount static files directory
    app.mount("/static", StaticFiles(directory="static"), name="static")

def setup_templates(app: FastAPI) -> Jinja2Templates:
    """
    Set up Jinja2 templates for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
        
    Returns:
        Jinja2Templates: The templates instance
    """
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    if not templates_dir.exists():
        os.makedirs(templates_dir)
    
    # Initialize templates
    templates = Jinja2Templates(directory=templates_dir)
    
    return templates

def setup_html_routes(app: FastAPI, templates: Jinja2Templates) -> None:
    """
    Set up HTML routes for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
        templates: The Jinja2Templates instance
    """
    # Check if templates directory contains necessary files
    templates_dir = Path("templates")
    
    # Only set up routes if template files exist
    if (templates_dir / "index.html").exists():
        @app.get("/", response_class=HTMLResponse, tags=["html"])
        async def home(request: Request):
            """Serve the home page"""
            return templates.TemplateResponse("index.html", {"request": request})
    
    if (templates_dir / "authors.html").exists():
        @app.get("/authors", response_class=HTMLResponse, tags=["html"])
        async def authors(request: Request):
            """Serve the authors page"""
            return templates.TemplateResponse("authors.html", {"request": request})
    
    if (templates_dir / "editors.html").exists():
        @app.get("/editors", response_class=HTMLResponse, tags=["html"])
        async def editors(request: Request):
            """Serve the editors page"""
            return templates.TemplateResponse("editors.html", {"request": request})
    
    if (templates_dir / "search.html").exists():
        @app.get("/search", response_class=HTMLResponse, tags=["html"])
        async def search(request: Request):
            """Serve the search page"""
            return templates.TemplateResponse("search.html", {"request": request})
    
    if (templates_dir / "view.html").exists():
        @app.get("/view", response_class=HTMLResponse, tags=["html"])
        async def view(request: Request):
            """Serve the view page"""
            return templates.TemplateResponse("view.html", {"request": request})
    
    if (templates_dir / "reader.html").exists():
        @app.get("/reader", response_class=HTMLResponse, tags=["html"])
        async def reader(request: Request):
            """Serve the reader page"""
            return templates.TemplateResponse("reader.html", {"request": request})
    
    if (templates_dir / "import.html").exists():
        @app.get("/import", response_class=HTMLResponse, tags=["html"])
        async def import_page(request: Request):
            """Serve the import page"""
            return templates.TemplateResponse("import.html", {"request": request})
