"""Utilities for file operations and change detection in First1KGreek Browser."""
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