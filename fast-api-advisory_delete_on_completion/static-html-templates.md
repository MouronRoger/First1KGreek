# Frontend Integration Strategy

This document outlines the strategy for integrating the FastAPI backend with the existing frontend in the First1KGreek project.

## Phase 1: Hybrid Mode API Client

During the transition phase, we'll maintain both servers while gradually moving functionality to the FastAPI server. This requires a JavaScript API client that can communicate with the new endpoints.

### API Client Implementation

Create a file `static/js/api-client.js` with the following structure:

```javascript
/**
 * First1KGreek API Client
 * Provides JavaScript functions for interacting with the FastAPI backend
 */

// API base URL (configurable to point to FastAPI or original server)
const API_BASE_URL = '/api';

// Fetch options for all requests
const DEFAULT_FETCH_OPTIONS = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

/**
 * Get a list of authors with optional filtering
 * 
 * @param {Object} options - Query parameters
 * @param {string} options.search - Search term for filtering authors
 * @param {number} options.century - Century for filtering authors
 * @param {string} options.type - Author type for filtering
 * @param {number} options.page - Page number (starts from 1)
 * @param {number} options.limit - Number of items per page
 * @returns {Promise<Array>} - List of authors
 */
async function getAuthors({ search, century, type, page = 1, limit = 25 } = {}) {
  // Build query string
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (century) params.append('century', century);
  if (type) params.append('type', type);
  params.append('page', page);
  params.append('limit', limit);

  // Make request
  const response = await fetch(`${API_BASE_URL}/authors?${params.toString()}`, {
    ...DEFAULT_FETCH_OPTIONS,
    method: 'GET'
  });

  // Handle response
  if (!response.ok) {
    throw new Error(`Error fetching authors: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get works for a specific author
 * 
 * @param {string} authorId - The author ID
 * @returns {Promise<Array>} - List of works
 */
async function getAuthorWorks(authorId) {
  // Make request
  const response = await fetch(`${API_BASE_URL}/authors/${authorId}/works`, {
    ...DEFAULT_FETCH_OPTIONS,
    method: 'GET'
  });

  // Handle response
  if (!response.ok) {
    throw new Error(`Error fetching works: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Update preference for a specific work
 * 
 * @param {Object} data - Preference update data
 * @param {string} data.workId - The work ID
 * @param {string} data.type - Preference type ('favorite', 'archive', or 'delete')
 * @param {string} data.action - Action to perform ('add' or 'remove')
 * @returns {Promise<Object>} - Result of the operation
 */
async function updateWorkPreference(data) {
  // Make request
  const response = await fetch(`${API_BASE_URL}/preferences/work`, {
    ...DEFAULT_FETCH_OPTIONS,
    method: 'POST',
    body: JSON.stringify({
      work_id: data.workId,
      type: data.type,
      action: data.action
    })
  });

  // Handle response
  if (!response.ok) {
    throw new Error(`Error updating preference: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Search texts for a specific term
 * 
 * @param {string} query - Search term
 * @returns {Promise<Object>} - Search results
 */
async function searchTexts(query) {
  // Make request
  const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`, {
    ...DEFAULT_FETCH_OPTIONS,
    method: 'GET'
  });

  // Handle response
  if (!response.ok) {
    throw new Error(`Error searching texts: ${response.statusText}`);
  }

  return response.json();
}

// Export functions for use in other files
window.apiClient = {
  getAuthors,
  getAuthorWorks,
  updateWorkPreference,
  searchTexts
};
```

## Phase 2: HTML Template Updates

Update the HTML templates to use the API client. Here's an example for the authors table:

```html
<!-- Before: Inline script making direct fetch calls -->
<script>
function fetchAuthorWorks(authorId) {
  fetch(`/get_author_works?author_id=${authorId}`)
    .then(response => response.json())
    .then(data => renderWorks(authorId, data))
    .catch(error => console.error('Error fetching works:', error));
}
</script>

<!-- After: Using the API client -->
<script src="/static/js/api-client.js"></script>
<script>
function fetchAuthorWorks(authorId) {
  window.apiClient.getAuthorWorks(authorId)
    .then(data => renderWorks(authorId, data))
    .catch(error => console.error('Error fetching works:', error));
}
</script>
```

## Phase 3: Complete Frontend Integration

Once all API endpoints are working correctly with the frontend, you can update `run_server.py` to only start the FastAPI server. At this point, all frontend files should be served by FastAPI using `StaticFiles` middleware:

```python
from fastapi.staticfiles import StaticFiles

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
```

## HTML Templates for FastAPI

For FastAPI to serve HTML pages instead of just JSON, you'll need to add Jinja2Templates support:

```python
from fastapi.templating import Jinja2Templates
from fastapi import Request

# Set up templates
templates = Jinja2Templates(directory="templates")

# Add HTML routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

This requires moving HTML from Python strings to actual template files. For a smoother transition, consider creating a separate module that handles HTML template rendering first, then gradually migrating to Jinja2 templates.
