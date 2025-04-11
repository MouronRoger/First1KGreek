"""Pytest configuration for First1KGreek."""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Make sure the package root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_author():
    """Return a sample author dictionary."""
    return {
        "id": "tlg0007",
        "name": "Plutarch",
        "century": 1,
        "type": "Biographer",
        "works_count": 3,
        "is_favorite": False,
        "is_archived": False
    }

@pytest.fixture
def sample_works():
    """Return a list of sample works."""
    return [
        {
            "id": "tlg0007.tlg136.perseus-grc2",
            "title": "De Stoicorum Repugnantiis",
            "language": "Greek",
            "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
            "is_favorite": False,
            "is_archived": False
        },
        {
            "id": "tlg0007.tlg137.perseus-grc2",
            "title": "De Communibus Notitiis Adversus Stoicos",
            "language": "Greek",
            "file_path": "data/tlg0007/tlg137/tlg0007.tlg137.perseus-grc2.xml",
            "is_favorite": False,
            "is_archived": False
        }
    ]

@pytest.fixture
def sample_preferences():
    """Return a sample user preferences dictionary."""
    return {
        "favorites": ["tlg0007.tlg136.perseus-grc2"],
        "archived": ["tlg0012.tlg001.perseus-grc2"]
    }

@pytest.fixture
def sample_search_results():
    """Return a list of sample search results."""
    return [
        {
            "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml",
            "author": "Plutarch",
            "title": "De Stoicorum Repugnantiis",
            "editor": "Unknown",
            "context": "Sample search context",
            "occurrence_count": 5
        }
    ]

@pytest.fixture
def sample_xml_content():
    """Return a sample XML content dictionary."""
    return {
        "content": "<xml>Test content</xml>",
        "author": "Plutarch",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    }

@pytest.fixture
def sample_reader_content():
    """Return a sample reader content dictionary."""
    return {
        "content": "Test content without XML tags",
        "author": "Plutarch",
        "title": "De Stoicorum Repugnantiis",
        "language": "Greek",
        "file_path": "data/tlg0007/tlg136/tlg0007.tlg136.perseus-grc2.xml"
    }

@pytest.fixture
def mock_authors_file(tmp_path):
    """Create a temporary authors data file."""
    authors_data = {
        "tlg0007": {
            "name": "Plutarch",
            "century": 1,
            "type": "Biographer"
        },
        "tlg0012": {
            "name": "Homer",
            "century": -8,
            "type": "Poet"
        }
    }
    
    file_path = tmp_path / "authors_data.json"
    with open(file_path, "w") as f:
        json.dump(authors_data, f)
    
    return file_path

@pytest.fixture
def mock_user_prefs_file(tmp_path):
    """Create a temporary user preferences file."""
    prefs_data = {
        "favorites": ["tlg0007.tlg136.perseus-grc2"],
        "archived": ["tlg0012.tlg001.perseus-grc2"]
    }
    
    file_path = tmp_path / "user_preferences.json"
    with open(file_path, "w") as f:
        json.dump(prefs_data, f)
    
    return file_path

@pytest.fixture
def mock_file_system(tmp_path):
    """Create a mock file system structure."""
    # Create author directory
    author_dir = tmp_path / "data" / "tlg0007"
    author_dir.mkdir(parents=True)
    
    # Create author metadata
    with open(author_dir / "__cts__.xml", "w") as f:
        f.write("""<ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:greekLit:tlg0007">
    <ti:groupname xml:lang="eng">Plutarch</ti:groupname>
</ti:textgroup>""")
    
    # Create work directory
    work_dir = author_dir / "tlg136"
    work_dir.mkdir()
    
    # Create work metadata
    with open(work_dir / "__cts__.xml", "w") as f:
        f.write("""<ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" groupUrn="urn:cts:greekLit:tlg0007" xml:lang="grc" urn="urn:cts:greekLit:tlg0007.tlg136">
    <ti:title xml:lang="eng">De Stoicorum Repugnantiis</ti:title>
    <ti:edition urn="urn:cts:greekLit:tlg0007.tlg136.perseus-grc2" workUrn="urn:cts:greekLit:tlg0007.tlg136" xml:lang="grc">
        <ti:label xml:lang="eng">De Stoicorum Repugnantiis</ti:label>
        <ti:description xml:lang="eng">Perseus edition</ti:description>
    </ti:edition>
</ti:work>""")
    
    # Create work file
    with open(work_dir / "tlg0007.tlg136.perseus-grc2.xml", "w") as f:
        f.write("""<TEI>
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>De Stoicorum Repugnantiis</title>
                <author>Plutarch</author>
                <editor>Unknown</editor>
            </titleStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <div type="textpart" subtype="section" n="1">
                <p>Test content</p>
            </div>
        </body>
    </text>
</TEI>""")
    
    return tmp_path

@pytest.fixture
def patch_file_access(monkeypatch, mock_file_system, mock_authors_file, mock_user_prefs_file):
    """Patch file access functions to use temporary files."""
    # Patch Path.exists() to check temporary paths
    original_exists = Path.exists
    
    def patched_exists(self):
        if self.name == "authors_data.json":
            return True
        if self.name == "user_preferences.json":
            return True
        if str(self).startswith(str(mock_file_system)):
            return os.path.exists(self)
        return original_exists(self)
    
    monkeypatch.setattr(Path, "exists", patched_exists)
    
    # Patch open() to use temporary files
    original_open = open
    
    def patched_open(file, *args, **kwargs):
        if file == "authors_data.json" or str(file) == "authors_data.json":
            return original_open(mock_authors_file, *args, **kwargs)
        if file == "user_preferences.json" or str(file) == "user_preferences.json":
            return original_open(mock_user_prefs_file, *args, **kwargs)
        if isinstance(file, str) and file.startswith("data/"):
            # Map data path to the temporary directory
            rel_path = file.split("data/")[1]
            new_path = os.path.join(mock_file_system, "data", rel_path)
            return original_open(new_path, *args, **kwargs)
        return original_open(file, *args, **kwargs)
    
    monkeypatch.setattr("builtins.open", patched_open)
    
    # Patch os.path.exists() to check temporary paths
    original_os_path_exists = os.path.exists
    
    def patched_os_path_exists(path):
        if path == "authors_data.json":
            return True
        if path == "user_preferences.json":
            return True
        if isinstance(path, str) and path.startswith("data/"):
            # Map data path to the temporary directory
            rel_path = path.split("data/")[1]
            new_path = os.path.join(mock_file_system, "data", rel_path)
            return original_os_path_exists(new_path)
        return original_os_path_exists(path)
    
    monkeypatch.setattr(os.path, "exists", patched_os_path_exists)
    
    # Return a function to reset the patches if needed
    return lambda: monkeypatch.undo()
