"""Handler modules for First1KGreek Browser.

This package contains handler modules for different types of requests.
"""

import time

# UI handlers
from .ui import render_main_page, get_base_js_scripts, get_base_css_links

# Browse handlers
from .browse import render_authors_page, render_editors_page, handle_browse_authors, handle_browse_editors, handle_home_page

# Search handlers
from .search import render_search_page, search_corpus

# Import/Export handlers
from .import_export import render_import_page, render_export_page

# View handlers
from .view import render_xml_view_page, render_reader_view_page

# Works handlers
from .works import render_works_page, render_editor_works_page, get_works_by_author, get_works_by_editor, get_author_works_for_api

# API handlers
from .api import handle_get_author_works

# Preferences handlers
from .preferences import handle_update_work_preference, handle_bulk_update_preferences, get_user_preferences, update_user_preferences

# Common variable to include FastAPI JavaScript files
# For use in page headers
def get_api_js_scripts():
    """Get script tags for FastAPI JavaScript files.
    
    Returns:
        str: HTML script tags for FastAPI JavaScript files
    """
    return """
    <script src="/static/js/api.js?v={timestamp}" defer></script>
    <script src="/static/js/api-adapters.js?v={timestamp}" defer></script>
    """.format(timestamp=int(time.time()))

__all__ = [
    # UI
    'render_main_page',
    
    # Browse
    'render_authors_page',
    'render_editors_page',
    'handle_browse_authors',
    'handle_browse_editors',
    'handle_home_page',
    
    # Search
    'render_search_page',
    'search_corpus',
    
    # Import/Export
    'render_import_page',
    'render_export_page',
    
    # View
    'render_xml_view_page',
    'render_reader_view_page',
    
    # Works
    'render_works_page',
    'render_editor_works_page',
    'get_works_by_author',
    'get_works_by_editor',
    'get_author_works_for_api',
    
    # API
    'handle_get_author_works',
    
    # Preferences
    'handle_update_work_preference',
    'handle_bulk_update_preferences',
    'get_user_preferences',
    'update_user_preferences',
    
    # UI utilities
    'get_base_js_scripts',
    'get_base_css_links',
    'get_api_js_scripts'
]
