# FastAPI Migration Guide for First1KGreek

This document provides detailed instructions for migrating the First1KGreek browser from its current implementation using Python's standard library HTTP server to FastAPI.

## Prerequisites

Before starting the migration, make sure you have:

1. A working understanding of the current codebase
2. Python 3.8+ installed
3. Git repository cloned and up to date
4. Virtual environment set up for development

## Step 1: Set Up Project Dependencies

1. Create a `requirements.txt` file with the necessary packages:

```
fastapi>=0.95.1
uvicorn>=0.22.0
pydantic>=2.0.0
```

2. Install the dependencies in your virtual environment:

```bash
pip install -r requirements.txt
```

## Step 2: Implement the FastAPI Application Structure

1. Create or modify the following files:

- `src/first1k/models.py` - Pydantic models for API
- `src/first1k/api.py` - FastAPI application
- `src/first1k/routers/` - Directory for route modules
- `src/first1k/middleware.py` - Custom middleware
- `src/first1k/dependencies.py` - FastAPI dependencies

2. Update `src/first1k/config.py` to ensure it provides the necessary configuration values for the FastAPI application.

## Step 3: Implement Core API Endpoints

Migrate the following endpoints from the existing HTTP server:

1. Authors API:
   - GET /api/authors - List authors with filtering
   - GET /api/authors/{author_id} - Get author details
   - GET /api/authors/{author_id}/works - Get works for an author

2. Preferences API:
   - POST /api/preferences/work - Update work preference
   - POST /api/preferences/batch - Bulk update preferences

3. Search API:
   - GET /api/search - Search texts

4. View API:
   - GET /api/view/xml - Get XML content
   - GET /api/view/reader - Get reader-friendly content

## Step 4: Create Hybrid Server Mode

During the transition, run both servers simultaneously:

1. Create a new run script that starts the FastAPI server on a different port than the original server.
2. Update JavaScript files to check both servers for compatibility.
3. Add fallback mechanisms in the JavaScript client.

## Step 5: Test API Endpoints

1. Create unit tests for each API endpoint using `pytest` and FastAPI's test client:

```python
from fastapi.testclient import TestClient
from src.first1k.api import app

client = TestClient(app)

def test_get_authors():
    response = client.get("/api/authors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

2. Run tests to ensure all endpoints work correctly:

```bash
pytest tests/api/
```

## Step 6: Migrate Frontend to Use API

1. Create a JavaScript API client:

```javascript
// In static/js/api-client.js
const API_BASE_URL = '/api';

async function getAuthors(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/authors?${queryString}`);
  if (!response.ok) throw new Error('Failed to fetch authors');
  return response.json();
}

// Export as global object
window.apiClient = {
  getAuthors,
  // Add other functions here
};
```

2. Update HTML templates to use the API client.

## Step 7: Add Static File Serving

For FastAPI to serve static files (CSS, JavaScript, etc.):

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Step 8: Implement HTML Templates

1. Install Jinja2 for template rendering:

```bash
pip install jinja2
```

2. Set up template rendering:

```python
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

3. Move HTML from Python strings to actual template files.

## Step 9: Complete the Migration

1. Update `run_server.py` to use only the FastAPI server:

```python
import uvicorn
from src.first1k import config

def main():
    uvicorn.run(
        "src.first1k.api:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )

if __name__ == "__main__":
    main()
```

2. Run final tests to ensure everything works correctly.

3. Update documentation to reflect the new API and server implementation.

## Step 10: Advanced Features (Optional)

After the basic migration is complete, consider implementing:

1. Authentication and authorization for admin functions
2. Rate limiting for API endpoints
3. Caching for frequently accessed data
4. Background tasks for long-running operations
5. API versioning for future compatibility
