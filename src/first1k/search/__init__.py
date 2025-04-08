"""Search functionality for the First1KGreek Browser.

This module provides search capabilities for finding texts and authors.
"""

from .searcher import (
    search_texts,
    search_authors,
    format_search_results
)

__all__ = [
    'search_texts',
    'search_authors',
    'format_search_results'
]
