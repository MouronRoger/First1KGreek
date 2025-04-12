"""First1KGreek HTTP request handler implementations.

This package contains handlers for different HTTP request types including browsing, search, and content viewing.
"""

import logging
import time

logger = logging.getLogger(__name__)

# UI handlers
from .ui import render_main_page, get_base_js_scripts, get_base_css_links

# Browse handlers
from .browse import render_authors_page, render_editors_page, handle_browse_authors, handle_browse_editors, handle_home_page

# Search handlers
from .search import handle_search_request, render_search_page

# Import/Export handlers
from .import_text import render_import_page, handle_import_text

# View handlers
from .view import handle_view_xml, handle_view_text, handle_view_reader, handle_view_raw

# Works handlers
from .works import get_author_works_for_api
from .api import handle_get_author_works

# Preferences handlers
from .preferences import handle_update_work_preference, handle_update_preference, get_user_preferences

# Common variable to include FastAPI JavaScript files
# For use in page headers
def get_api_js_scripts():
    """Get script tags for FastAPI JavaScript files.
    
    Returns:
        str: HTML script tags for FastAPI JavaScript files
    """
    timestamp = int(time.time())
    return f"""
    <script src="/static/js/api.js?v={timestamp}" defer></script>
    <script src="/static/js/api-adapters.js?v={timestamp}" defer></script>
    <script src="/static/js/error-handler.js?v={timestamp}" defer></script>
    <script src="/static/js/loading-state.js?v={timestamp}" defer></script>
    """

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
    'handle_search_request',
    
    # Import/Export
    'render_import_page',
    'handle_import_text',
    
    # View
    'handle_view_xml',
    'handle_view_text',
    'handle_view_reader',
    'handle_view_raw',
    
    # Works
    'get_author_works_for_api',
    'handle_get_author_works',
    
    # Preferences
    'handle_update_work_preference',
    'handle_update_preference',
    'get_user_preferences',
    
    # UI utilities
    'get_base_js_scripts',
    'get_base_css_links',
    'get_api_js_scripts'
]
