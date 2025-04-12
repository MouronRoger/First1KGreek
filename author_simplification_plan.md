# First1KGreek Browser Implementation Plan

Remembering...
Here's a conceptual explanation of the First1KGreek browser project you can share with Cursor:
First1KGreek Browser: Conceptual Overview
The First1KGreek Browser started as a simple file navigator for the Perseus Digital Library's Greek texts collection. In its original form, it was literally just a "browser" - a way to navigate through a directory structure of XML files containing ancient Greek texts.
Original Architecture
The system had minimal architecture:

Directory structure organized by author ID and work ID
XML files with TEI markup containing the actual texts
Navigation directly mapped to filesystem hierarchy
No intermediate data layer or index

This created significant performance problems when trying to display works, as it required:

Real-time directory traversal
On-the-fly XML parsing for metadata extraction
Complex fallback mechanisms to handle inconsistencies

Simplified Approach
Our new approach inserts a lightweight index layer:
[File System] → [JSON Index] → [User Interface]
The index captures all essential metadata in a simple JSON structure:

Author information (name, century, type)
Work information (titles in different languages)
Text versions with language and file paths

This creates a fast lookup mechanism while preserving the original file organization. The browser becomes a two-step process:

Consult the index for navigation and metadata (fast)
Access the XML files directly only when viewing a specific text

Benefits

Performance: Navigation becomes instant, no more XML parsing until needed
Simplicity: Clean separation between data structure and viewing logic
Maintainability: Single source of truth for metadata
Extensibility: Foundation for additional features (search, preferences, vectorization)

This approach keeps the system true to its roots as a "browser" while addressing the performance bottlenecks that were causing issues.

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

2. **Create Indexing Script**
   - Script to scan the data directory for author folders
   - Parse `__cts__.xml` files for titles and metadata
   - Extract language information from filenames
   - Build and save the index as JSON 
   
3. There should be a prompt to "reindex when data is modified 

Manual trigger with prompt: Provide a clear UI button for manual reindexing with a confirmation prompt
Detection with notification: Detect when data files have been added, modified, or removed, and show a notification suggesting reindexing
Optional automatic mode: Include a configuration setting to enable fully automatic reindexing

Rationale
This hybrid approach works well because:

Data stability: The Perseus collection is relatively static, so automatic reindexing on every start would be unnecessary overhead
Performance consideration: Reindexing could be resource-intensive with a large collection
User control: Scholars might be adding or modifying texts in batches and would prefer to control when reindexing happens
Transparency: Users should understand when/why reindexing is happening

Implementation Approach
pythondef check_for_changes():
    """Check if data directory has changes since last indexing."""
    # Compare modification timestamps or hash of directory listing
    # with stored values from last indexing
    return changes_detected

# In main application
if check_for_changes():
    if config.get('auto_reindex'):
        # Automatically reindex
        build_index()
    else:
        # Show notification
        show_notification("Data changes detected. Would you like to reindex?", 
                          actions=["Reindex Now", "Remind Later"])
## Phase 2: Create FastAPI Endpoints

1. **Define Core Routes**
   - `/api/authors` - List all authors
   - `/api/authors/{author_id}` - Get author details
   - `/api/authors/{author_id}/works` - List works by author
   - `/api/works/{author_id}/{work_id}` - Get work details
   - `/view/raw/{file_path:path}` - View raw XML
   - `/view/reader/{author_id}/{work_id}/{language}` - View reader-friendly version

2. **Implement Handlers**
   - Simple index loading and lookup functions
   - XML-to-reader conversion function (for reader view only)
   - Static file serving for raw XML

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
   ├── data/                 # Original XML data
   ├── static/               # CSS, JS, and static assets
   ├── templates/            # HTML templates
   ├── app.py                # FastAPI application
   ├── indexer.py            # Indexing script
   ├── utils.py              # Helper functions
   └── index.json            # Generated index file
   ```

2. **Create Indexing Script**
   - Implement the index builder in `indexer.py`
   - Run to generate initial `index.json`

3. **FastAPI Setup**
   - Install dependencies: `fastapi`, `uvicorn`, `jinja2`
   - Configure Jinja2 templates
   - Implement routes in `app.py`

4. **Frontend Development**
   - Create HTML templates with minimal JavaScript
   - Implement basic CSS for styling
   - Add client-side functionality for preferences

5. **Testing**
   - Test navigation flow
   - Verify XML and reader views
   - Check performance with large datasets

## Code Samples

### Indexing Script Example

```python
import os
import json
import re
import xml.etree.ElementTree as ET

def get_author_name(author_id):
    """Get author name from metadata or known mapping."""
    author_map = {
        "tlg0032": "Xenophon",
        "tlg0059": "Plato",
        # Add more mappings as needed
    }
    return author_map.get(author_id, f"Author {author_id}")

def get_work_title(author_path, work_dir):
    """Extract work title from __cts__.xml file."""
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

def build_index():
    """Build the index from the data directory."""
    index = {"authors": {}}
    
    # Scan for author folders
    for author_dir in os.listdir("data"):
        author_path = os.path.join("data", author_dir)
        if not os.path.isdir(author_path) or not author_dir.startswith(('tlg', 'ggm')):
            continue
            
        # Add author entry
        author_id = author_dir
        index["authors"][author_id] = {
            "id": author_id,
            "name": get_author_name(author_id),
            "works": {}
        }
        
        # Scan for work folders
        for work_dir in os.listdir(author_path):
            work_path = os.path.join(author_path, work_dir)
            if not os.path.isdir(work_path):
                continue
                
            # Add work entry
            work_id = work_dir
            title = get_work_title(author_path, work_dir)
            
            index["authors"][author_id]["works"][work_id] = {
                "id": work_id,
                "title": title,
                "texts": []
            }
            
            # Find language versions
            for file_name in os.listdir(work_path):
                if not file_name.endswith('.xml') or file_name == '__cts__.xml':
                    continue
                    
                language = "Greek" if "grc" in file_name else "English" if "eng" in file_name else "Unknown"
                text_id = file_name.replace(".xml", "")
                
                index["authors"][author_id]["works"][work_id]["texts"].append({
                    "id": text_id,
                    "language": language,
                    "path": os.path.join(author_path, work_dir, file_name)
                })
    
    # Save index
    with open("index.json", 'w') as f:
        json.dump(index, f, indent=2)
        
    return index

if __name__ == "__main__":
    print("Building index...")
    index = build_index()
    print(f"Index built with {len(index['authors'])} authors")
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
