[![DOI](https://zenodo.org/badge/56595003.svg)](https://zenodo.org/badge/latestdoi/56595003)

# First1KGreek Browser

A specialized tool for browsing, searching, and analyzing ancient Greek texts combining data from both the First Thousand Years Project and Canonical-GreekLit repositories. This hybrid collection provides a comprehensive corpus of ancient Greek texts through a lightweight, standalone web interface, making classical texts accessible without requiring specialized software or cloud dependencies.

## Overview

The First1KGreek Browser is designed for classical scholars, researchers, and students studying ancient Greek texts. This hybrid version combines:

- Texts from the First Thousand Years Project (First1K)
- Works from the Canonical-GreekLit repository
- Integrated metadata and cross-references between collections

The browser provides:
- Local web-based access to a comprehensive corpus of ancient Greek texts
- Simple, intuitive navigation through authors and works
- XML and reader views with proper Greek text rendering
- Dark theme for comfortable extended reading sessions
- Import capabilities for texts from Scaife/Perseus
- Unified metadata management for authors, editors, and works across both collections

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)
- Sufficient disk space for text corpus (both First1K and Canonical-GreekLit collections)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/OpenGreekAndLatin/First1KGreek.git
cd First1KGreek
```

2. No additional installation steps required - the application runs using Python's standard library.

## Usage

1. Start the server from the project directory:
```bash
python browse_texts_fixed.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

The interface provides:
- Author/Editor browsing across both collections
- Full-text search capabilities in the combined corpus
- XML source viewing
- Reader mode with customizable display
- Text import functionality from Scaife/Perseus
- Integrated navigation between First1K and Canonical-GreekLit texts

## Project Structure

```
First1KGreek/
├── browse_texts_fixed.py     # Main application server
├── src/                      # Source code directory
├── data/                     # Combined text corpus storage
├── raw_files/               # Original source files from both collections
├── greek-texts-index/       # Unified text indexing information
└── requirements.txt         # (Empty - no external dependencies)
```

## Features

### Core Functionality
- Browse texts by author or editor across both collections
- Search through the entire combined corpus
- View texts in XML format or reader mode
- Import new texts from Scaife/Perseus
- Dark theme for comfortable reading
- Unified metadata management and display
- Cross-references between First1K and Canonical-GreekLit texts

### Text Processing
- TEI XML parsing and rendering
- Proper Greek text display
- Metadata extraction and management
- Import workflow with validation
- Unified handling of both collections' XML formats

## Contributing

This is an open-source project maintained by the Open Greek and Latin Project. Contributions are welcome:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [license.md](license.md) file for details.

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgments and contributors.

## Documentation

- For detailed usage instructions, see [USAGE.md](USAGE.md)
- For project comparison information, see [COMPARISON.md](COMPARISON.md)
- For user help documentation, see [First1K_User_Help.txt](First1K_User_Help.txt)
