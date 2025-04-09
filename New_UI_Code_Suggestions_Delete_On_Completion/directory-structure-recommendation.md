# First1KGreek Browser Directory Structure Integration

This document outlines the recommended integration of the enhanced authors page and related components into the existing First1KGreek Browser codebase.

## Overview

The enhanced authors page implementation consists of three main components:

1. Enhanced Authors Page UI implementation
2. Author Works API endpoint
3. User Preferences API endpoints

These components should be integrated into the existing directory structure to maintain code organization and separation of concerns.

## Recommended Structure

### 1. Enhanced Authors Page Implementation

```
src/first1k/handlers/browse.py
```

Replace the existing `render_authors_page()` function in this file with the enhanced implementation. This maintains the current organization where browser functionality is in the `handlers/browse.py` module.

### 2. Author Works API Endpoint 

```
src/first1k/handlers/api.py
```

Create a new dedicated module for API endpoints. This keeps the API-specific code separate from the UI rendering code. The module should contain:

- `get_author_works_for_api()` function
- `handle_get_author_works()` function 
- Helper functions for API responses

### 3. User Preferences API Endpoint

```
src/first1k/handlers/preferences.py
```

Create a dedicated module for preference handling containing:

- `handle_update_work_preference()` function
- `handle_bulk_update_preferences()` function
- Helper functions for reading/writing preferences

### 4. Server Route Updates

```
src/first1k/server/server.py
```

Update the `CustomHTTPRequestHandler.do_GET()` and `CustomHTTPRequestHandler.do_POST()` methods to handle the new routes:

```python
# In do_GET method
elif path == '/get_author_works':
    from ..handlers.api import handle_get_author_works
    status_code, content_type, response_data = handle_get_author_works(query_params)
    self.send_response(status_code)
    self.send_header('Content-type', content_type)
    self.end_headers()
    self.wfile.write(response_data.encode('utf-8'))

# In do_POST method
elif path == '/update_work_preference':
    from ..handlers.preferences import handle_update_work_preference
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    status_code, content_type, response_data = handle_update_work_preference(query_params, post_data)
    self.send_response(status_code)
    self.send_header('Content-type', content_type)
    self.end_headers()
    self.wfile.write(response_data.encode('utf-8'))

elif path == '/update_preferences':
    from ..handlers.preferences import handle_bulk_update_preferences
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    status_code, content_type, response_data = handle_bulk_update_preferences(query_params, post_data)
    self.send_response(status_code)
    self.send_header('Content-type', content_type)
    self.end_headers()
    self.wfile.write(response_data.encode('utf-8'))
```

### 5. User Preferences Storage

```
user_preferences.json
```

This file should be stored at the root level of the project, alongside `authors_data.json`.

## Module Imports and Dependencies

Update the imports in the affected files to ensure proper dependencies:

### browse.py
```python
import os
import re
import time
import json
import logging
from pathlib import Path
from ..config import CSS_DIR
```

### api.py
```python
import os
import re
import json
import logging
from pathlib import Path
```

### preferences.py
```python
import json
import logging
from pathlib import Path
```

## Handlers Module Updates

The `src/first1k/handlers/__init__.py` file should be updated to export the new functions:

```python
"""First1KGreek Browser request handlers.

This package contains handlers for different types of HTTP requests,
organized by functionality.
"""

# UI handlers
from .ui import render_main_page

# Browse handlers
from .browse import render_authors_page, render_editors_page

# Search handlers
from .search import render_search_page

# Import/Export handlers
from .import_text import (
    render_import_page,
    render_import_success_page,
    render_import_error_page,
    import_text_from_scaife
)

# View handlers
from .view import render_xml_view_page, render_reader_view_page

# Works handlers
from .works import render_works_page, render_editor_works_page

# API handlers
from .api import handle_get_author_works

# Preferences handlers
from .preferences import handle_update_work_preference, handle_bulk_update_preferences

__all__ = [
    # UI
    'render_main_page',
    
    # Browse
    'render_authors_page',
    'render_editors_page',
    
    # Search
    'render_search_page',
    
    # Import/Export
    'render_import_page',
    'render_import_success_page',
    'render_import_error_page',
    'import_text_from_scaife',
    
    # View
    'render_xml_view_page',
    'render_reader_view_page',
    
    # Works
    'render_works_page',
    'render_editor_works_page',
    
    # API
    'handle_get_author_works',
    
    # Preferences
    'handle_update_work_preference',
    'handle_bulk_update_preferences',
]
```

## Benefits of This Structure

1. **Modularity**: Keeps related functionality together
2. **Separation of concerns**: UI rendering separate from API endpoints
3. **Consistency**: Follows the existing pattern of organizing by function
4. **Maintainability**: Makes future updates easier by isolating different components
5. **Future-proofing**: Positions the code well for HTMX integration later by having clean separation between UI and data

This structure also minimizes changes to existing files, focusing the modifications on adding new functionality rather than significantly altering current code.

## Implementation Steps

1. Create the new modules (`api.py` and `preferences.py`) in the `src/first1k/handlers/` directory
2. Update the `browse.py` file with the enhanced implementation
3. Update the server route handlers in `server.py`
4. Update the `__init__.py` file to include the new modules
5. Test the implementation with a simple "Hello World" response from each endpoint before integrating the full code

## Future HTMX Considerations

The proposed structure is well-suited for future HTMX integration because:

1. API endpoints are separate from UI rendering
2. The enhanced authors page uses semantic HTML that can be easily targeted with HTMX attributes
3. The modular approach makes it easy to replace JavaScript functions with HTMX directives

When implementing HTMX later, the API endpoints could be modified to return HTML fragments instead of JSON responses, allowing for partial page updates without rewriting the entire codebase.