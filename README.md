[![DOI](https://zenodo.org/badge/56595003.svg)](https://zenodo.org/badge/latestdoi/56595003)
[![Hook Coverage](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/coverage.svg)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![Hook Texts](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/texts.svg)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![Hook Metadata](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/metadata.svg)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![Total words](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/words.svg)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![Greek Words](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/words.svg?lang=grc)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![Latin Words](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/words.svg?lang=lat)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![English Words](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/words.svg?lang=eng)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)
[![German Words](https://ci.perseids.org/api/hook/v2.0/badges/OpenGreekAndLatin/First1KGreek/words.svg?lang=deu)](https://ci.perseids.org/repo/OpenGreekAndLatin/First1KGreek)

# First1KGreek Browser

A tool for browsing Greek texts from the First Thousand Years Project.

## Features

- Browse texts by author or editor
- Search through the corpus
- Import texts from Scaife/Perseus
- Dark theme for comfortable reading
- XML and reader views
- Support for fragments and editions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/First1KGreek.git
cd First1KGreek
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
venv\Scripts\activate  # On Windows
```

3. Install the package:
```bash
pip install -e .
```

## Usage

Run the browser:
```bash
first1k
```

This will start the server and open your default web browser to the application.

## Project Structure

```
src/first1k/
├── __init__.py
├── __main__.py
├── config.py
├── server/
│   ├── __init__.py
│   └── server.py
├── handlers/
│   └── __init__.py
├── xml_utils/
│   ├── __init__.py
│   └── processor.py
├── import_export/
│   ├── __init__.py
│   └── scaife.py
├── editor/
│   ├── __init__.py
│   └── manager.py
├── search/
│   ├── __init__.py
│   └── searcher.py
└── utils/
    ├── __init__.py
    └── network.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
