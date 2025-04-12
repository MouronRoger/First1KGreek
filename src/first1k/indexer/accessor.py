"""Index access functions with caching for First1KGreek Browser."""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from functools import lru_cache
import time

from .models import Index, Author, Work, TextVersion
from .builder import build_index, update_index
from ..utils.index_utils import is_index_valid, should_rebuild_index
from ..config import INDEX_FILE_PATH, INDEX_CHECK_INTERVAL, AUTO_REINDEX


# Time of last index check for file changes
_last_check_time = 0


@lru_cache(maxsize=1)
def load_index() -> Index:
    """Load the index from disk with caching.
    
    Returns:
        Loaded index
    """
    global _last_check_time
    
    # Check if we need to rebuild index or if it doesn't exist
    if should_rebuild_index():
        logging.info("Building index from scratch.")
        return build_index()
    
    # Check if we should look for updates (based on check interval)
    current_time = time.time()
    if AUTO_REINDEX and (current_time - _last_check_time) > INDEX_CHECK_INTERVAL:
        _last_check_time = current_time
        try:
            # Check for updates, but don't rebuild completely
            return update_index()
        except Exception as e:
            logging.error(f"Error updating index: {e}")
            # If update fails, try to load existing index
    
    # Load existing index
    try:
        with open(INDEX_FILE_PATH, 'r') as f:
            index_data = json.load(f)
            return Index.parse_obj(index_data)
    except Exception as e:
        logging.error(f"Error loading index: {e}")
        # If loading fails, rebuild
        return build_index()


def get_author(author_id: str) -> Optional[Author]:
    """Get a specific author by ID.
    
    Args:
        author_id: Author identifier
        
    Returns:
        Author object or None if not found
    """
    index = load_index()
    if author_id in index.authors:
        return index.authors[author_id]
    return None


def get_work(author_id: str, work_id: str) -> Optional[Work]:
    """Get a specific work by author ID and work ID.
    
    Args:
        author_id: Author identifier
        work_id: Work identifier
        
    Returns:
        Work object or None if not found
    """
    author = get_author(author_id)
    if author and work_id in author.works:
        return author.works[work_id]
    return None


def get_text(author_id: str, work_id: str, text_id: str) -> Optional[TextVersion]:
    """Get a specific text version by author ID, work ID, and text ID.
    
    Args:
        author_id: Author identifier
        work_id: Work identifier
        text_id: Text version identifier
        
    Returns:
        TextVersion object or None if not found
    """
    work = get_work(author_id, work_id)
    if work:
        for text in work.texts:
            if text.id == text_id:
                return text
    return None


def get_all_authors() -> List[Author]:
    """Get all authors in the index.
    
    Returns:
        List of all authors
    """
    index = load_index()
    return list(index.authors.values())


def get_authors_by_ids(author_ids: List[str]) -> List[Author]:
    """Get multiple authors by their IDs.
    
    Args:
        author_ids: List of author identifiers
        
    Returns:
        List of found authors (skipping any not found)
    """
    index = load_index()
    return [index.authors[author_id] for author_id in author_ids if author_id in index.authors]


def get_works_by_author(author_id: str) -> List[Work]:
    """Get all works by a specific author.
    
    Args:
        author_id: Author identifier
        
    Returns:
        List of works by the author
    """
    author = get_author(author_id)
    if author:
        return list(author.works.values())
    return []


def get_texts_by_language(language: str) -> List[Dict[str, Any]]:
    """Get all texts in a specific language with their metadata.
    
    Args:
        language: Language to filter by (e.g., 'Greek', 'English')
        
    Returns:
        List of text versions in the specified language with author and work info
    """
    index = load_index()
    result = []
    
    for author in index.authors.values():
        for work in author.works.values():
            for text in work.texts:
                if text.language.lower() == language.lower():
                    result.append({
                        "author": {
                            "id": author.id,
                            "name": author.name
                        },
                        "work": {
                            "id": work.id,
                            "title": work.titles.english or work.titles.latin or work.titles.greek or f"Work {work.id}"
                        },
                        "text": {
                            "id": text.id,
                            "language": text.language,
                            "path": text.path
                        }
                    })
    
    return result


def search_authors(query: str) -> List[Author]:
    """Search for authors by name.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching authors
    """
    index = load_index()
    query = query.lower()
    
    results = []
    for author in index.authors.values():
        if query in author.name.lower() or query in author.id.lower():
            results.append(author)
            
    return results


def search_works(query: str) -> List[Dict[str, Any]]:
    """Search for works by title.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching works with author info
    """
    index = load_index()
    query = query.lower()
    
    results = []
    for author in index.authors.values():
        for work in author.works.values():
            title = work.titles.english or work.titles.latin or work.titles.greek or ""
            if (query in title.lower() or 
                query in work.id.lower() or
                (work.titles.latin and query in work.titles.latin.lower()) or
                (work.titles.greek and query in work.titles.greek.lower())):
                
                results.append({
                    "author": {
                        "id": author.id,
                        "name": author.name
                    },
                    "work": {
                        "id": work.id,
                        "title": title,
                        "titles": work.titles.dict(exclude_none=True)
                    }
                })
                
    return results


def clear_cache() -> None:
    """Clear the index cache to force reload."""
    load_index.cache_clear()
    
    
def force_update() -> Index:
    """Force an update of the index regardless of cache.
    
    Returns:
        Updated index
    """
    # Clear cache first
    clear_cache()
    
    # Update index
    updated_index = update_index()
    
    return updated_index 