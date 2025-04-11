"""Integration tests for hybrid server mode in First1KGreek FastAPI implementation.

This module tests the hybrid server mode that runs both HTTP and FastAPI servers simultaneously.
"""

import pytest
import requests
import multiprocessing
import time
import os
import signal
import socket
from pathlib import Path
from unittest.mock import patch

# Import the hybrid server module
from src.first1k.server.hybrid_server import run_hybrid_server


def is_port_available(port):
    """Check if a port is available for use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("127.0.0.1", port))
        result = True
    except socket.error:
        pass
    finally:
        sock.close()
    return result


@pytest.fixture
def available_ports():
    """Find two available ports for testing."""
    port1 = 8000
    while not is_port_available(port1):
        port1 += 1
    
    port2 = port1 + 1
    while not is_port_available(port2):
        port2 += 1
    
    return port1, port2


@pytest.fixture
def hybrid_server(available_ports):
    """Start a hybrid server process for testing."""
    http_port, fastapi_port = available_ports
    
    # Ensure we're using a test preferences file
    test_prefs_path = Path("test_user_preferences.json")
    if not test_prefs_path.exists():
        with open(test_prefs_path, "w") as f:
            f.write('{"favorites": [], "archived": []}')
    
    # Start server in a separate process
    with patch("src.first1k.server.hybrid_server.PREFERENCES_FILE", str(test_prefs_path)):
        server_process = multiprocessing.Process(
            target=run_hybrid_server,
            kwargs={
                "http_port": http_port,
                "fastapi_port": fastapi_port,
                "debug": True
            }
        )
        server_process.start()
        
        # Wait for server to start
        time.sleep(2)
        
        yield (http_port, fastapi_port)  # Return both ports
        
        # Terminate server
        os.kill(server_process.pid, signal.SIGTERM)
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.terminate()
    
    # Clean up test file
    if test_prefs_path.exists():
        test_prefs_path.unlink()


def test_hybrid_server_http_endpoint(hybrid_server):
    """Test accessing an HTTP endpoint in hybrid mode."""
    http_port, _ = hybrid_server
    response = requests.get(f"http://localhost:{http_port}/")
    assert response.status_code == 200
    assert "First1KGreek" in response.text


def test_hybrid_server_fastapi_endpoint(hybrid_server):
    """Test accessing a FastAPI endpoint in hybrid mode."""
    _, fastapi_port = hybrid_server
    response = requests.get(f"http://localhost:{fastapi_port}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_hybrid_server_http_authors_endpoint(hybrid_server):
    """Test accessing the authors endpoint via HTTP server."""
    http_port, _ = hybrid_server
    response = requests.get(f"http://localhost:{http_port}/browse_authors")
    assert response.status_code == 200
    assert "Authors" in response.text


def test_hybrid_server_fastapi_authors_endpoint(hybrid_server):
    """Test accessing the authors endpoint via FastAPI server."""
    _, fastapi_port = hybrid_server
    response = requests.get(f"http://localhost:{fastapi_port}/api/authors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_hybrid_server_api_integration(hybrid_server):
    """Test that both servers can access the same data sources."""
    http_port, fastapi_port = hybrid_server
    
    # Get authors from FastAPI
    fastapi_response = requests.get(f"http://localhost:{fastapi_port}/api/authors")
    assert fastapi_response.status_code == 200
    fastapi_authors = fastapi_response.json()
    
    # There should be at least one author
    assert len(fastapi_authors) > 0
    
    # HTTP server's browse authors page should contain same author names
    http_response = requests.get(f"http://localhost:{http_port}/browse_authors")
    assert http_response.status_code == 200
    
    # At least one author name from FastAPI should be in HTTP response
    author_name = fastapi_authors[0]["name"]
    assert author_name in http_response.text 