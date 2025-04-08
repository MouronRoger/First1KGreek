"""XML utilities for the First1KGreek Browser.

This module provides functionality for processing and displaying XML files.
"""

from .processor import (
    parse_xml,
    extract_metadata,
    convert_to_html,
    extract_revision_history
)

__all__ = [
    'parse_xml',
    'extract_metadata',
    'convert_to_html',
    'extract_revision_history'
]
