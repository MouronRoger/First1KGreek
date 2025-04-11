# FastAPI Testing Strategy for First1KGreek

## Overview

This document outlines the strategy for updating the existing test suite to work with the new modular architecture using FastAPI. The goal is to ensure comprehensive test coverage for both the HTTP server and FastAPI implementations, as well as the hybrid mode.

## Key Changes Required

### 1. Update Import Paths

The tests currently import from `browse_texts_fixed.py`, but should be updated to import from the new module structure:

```python
# Old
from browse_texts_fixed import CustomHTTPRequestHandler, AUTHORS_DATA

# New
from src.first1k.server.server import CustomHTTPRequestHandler
from src.first1k.data.authors import AUTHORS_DATA
```

### 2. Mock Setup Updates

The mock setup should be updated to match the new class structure:

```python
# Old
handler = mock.MagicMock(spec=browse_texts_fixed.CustomHTTPRequestHandler)

# New
handler = mock.MagicMock(spec=server.CustomHTTPRequestHandler)
# Add page_generator attribute, which is now a separate component
handler.page_generator = mock.MagicMock(spec=browse.PageGenerator)
```

### 3. API Response Format

Tests should be updated to match the new API response format:

```python
# Old
response = handler.do_GET()

# New
# For HTTP Handler
status_code, content_type, response_data = handler.do_GET()

# For FastAPI endpoints
client = TestClient(app)
response = client.get("/api/authors")
assert response.status_code == 200
```

## New Tests for FastAPI

### 1. API Endpoint Tests

Create tests for all FastAPI endpoints using FastAPI's TestClient:

```python
from fastapi.testclient import TestClient
from src.first1k.api import app

client = TestClient(app)

def test_list_authors():
    response = client.get("/api/authors")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

### 2. Pydantic Model Tests

Add tests for Pydantic model validation:

```python
from src.first1k.models import Author

def test_author_model():
    author = Author(id="tlg0001", name="Test Author", century=1, type="Historian")
    assert author.id == "tlg0001"
    assert author.name == "Test Author"
    assert author.century == 1
    assert author.type == "Historian"
```

### 3. Hybrid Server Tests

Create integration tests for hybrid server mode:

```python
import requests
import multiprocessing
import time
from src.first1k.server.hybrid_server import HybridServer

def test_hybrid_server():
    server = HybridServer(
        http_port=8080,
        fastapi_port=8081
    )
    
    # Start server in a separate process
    process = multiprocessing.Process(target=server.start)
    process.start()
    time.sleep(1)  # Allow time for server to start
    
    # Test HTTP server
    http_response = requests.get("http://localhost:8080/browse/authors")
    assert http_response.status_code == 200
    
    # Test FastAPI server
    api_response = requests.get("http://localhost:8081/api/authors")
    assert api_response.status_code == 200
    
    # Cleanup
    server.stop()
    process.join(timeout=5)
```

## Implementation Plan

1. Update `test_base.py` to work with the new module structure
2. Update `test_http_handler.py` to use the new handler methods
3. Fix `test_page_generation.py` to use the modular components
4. Add FastAPI-specific tests:
   - API endpoint tests
   - Pydantic model tests
   - Hybrid server tests
5. Extend the test suite with broader coverage

## Handling Multiprocessing Issues

For hybrid server tests, we need to address the multiprocessing issues:

1. Use a more stable approach to process management
2. Implement proper cleanup of processes
3. Use threading instead of multiprocessing for simpler scenarios
4. Consider using contextlib for resource management
5. Implement timeouts to prevent hanging tests

## Test Fixtures

Update or create fixtures for FastAPI testing:

```python
@pytest.fixture
def fastapi_client():
    return TestClient(app)

@pytest.fixture
def test_data():
    # Create test data
    yield test_data
    # Clean up test data
```

## Continuous Integration

Ensure that all tests run in CI:

1. Set up GitHub Actions workflow for running tests
2. Add test coverage reporting
3. Configure testing for different server modes (HTTP, FastAPI, hybrid)
4. Implement parallel test execution for faster feedback 