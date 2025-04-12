# First1KGreek Browser Implementation Plan

## Phase 1: Create Index Structure

1. **Design the JSON Index Schema**
   ```json
   {
     "authors": {
       "tlg0032": {
         "name": "Xenophon", 
         "century": 4,
         "type": "Historian",
         "works": {
           "tlg008": {
             "titles": {
               "latin": "Hiero",
               "english": "Hiero"
             },
             "texts": [
               {
                 "id": "tlg0032.tlg008.perseus-grc2",
                 "language": "Greek",
                 "path": "data/tlg0032/tlg008/tlg0032.tlg008.perseus-grc2.xml"
               },
               {
                 "id": "tlg0032.tlg008.perseus-eng2",
                 "language": "English",
                 "path": "data/tlg0032/tlg008/tlg0032.tlg008.perseus-eng2.xml"
               }
             ]
           }
         }
       }
     }
   }
   ```

2. **Create Indexer Module (src/first1k/indexer/)**
   - **models.py**: Pydantic models for authors, works, and text versions
   - **builder.py**: Index construction functions that scan data directory and XML files
   - **accessor.py**: Cached index access functions with performance optimizations
   - **__init__.py**: Package exports with clear API for index functions

3. **Add Utility Functions**
   - **src/first1k/utils/file_utils.py**: Change detection in data files for reindexing
   - **src/first1k/utils/index_utils.py**: Index management and validation

4. **Implement Hybrid Reindexing**
   - Manual trigger with confirmation prompt
   - Notification system for detected file changes
   - Optional automatic mode configurable in settings

5. **Update Configuration**
   - Update **src/first1k/config.py** with index file paths and reindexing settings

## Phase 2: Create FastAPI Endpoints

1. **Define Core Routes**
   - `/api/authors` - List all authors
   - `/api/authors/{author_id}` - Get author details
   - `/api/authors/{author_id}/works` - List works by author
   - `/api/works/{author_id}/{work_id}` - Get work details
   - `/view/raw/{file_path:path}` - View raw XML
   - `/view/reader/{author_id}/{work_id}/{language}` - View reader-friendly version

2. **Implement API Handlers**
   - Type-safe handlers with Pydantic models
   - Dependency injection for index access
   - Error handling with appropriate HTTP status codes
   - Comprehensive response models with proper documentation

3. **Optimize Performance**
   - Implement caching for frequent requests
   - Use async handlers for I/O-bound operations
   - Efficient index lookups with minimal XML parsing
   
4. **API Documentation**
   - Auto-generated Swagger UI documentation
   - Clear endpoint descriptions and example responses
   - Proper parameter validation and error documentation

## Phase 3: Frontend Templates

1. **Authors List Page**
   - Show all authors with basic information
   - Link to author detail pages

2. **Author Detail Page**
   - Show author metadata
   - List all works by the author
   - Link to work detail pages

3. **Work Detail Page**
   - Show work metadata and available languages
   - Links to view raw XML or reader-friendly version

4. **Reader View**
   - Process XML to readable format
   - Style for readability

## Phase 4: User Preferences

1. **Implement User Preferences**
   - Simple localStorage-based favorites
   - Archived items functionality
   - Client-side filtering

## Phase 5: Search & Advanced Features

1. **Simple Text Search**
   - Client-side filtering for names/titles

2. **Future Vectorization**
   - Prepare for future advanced search features
   - Document linking metadata for eventual vector embeddings

## Implementation Steps

1. **Setup Project Structure**
   ```
   first1k/
   ├── data/                       # Original XML data
   ├── static/                     # CSS, JS, and static assets
   │   ├── css/                    # Stylesheets
   │   └── js/                     # JavaScript files
   ├── src/                        # Source code
   │   └── first1k/
   │       ├── indexer/            # Indexing module
   │       │   ├── __init__.py     # Package exports
   │       │   ├── models.py       # Pydantic models
   │       │   ├── builder.py      # Index construction
   │       │   └── accessor.py     # Index access with caching
   │       ├── utils/              # Utility functions
   │       │   ├── __init__.py
   │       │   ├── file_utils.py   # File change detection
   │       │   └── index_utils.py  # Index management
   │       ├── config.py           # Configuration settings
   │       └── api.py              # FastAPI application
   ├── templates/                  # HTML templates
   ├── index.json                  # Generated index file
   └── setup.cfg                   # Linting configuration
   ```

2. **Update Configuration Settings**
   - Add index file paths and configuration to `src/first1k/config.py`
   - Configure reindexing settings and file change detection

