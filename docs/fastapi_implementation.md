# First1KGreek FastAPI Implementation

## Overview

This document provides comprehensive information about the FastAPI implementation for the First1KGreek browser. It explains the architecture, components, and how to use the API.

## Architecture

The First1KGreek FastAPI implementation follows a modular architecture with clear separation of concerns:

```
src/first1k/
├── __init__.py         # Package initialization
├── __main__.py         # Entry point for running as a module
├── api.py              # FastAPI application definition
├── config.py           # Configuration settings
├── models.py           # Pydantic models for data validation
├── data/               # Data access layer
├── handlers/           # Request handlers
├── routers/            # API route definitions
├── server/             # Server implementations
└── utils/              # Utility functions
```

### Key Components

1. **FastAPI Application** (`api.py`): Defines the FastAPI application, middleware, error handling, and includes the routers.

2. **Pydantic Models** (`models.py`): Defines data models for request/response validation.

3. **Routers** (`routers/`): Contains API endpoint definitions organized by functionality:
   - `authors.py`: Endpoints for author data
   - `preferences.py`: Endpoints for user preferences
   - `search.py`: Endpoints for searching the corpus
   - `view.py`: Endpoints for viewing content

4. **Data Access Layer** (`data/`): Contains functions for accessing and manipulating data:
   - `authors.py`: Functions for working with author data

5. **Handlers** (`handlers/`): Contains request handlers shared by both HTTP and FastAPI servers:
   - `api.py`: API-specific handlers
   - `browse.py`: Handlers for browsing pages
   - `search.py`: Handlers for search functionality
   - `view.py`: Handlers for viewing content

6. **Server** (`server/`): Contains server implementations:
   - `server.py`: HTTP server implementation
   - `hybrid_server.py`: Hybrid server that runs both HTTP and FastAPI servers

7. **Utilities** (`utils/`): Contains utility functions used throughout the application:
   - `path.py`: Path normalization utilities
   - `network.py`: Network-related utilities

## API Endpoints

### Authors

#### List Authors

```
GET /api/authors/
```

Lists all authors with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, default=0): Number of authors to skip
- `limit` (int, default=100): Maximum number of authors to return
- `century` (int, optional): Filter by century (negative for BCE, positive for CE)
- `type` (string, optional): Filter by author type

**Response:**
```json
[
  {
    "id": "tlg0001",
    "name": "Homer",
    "century": -8,
    "type": "Poet"
  },
  ...
]
```

#### Get Author

```
GET /api/authors/{author_id}
```

Gets details for a specific author.

**Path Parameters:**
- `author_id` (string): Author ID (e.g., 'tlg0001')

**Response:**
```json
{
  "id": "tlg0001",
  "name": "Homer",
  "century": -8,
  "type": "Poet"
}
```

#### Get Author Works

```
GET /api/authors/{author_id}/works
```

Gets works for a specific author.

**Path Parameters:**
- `author_id` (string): Author ID (e.g., 'tlg0001')

**Response:**
```json
[
  {
    "id": "tlg001",
    "title": "Iliad",
    "author_id": "tlg0001",
    "language": "grc",
    "file_path": "data/tlg0001/tlg001/tlg0001.tlg001.perseus-grc2.xml",
    "is_favorite": false,
    "is_archived": false,
    "files": [
      {
        "name": "tlg0001.tlg001.perseus-grc2.xml",
        "type": "xml",
        "path": "data/tlg0001/tlg001/tlg0001.tlg001.perseus-grc2.xml"
      }
    ]
  }
]
```

### Preferences

#### Update Work Preference

```
POST /api/preferences/work
```

Updates a preference for a specific work.

**Request Body:**
```json
{
  "author_id": "tlg0001",
  "work_id": "tlg001",
  "preference_type": "favorite",
  "value": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Preference updated successfully",
  "data": {
    "author_id": "tlg0001",
    "work_id": "tlg001",
    "preference_type": "favorite",
    "value": true
  }
}
```

#### Batch Update Preferences

```
POST /api/preferences/batch
```

Updates multiple preferences in a single request.

**Request Body:**
```json
{
  "preferences": [
    {
      "author_id": "tlg0001",
      "work_id": "tlg001",
      "preference_type": "favorite",
      "value": true
    },
    {
      "author_id": "tlg0001",
      "preference_type": "archived",
      "value": false
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Preferences updated successfully",
  "data": {
    "updated_count": 2
  }
}
```

### Search

#### Search Corpus

```
GET /api/search
```

Searches the corpus for the given query.

**Query Parameters:**
- `query` (string): Text to search for
- `authors` (list[string], optional): List of author IDs to limit search scope
- `language` (string, optional): Language filter ('grc', 'eng')
- `max_results` (int, default=100): Maximum number of results to return

**Response:**
```json
{
  "query": "virtue",
  "results": [
    {
      "author_id": "tlg0086",
      "work_id": "tlg010",
      "file_path": "data/tlg0086/tlg010/tlg0086.tlg010.perseus-eng1.xml",
      "excerpt": "...discussion of <em>virtue</em> and ethics...",
      "language": "eng"
    }
  ],
  "total_found": 1,
  "executed_in": 0.123
}
```

### View

#### View XML

```
GET /api/view/xml
```

Gets XML content for a specific file.

**Query Parameters:**
- `path` (string): Path to the XML file

**Response:**
```
HTML content with the XML file rendered for viewing
```

#### View Reader

```
GET /api/view/reader
```

Gets reader-friendly content for a specific file.

**Query Parameters:**
- `path` (string): Path to the XML file

**Response:**
```
HTML content with the XML file rendered in reader-friendly format
```

## Legacy API Endpoints

The following legacy endpoints are maintained for backward compatibility:

- `GET /get_author_works`: Gets works for an author
- `POST /update_work_preference`: Updates a work preference
- `POST /update_preferences`: Updates multiple preferences

## Server Modes

The First1KGreek browser supports three server modes:

1. **HTTP Server**: The original server using Python's built-in http.server
2. **FastAPI Server**: The new FastAPI-based server
3. **Hybrid Server**: Runs both HTTP and FastAPI servers simultaneously

### Running in Different Modes

#### HTTP Server

```
python run_server.py --mode http
```

#### FastAPI Server

```
python run_server.py --mode fastapi
```

#### Hybrid Server

```
python run_server.py --mode hybrid
```

## Development

### Adding New Endpoints

To add a new endpoint, follow these steps:

1. Define a Pydantic model in `models.py` if needed
2. Add the endpoint to the appropriate router in `routers/`
3. Implement any necessary data access functions in `data/`
4. Update the documentation

### Testing

The test suite includes tests for both HTTP and FastAPI implementations:

```
python -m pytest tests/
```

To run only FastAPI tests:

```
python -m pytest tests/api/
```

### Deployment

For production deployment, it's recommended to use a proper ASGI server like Uvicorn with multiple workers:

```
uvicorn src.first1k.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Migration from HTTP Server

If you're migrating from the HTTP server to FastAPI, keep these differences in mind:

1. **Response Format**: The HTTP server returns HTML or JSON directly, while FastAPI uses structured responses.
2. **Path Handling**: The FastAPI implementation uses absolute paths, while the HTTP server uses relative paths.
3. **API Client**: Use the API client in `static/js/api.js` for consistent access to endpoints.

## Troubleshooting

### Common Issues

1. **Path Resolution**: If you encounter path-related errors, check that the path normalization is working correctly.
2. **JSON Serialization**: If you see errors like "works.forEach is not a function", ensure proper JSON serialization.
3. **Multiprocessing**: If the hybrid server has issues, check for problems with process management. 