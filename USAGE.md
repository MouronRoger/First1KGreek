# First 1K Greek Project - Usage Guide

This guide will help you navigate and use the First 1K Greek Project repository to access ancient Greek and Latin texts.

## Overview

The First 1K Greek Project by Open Greek and Latin (OGL) contains digital versions of Greek texts from the first thousand years of Greek literature. The texts are encoded in TEI XML format, providing structured, machine-readable versions of these ancient texts.

## Repository Structure

- `data/`: Contains the processed, formatted XML texts organized by author and work
- `raw_files/`: Contains original, unprocessed text files
- `volume_xml/`: Contains complete volumes or works in XML format
- `split/` and `save/`: Folders for processing intermediate files
- `src/first1k/`: Contains the modular implementation of the browser application

## Using the Text Browser

We've created a web-based browser to help you navigate the texts easily.

### Running the Browser

There are multiple ways to run the First1KGreek Browser:

#### Option 1: Using run_server.py (Recommended)

1. Make sure you have Python 3.6+ installed on your system
2. Open a terminal/command prompt
3. Navigate to the repository directory:
   ```
   cd /path/to/First1KGreek
   ```
4. Run the server script:
   ```
   python run_server.py
   ```
5. Your web browser should automatically open to `http://localhost:8000/`

Additional options:
```bash
python run_server.py --port 8080 --debug --host 0.0.0.0 --no-browser
```

#### Option 2: Using the Python Module

Run as a Python module:
```bash
python -m src.first1k
```

#### Option 3: Using the Package Entry Point (if installed)

If you've installed the package:
```bash
pip install -e .
first1k
```

### Browser Features

The browser provides several ways to access the texts:

- **Browse Authors**: View texts organized by author, century, and type
- **Browse Works**: See all works by a particular author
- **Search Texts**: Search across the corpus
- **User Preferences**: Mark authors as favorites or archived
- **Dark Theme**: Toggle between light and dark themes for better readability

### Viewing Texts

When viewing a text, you can see:

- The XML content in a formatted, readable view
- Raw XML for technical inspection
- Metadata about the text (author, title, edition information)
- The primary text in Greek or Latin
- Critical apparatus (variant readings and editorial notes)
- Commentary and notes
- References to parallel passages

## Command-line Tools

The repository also includes several command-line tools:

- `pages.sh`: Generate GitHub Pages for the project
- `pnumber.xsl`: XSLT transformation for processing XML
- `lint_advisory.py`: Tool for checking code quality

## Text Structure

Each text follows a standard structure:

1. Each author has a unique identifier (e.g., `tlg2042` for Origen)
2. Each work has a work identifier (e.g., `tlg001` for "Contra Celsum")
3. Each text might have multiple editions (e.g., `perseus-grc1` for a specific Greek edition)

## Text Identification

The texts use Canonical Text Services (CTS) URNs for identification:

- `urn:cts:greekLit:tlg2042.tlg001.perseus-grc1`
  - `greekLit`: The text collection
  - `tlg2042`: The author ID (Origen)
  - `tlg001`: The work ID (Contra Celsum)
  - `perseus-grc1`: The specific edition

## Contributing

For information on contributing to the project, please refer to the original project repository at [OpenGreekAndLatin/First1KGreek](https://github.com/OpenGreekAndLatin/First1KGreek).

## License

The texts in this repository are available under a Creative Commons Attribution-ShareAlike 4.0 International License, as indicated in the XML files. 