3. **Implement Index Module**
   - Create Pydantic models in `src/first1k/indexer/models.py`
   - Implement index builder in `src/first1k/indexer/builder.py`
   - Add cached access functions in `src/first1k/indexer/accessor.py`
   - Create package API in `src/first1k/indexer/__init__.py`

4. **Implement Utility Functions**
   - Add file change detection in `src/first1k/utils/file_utils.py`
   - Implement index management in `src/first1k/utils/index_utils.py`

5. **FastAPI Setup**
   - Install dependencies: `fastapi`, `uvicorn`, `jinja2`, `pydantic`
   - Configure Jinja2 templates
   - Implement API routes in `src/first1k/api.py`

6. **Frontend Development**
   - Create HTML templates with minimal JavaScript
   - Implement basic CSS for styling
   - Add client-side functionality for preferences

7. **Code Standards Implementation**
   - Configure Black formatting (120-character line length)
   - Set up flake8 with appropriate rules
   - Add pydocstyle D100s requirements for docstrings
   - Ensure proper type annotations throughout the codebase

8. **Testing**
   - Test navigation flow
   - Verify XML and reader views
   - Check index performance with large datasets
   - Test reindexing functionality

## Code Samples

### Modular Implementation Examples

#### src/first1k/indexer/models.py
```python
"""Pydantic models for First1KGreek index data."""
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class TextVersion(BaseModel):
    """A specific version of a text in a particular language."""
    
    id: str = Field(..., description="Unique identifier for the text version")
    language: str = Field(..., description="Language of the text (Greek or English)")
    path: str = Field(..., description="Path to the XML file")


class WorkTitles(BaseModel):
    """Titles for a work in different languages."""
    
    latin: Optional[str] = Field(None, description="Latin title")
    english: Optional[str] = Field(None, description="English title")
    greek: Optional[str] = Field(None, description="Greek title")


class Work(BaseModel):
    """A literary work by an author."""
    
    id: str = Field(..., description="Work identifier (e.g., 'tlg008')")
    titles: WorkTitles = Field(..., description="Titles in different languages")
    texts: List[TextVersion] = Field(default_factory=list, description="Available text versions")


class Author(BaseModel):
    """An author in the First1KGreek corpus."""
    
    id: str = Field(..., description="Author identifier (e.g., 'tlg0032')")
    name: str = Field(..., description="Author name")
    century: Optional[int] = Field(None, description="Century (negative for BCE, positive for CE)")
    type: Optional[str] = Field(None, description="Author type (e.g., 'Historian')")
    works: Dict[str, Work] = Field(default_factory=dict, description="Works by this author")


class Index(BaseModel):
    """The complete First1KGreek index."""
    
    authors: Dict[str, Author] = Field(default_factory=dict, description="Authors by ID")
    version: str = Field("1.0.0", description="Index format version")
    generated_at: str = Field(..., description="Timestamp when index was generated")
```

