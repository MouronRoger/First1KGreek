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
]
