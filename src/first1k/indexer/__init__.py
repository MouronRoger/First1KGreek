"""
First1KGreek indexer module.

This module provides functionality for building and accessing an index
of authors, works, and text versions for the First1KGreek corpus.
"""

# Import models
from .models import Author, Work, WorkTitles, TextVersion, Index

# Import accessor functions
from .accessor import (
    load_index, get_author, get_work, get_text,
    get_all_authors, get_authors_by_ids, get_works_by_author,
    get_texts_by_language, search_authors, search_works,
    clear_cache, force_update
)

# Import builder functions
from .builder import build_index, update_index

# Define public API
__all__ = [
    # Models
    'Author', 'Work', 'WorkTitles', 'TextVersion', 'Index',
    
    # Accessor functions
    'load_index', 'get_author', 'get_work', 'get_text',
    'get_all_authors', 'get_authors_by_ids', 'get_works_by_author',
    'get_texts_by_language', 'search_authors', 'search_works',
    'clear_cache', 'force_update',
    
    # Builder functions
    'build_index', 'update_index'
] 