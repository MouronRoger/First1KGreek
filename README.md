[![DOI](https://zenodo.org/badge/56595003.svg)](https://zenodo.org/badge/latestdoi/56595003)

# First1KGreek Browser

A specialized tool for browsing, searching, and analyzing ancient Greek texts from the First Thousand Years of Greek project.

## Features

- Browse authors by name, century, and type
- View works by author
- Read texts in both readable and raw XML formats
- Search functionality across the corpus
- User preferences (favorites, archived, deleted)
- Dark theme UI for better readability

## Installation

### Prerequisites

- Python 3.6 or higher

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/First1KGreek.git
   cd First1KGreek
   ```

2. Install dependencies (minimal, uses standard library):
   ```
   pip install -e .
   ```

## Usage

There are multiple ways to run the First1KGreek Browser:

### 1. Using the run_server.py script (recommended)

This is the simplest way to run the application:

```bash
python run_server.py
```

Options:
- `--port PORT`: Specify the port to run on (default: 8000)
- `--debug`: Enable debug mode with verbose logging
- `--version`: Show version information and exit
- `--no-browser`: Don't automatically open a browser window
- `--host HOST`: Host to bind to (use 0.0.0.0 for network access)

Example:
```bash
python run_server.py --port 8080 --debug
```

### 2. Using the modular package directly

Run as a Python module:

```bash
python -m src.first1k
```

Options are the same as above.

### 3. Using the package entry point (if installed)

If you've installed the package, you can use:

```bash
first1k
```

## Performance Testing

To run performance tests:

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
├── handlers/             # Request handlers for different routes
├── server/               # HTTP server implementation
├── utils/                # Utility functions
├── xml_utils/            # XML processing utilities
├── search/               # Search functionality
├── import_export/        # Import/export functionality
└── editor/               # Editor management
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
