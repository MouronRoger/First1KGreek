"""Editor functionality for the First1KGreek Browser.

This module provides text editing capabilities for the browser application.
"""

from .manager import (
    save_edited_text,
    get_edit_history,
    create_backup
)

__all__ = [
    'save_edited_text',
    'get_edit_history',
    'create_backup'
]
