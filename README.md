[![DOI](https://zenodo.org/badge/56595003.svg)](https://zenodo.org/badge/latestdoi/56595003)

# First1KGreek Browser

A specialized tool for browsing, searching, and analyzing ancient Greek texts from the First Thousand Years of Greek project.

## Features

- Browser-based interface for ancient Greek texts
- Searchable author and work listings
- XML and reader views for texts
- Dark theme for comfortable reading
- User preferences (favorites, archived, deleted)
- Dark theme UI for better readability

## FastAPI Migration

The First1KGreek Browser has been migrated to use FastAPI for improved API performance, documentation, and type validation. The migration follows a phased approach to maintain backward compatibility during the transition period.

### New Features

- **Modern API**: Built with FastAPI, providing automatic documentation, request validation, and better performance.
- **API Documentation**: Available at `/docs` for interactive API exploration.
- **Multiple Server Modes**: Choose between FastAPI, traditional HTTP, or hybrid mode during transition.
- **JavaScript API Client**: Easy-to-use client-side functions for interacting with the API.

### Running the Server

The server can be run in three different modes:

#### FastAPI Mode (Recommended)

```bash
python run_server.py --mode fastapi
```

#### HTTP Mode (Legacy)

```bash
python run_server.py --mode http
```

#### Hybrid Mode (Transition)

```bash
python run_server.py --mode hybrid
```

### Command-line Options

```
--host HOST           Host to bind the server to (default: localhost)
--port PORT           Port to bind the server to (default: 8000)
--mode {fastapi,http,hybrid}
                      Server mode to run (default: fastapi)
--debug               Enable debug mode
--reload              Enable auto-reload for FastAPI (only in fastapi or hybrid mode)
--no-browser          Don't open browser automatically
--version             Show version information and exit
```

### JavaScript API Client

The JavaScript API client is available at `/static/js/api.js` and provides easy-to-use functions for interacting with the API:

```javascript
// Example: Get all authors
First1KAPI.getAuthors()
  .then(authors => {
    console.log('Authors:', authors);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### API Adapters

During the transition period, adapter functions are available at `/static/js/api-adapters.js` to maintain backward compatibility:

```javascript
// Legacy-compatible function
First1KAdapters.loadAuthorWorks('tlg0001', function(data) {
  console.log('Author works:', data);
});
```

## Original Documentation

[Original documentation content goes here]

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/First1KGreek.git
cd First1KGreek

# Install dependencies
pip install -r requirements.txt

# Run the server
python run_server.py
```

## Usage

```bash
# Run with default settings
python run_server.py

# Run on a specific port
python run_server.py --port 8080

# Run with debug mode
python run_server.py --debug
```

You can also run as a module:

```bash
python -m src.first1k
```

## Performance Testing

The application includes performance tests:

```bash
python tests/run_tests.py --performance
```

This tests various aspects of the application including:
- HTTP server response times
- XML processing performance
- Search functionality speed

## Project Structure

The application uses a modular architecture:

```
src/first1k/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point when run as a module
├── config.py             # Configuration settings
├── api.py                # FastAPI implementation
├── models.py             # Pydantic models for API
├── handlers/             # Request handlers for different routes
├── server/               # HTTP server implementation
├── routers/              # FastAPI router modules
├── data/                 # Data access modules
├── utils/                # Utility functions
├── xml_utils/            # XML processing utilities
├── search/               # Search functionality
├── import_export/        # Import/export functionality
└── editor/               # Editor management
```

## Development

For development work:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python run_pytest.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The First Thousand Years of Greek Project
- Canonical-GreekLit repository for source data

## Documentation

- For detailed usage instructions, see [USAGE.md](USAGE.md)
- For project comparison information, see [COMPARISON.md](COMPARISON.md)
- For user help documentation, see [First1K_User_Help.txt](First1K_User_Help.txt)