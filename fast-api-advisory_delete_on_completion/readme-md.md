# First1KGreek FastAPI Implementation

This project implements a FastAPI backend for the First1KGreek Browser application, replacing the original HTTP server with a modern, high-performance API server.

## Features

- RESTful API for browsing ancient Greek texts
- Automatic API documentation with Swagger/OpenAPI
- Type validation with Pydantic models
- Asynchronous request handling
- Dependency injection
- Middleware for logging and CORS
- Static file serving

## Directory Structure

```
first1kgreek/
├── src/
│   └── first1k/
│       ├── __init__.py
│       ├── __main__.py
│       ├── api.py           # FastAPI application
│       ├── config.py        # Configuration settings
│       ├── dependencies.py  # FastAPI dependencies
│       ├── middleware.py    # Custom middleware
│       ├── models.py        # Pydantic models
│       ├── static_files.py  # Static file handling
│       ├── handlers/        # Request handlers
│       │   ├── __init__.py
│       │   ├── api.py       # API handlers
│       │   └── ...
│       └── routers/         # FastAPI routes
│           ├── __init__.py
│           ├── authors.py
│           ├── preferences.py
│           ├── search.py
│           └── view.py
├── static/                  # Static files (CSS, JS)
│   ├── css/
│   ├── js/
│   │   └── api-client.js    # JavaScript API client
├── templates/               # HTML templates (optional)
├── tests/                   # Tests
│   ├── api/
│   │   └── test_api.py
│   └── conftest.py
├── .gitignore
├── hybrid_server.py         # Script to run both servers during transition
├── pyproject.toml           # Package configuration
├── README.md
├── requirements.txt
└── run_server.py            # Script to run the FastAPI server
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/first1kgreek.git
cd first1kgreek
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

### FastAPI Server Only

```bash
python run_server.py
```

Options:
- `--port PORT`: Port to run the server on (default: 8000)
- `--host HOST`: Host to bind to (default: localhost)
- `--debug`: Enable debug mode with verbose logging
- `--no-browser`: Don't open a browser automatically

### Hybrid Mode (During Transition)

```bash
python hybrid_server.py
```

Options:
- `--http-port PORT`: Port for the HTTP server (default: 8000)
- `--api-port PORT`: Port for the FastAPI server (default: 8001)
- `--api-only`: Run only the FastAPI server
- `--http-only`: Run only the HTTP server
- Other options same as above

## API Endpoints

### Authors

- `GET /api/authors`: List authors with filtering
- `GET /api/authors/{author_id}`: Get author details
- `GET /api/authors/{author_id}/works`: Get works for an author

### Preferences

- `GET /api/preferences`: Get user preferences
- `POST /api/preferences/work`: Update work preference
- `POST /api/preferences/batch`: Bulk update preferences

### Search

- `GET /api/search?q={query}`: Search texts

### View

- `GET /api/view/xml?path={path}`: Get XML content
- `GET /api/view/reader?path={path}`: Get reader-friendly content

### Health and Info

- `GET /api/health`: Check API health
- `GET /api/info`: Get API information

## Documentation

API documentation is available at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Testing

Run tests with pytest:

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=src/first1k
```

## Frontend Integration

The JavaScript API client is available at `/static/js/api-client.js`. Include it in your HTML files:

```html
<script src="/static/js/api-client.js"></script>
<script>
  // Use the API client
  window.apiClient.getAuthors()
    .then(authors => {
      console.log(authors);
    });
</script>
```

## Development

1. Install development dependencies:

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

2. Run the server in debug mode:

```bash
python run_server.py --debug
```

## License

MIT