#### src/first1k/indexer/builder.py
```python
"""Index builder for First1KGreek Browser."""
import os
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from .models import Index, Author, Work, WorkTitles, TextVersion
from ..utils.file_utils import get_modified_files
from ..config import DATA_DIR, INDEX_FILE_PATH


def get_author_name(author_id: str) -> str:
    """Get author name from metadata or known mapping.
    
    Args:
        author_id: Author identifier (e.g., 'tlg0032')
        
    Returns:
        Author name or fallback if not found
    """
    author_map = {
        "tlg0032": "Xenophon",
        "tlg0059": "Plato",
        # Add more mappings as needed
    }
    return author_map.get(author_id, f"Author {author_id}")


def get_work_title(author_path: str, work_dir: str) -> str:
    """Extract work title from __cts__.xml file.
    
    Args:
        author_path: Path to author directory
        work_dir: Work directory name
        
    Returns:
        Work title or fallback if not found
    """
    cts_path = os.path.join(author_path, work_dir, "__cts__.xml")
    if not os.path.exists(cts_path):
        return f"Work {work_dir}"
        
    try:
        tree = ET.parse(cts_path)
        title_elem = tree.find(".//{*}title")
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
    except Exception as e:
        print(f"Error parsing {cts_path}: {str(e)}")
    
    return f"Work {work_dir}"


def build_index() -> Index:
    """Build the complete index from the data directory.
    
    Returns:
        Complete index of authors and works
    """
    # Initialize with empty authors dictionary
    index_data = {
        "authors": {},
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat()
    }
    
    # Scan for author folders
    for author_dir in os.listdir(DATA_DIR):
        author_path = os.path.join(DATA_DIR, author_dir)
        if not os.path.isdir(author_path) or not author_dir.startswith(('tlg', 'ggm')):
            continue
            
        # Add author entry
        author_id = author_dir
        index_data["authors"][author_id] = {
            "id": author_id,
            "name": get_author_name(author_id),
            "works": {}
        }
        
        # Scan for work folders
        for work_dir in os.listdir(author_path):
            work_path = os.path.join(author_path, work_dir)
            if not os.path.isdir(work_path):
                continue
                
            # Add work entry with titles
            work_id = work_dir
            english_title = get_work_title(author_path, work_dir)
            
            index_data["authors"][author_id]["works"][work_id] = {
                "id": work_id,
                "titles": {
                    "latin": english_title,  # Default to same as English
                    "english": english_title
                },
                "texts": []
            }
            
            # Find language versions
            for file_name in os.listdir(work_path):
                if not file_name.endswith('.xml') or file_name == '__cts__.xml':
                    continue
                    
                language = "Greek" if "grc" in file_name else "English" if "eng" in file_name else "Unknown"
                text_id = file_name.replace(".xml", "")
                
                index_data["authors"][author_id]["works"][work_id]["texts"].append({
                    "id": text_id,
                    "language": language,
                    "path": os.path.join(author_path, work_dir, file_name)
                })
    
    # Create Pydantic model for validation and export
    index = Index.parse_obj(index_data)
    
    # Save index
    with open(INDEX_FILE_PATH, 'w') as f:
        json.dump(index.dict(), f, indent=2)
        
    return index


def update_index() -> Index:
    """Update existing index with modified files only.
    
    Returns:
        Updated index
    """
    # Load existing index if available
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                existing_index = Index.parse_raw(f.read())
            except:
                # If parsing fails, rebuild from scratch
                return build_index()
    else:
        # If no index exists, build from scratch
        return build_index()
    
    # Get modified files
    modified_files = get_modified_files(DATA_DIR)
    
    # If no modifications, return existing index
    if not modified_files:
        return existing_index
    
    # TODO: Implement incremental update logic
    # For simplicity, rebuild the entire index for now
    return build_index()
```

#### src/first1k/indexer/accessor.py
```python
"""Index access functions with caching for First1KGreek Browser."""
import os
import json
from typing import Dict, List, Optional, Any
from functools import lru_cache

from .models import Index, Author, Work, TextVersion
from .builder import build_index, update_index
from ..config import INDEX_FILE_PATH


@lru_cache(maxsize=1)
def load_index() -> Index:
    """Load the index from disk with caching.
    
    Returns:
        Loaded index
    """
    if not os.path.exists(INDEX_FILE_PATH):
        # Build index if it doesn't exist
        return build_index()
        
    with open(INDEX_FILE_PATH, 'r') as f:
        index_data = json.load(f)
        return Index.parse_obj(index_data)


def get_author(author_id: str) -> Optional[Author]:
    """Get a specific author by ID.
    
    Args:
        author_id: Author identifier
        
    Returns:
        Author object or None if not found
    """
    index = load_index()
    if author_id in index.authors:
        return index.authors[author_id]
    return None


def get_work(author_id: str, work_id: str) -> Optional[Work]:
    """Get a specific work by author ID and work ID.
    
    Args:
        author_id: Author identifier
        work_id: Work identifier
        
    Returns:
        Work object or None if not found
    """
    author = get_author(author_id)
    if author and work_id in author.works:
        return author.works[work_id]
    return None


def get_all_authors() -> List[Author]:
    """Get all authors in the index.
    
    Returns:
        List of all authors
    """
    index = load_index()
    return list(index.authors.values())


def get_texts_by_language(language: str) -> List[TextVersion]:
    """Get all texts in a specific language.
    
    Args:
        language: Language to filter by
        
    Returns:
        List of text versions in the specified language
    """
    index = load_index()
    result = []
    
    for author in index.authors.values():
        for work in author.works.values():
            for text in work.texts:
                if text.language.lower() == language.lower():
                    result.append(text)
    
    return result


def clear_cache() -> None:
    """Clear the index cache to force reload."""
    load_index.cache_clear()
```

