"""Utilities for index management and validation in First1KGreek Browser."""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from ..config import INDEX_FILE_PATH, DATA_DIR


def is_index_valid() -> bool:
    """Check if the current index is valid and exists.
    
    Returns:
        True if index exists and is a valid JSON file, False otherwise
    """
    if not os.path.exists(INDEX_FILE_PATH):
        return False
        
    try:
        with open(INDEX_FILE_PATH, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Invalid index file: {e}")
        return False


def should_rebuild_index() -> bool:
    """Determine if the index should be rebuilt.
    
    Returns:
        True if the index should be rebuilt, False otherwise
    """
    # Check if index exists
    if not os.path.exists(INDEX_FILE_PATH):
        logging.info("Index file does not exist. Rebuild required.")
        return True
        
    # Check if index is valid JSON
    if not is_index_valid():
        logging.info("Index file is invalid. Rebuild required.")
        return True
        
    # Additional checks could be added here
    
    return False


def get_index_stats() -> Dict[str, Any]:
    """Get statistics about the current index.
    
    Returns:
        Dictionary with index statistics
    """
    if not os.path.exists(INDEX_FILE_PATH):
        return {
            "exists": False,
            "size": 0,
            "author_count": 0,
            "work_count": 0,
            "text_count": 0,
            "last_modified": None
        }
    
    try:
        file_size = os.path.getsize(INDEX_FILE_PATH)
        file_modified = os.path.getmtime(INDEX_FILE_PATH)
        
        with open(INDEX_FILE_PATH, 'r') as f:
            index_data = json.load(f)
            
            author_count = len(index_data.get("authors", {}))
            
            # Count works and texts
            work_count = 0
            text_count = 0
            
            for author_id, author in index_data.get("authors", {}).items():
                work_count += len(author.get("works", {}))
                
                for work_id, work in author.get("works", {}).items():
                    text_count += len(work.get("texts", []))
            
            return {
                "exists": True,
                "size": file_size,
                "size_formatted": f"{file_size / 1024 / 1024:.2f} MB",
                "author_count": author_count,
                "work_count": work_count,
                "text_count": text_count,
                "last_modified": file_modified,
                "generated_at": index_data.get("generated_at", "Unknown")
            }
    except (json.JSONDecodeError, KeyError, IOError) as e:
        logging.error(f"Error getting index stats: {e}")
        return {
            "exists": True,
            "size": os.path.getsize(INDEX_FILE_PATH) if os.path.exists(INDEX_FILE_PATH) else 0,
            "error": str(e),
            "author_count": 0,
            "work_count": 0,
            "text_count": 0,
            "last_modified": os.path.getmtime(INDEX_FILE_PATH) if os.path.exists(INDEX_FILE_PATH) else None
        }


def check_index_integrity() -> Tuple[bool, List[str]]:
    """Check the integrity of the index.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if not os.path.exists(INDEX_FILE_PATH):
        return False, ["Index file does not exist"]
    
    try:
        with open(INDEX_FILE_PATH, 'r') as f:
            index_data = json.load(f)
            
            # Check required fields
            if "authors" not in index_data:
                issues.append("Missing 'authors' field in index")
                
            if "version" not in index_data:
                issues.append("Missing 'version' field in index")
                
            if "generated_at" not in index_data:
                issues.append("Missing 'generated_at' field in index")
            
            # Check authors data
            for author_id, author in index_data.get("authors", {}).items():
                if not isinstance(author, dict):
                    issues.append(f"Author {author_id} is not a dictionary")
                    continue
                    
                if "id" not in author:
                    issues.append(f"Author {author_id} is missing 'id' field")
                
                if "name" not in author:
                    issues.append(f"Author {author_id} is missing 'name' field")
                    
                if "works" not in author or not isinstance(author["works"], dict):
                    issues.append(f"Author {author_id} has invalid 'works' field")
                    continue
                    
                # Check works data
                for work_id, work in author.get("works", {}).items():
                    if not isinstance(work, dict):
                        issues.append(f"Work {author_id}/{work_id} is not a dictionary")
                        continue
                    
                    if "id" not in work:
                        issues.append(f"Work {author_id}/{work_id} is missing 'id' field")
                        
                    if "titles" not in work or not isinstance(work["titles"], dict):
                        issues.append(f"Work {author_id}/{work_id} has invalid 'titles' field")
                    
                    if "texts" not in work or not isinstance(work["texts"], list):
                        issues.append(f"Work {author_id}/{work_id} has invalid 'texts' field")
                        continue
                    
                    # Check text versions
                    for i, text in enumerate(work.get("texts", [])):
                        if not isinstance(text, dict):
                            issues.append(f"Text {i} in {author_id}/{work_id} is not a dictionary")
                            continue
                        
                        if "id" not in text:
                            issues.append(f"Text {i} in {author_id}/{work_id} is missing 'id' field")
                            
                        if "language" not in text:
                            issues.append(f"Text {i} in {author_id}/{work_id} is missing 'language' field")
                            
                        if "path" not in text:
                            issues.append(f"Text {i} in {author_id}/{work_id} is missing 'path' field")
                        elif not os.path.exists(text["path"]):
                            issues.append(f"Text file not found: {text['path']}")
            
        return len(issues) == 0, issues
    except (json.JSONDecodeError, IOError) as e:
        return False, [f"Error reading index: {str(e)}"] 