#### src/first1k/utils/file_utils.py
```python
"""File utilities for First1KGreek Browser."""
import os
import hashlib
from typing import Set, Optional
from datetime import datetime
import json

from ..config import LAST_INDEX_TIME_FILE


def get_file_hash(file_path: str) -> str:
    """Get SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hex digest of file hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_modified_files(directory: str) -> Set[str]:
    """Get set of files modified since last indexing.
    
    Args:
        directory: Directory to check for modifications
        
    Returns:
        Set of modified file paths
    """
    # Get last indexing time
    last_index_time = get_last_index_time()
    if not last_index_time:
        # If no last index time, return empty set (will trigger full rebuild)
        return set()
    
    modified_files = set()
    
    # Walk directory and check modification times
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.xml'):
                continue
                
            file_path = os.path.join(root, file)
            mod_time = os.path.getmtime(file_path)
            
            # Convert to datetime for comparison
            mod_datetime = datetime.fromtimestamp(mod_time)
            
            if mod_datetime > last_index_time:
                modified_files.add(file_path)
    
    return modified_files


def get_last_index_time() -> Optional[datetime]:
    """Get timestamp of last indexing operation.
    
    Returns:
        Datetime of last indexing or None if not available
    """
    if not os.path.exists(LAST_INDEX_TIME_FILE):
        return None
        
    try:
        with open(LAST_INDEX_TIME_FILE, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_index_time'])
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def update_last_index_time() -> None:
    """Update the timestamp of last indexing operation."""
    data = {
        'last_index_time': datetime.now().isoformat()
    }
    
    with open(LAST_INDEX_TIME_FILE, 'w') as f:
        json.dump(data, f)
```


### FastAPI App Example

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI(title="First1KGreek Browser")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Load index
def load_index():
    with open("index.json", "r") as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/browse/authors", response_class=HTMLResponse)
async def list_authors(request: Request):
    index = load_index()
    return templates.TemplateResponse(
        "authors.html", 
        {"request": request, "authors": index["authors"]}
    )

@app.get("/browse/authors/{author_id}", response_class=HTMLResponse)
async def author_detail(request: Request, author_id: str):
    index = load_index()
    if author_id not in index["authors"]:
        raise HTTPException(status_code=404, detail="Author not found")
        
    author = index["authors"][author_id]
    return templates.TemplateResponse(
        "author_detail.html", 
        {"request": request, "author": author}
    )

@app.get("/browse/works/{author_id}/{work_id}", response_class=HTMLResponse)
async def work_detail(request: Request, author_id: str, work_id: str):
    index = load_index()
    if author_id not in index["authors"] or work_id not in index["authors"][author_id]["works"]:
        raise HTTPException(status_code=404, detail="Work not found")
        
    author = index["authors"][author_id]
    work = author["works"][work_id]
    return templates.TemplateResponse(
        "work_detail.html", 
        {"request": request, "author": author, "work": work}
    )

@app.get("/view/raw/{file_path:path}")
async def view_raw_xml(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/view/reader/{author_id}/{work_id}/{text_id}", response_class=HTMLResponse)
async def view_reader_friendly(request: Request, author_id: str, work_id: str, text_id: str):
    index = load_index()
    if author_id not in index["authors"] or work_id not in index["authors"][author_id]["works"]:
        raise HTTPException(status_code=404, detail="Work not found")
        
    author = index["authors"][author_id]
    work = author["works"][work_id]
    
    # Find the text
    text = None
    for t in work["texts"]:
        if t["id"] == text_id:
            text = t
            break
            
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Process XML for reading (simplified)
    from xml_utils import process_xml_for_reading
    processed_text = process_xml_for_reading(text["path"])
    
    return templates.TemplateResponse(
        "reader.html", 
        {
            "request": request, 
            "author": author, 
            "work": work, 
            "text": text,
            "content": processed_text
        }
    )
```

### HTML Template Example

```html
<!-- templates/authors.html -->
<!DOCTYPE html>
<html>
<head>
    <title>First1KGreek - Authors</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <h1>First1KGreek Authors</h1>
        
        <div class="authors-grid">
            {% for author_id, author in authors.items() %}
            <div class="author-card">
                <h2>{{ author.name }}</h2>
                <div class="author-meta">
                    {% if author.century %}
                    <span class="century">{{ author.century }} {% if author.century < 0 %}BCE{% else %}CE{% endif %}</span>
                    {% endif %}
                    
                    {% if author.type %}
                    <span class="type">{{ author.type }}</span>
                    {% endif %}
                </div>
                
                <div class="work-count">
                    {{ author.works|length }} work(s)
                </div>
                
                <a href="/browse/authors/{{ author_id }}" class="view-button">View Works</a>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script src="/static/js/favorites.js"></script>
</body>
</html>
```

This implementation plan provides a clear roadmap for rebuilding the First1KGreek Browser with a simplified architecture focused on performance and maintainability.
