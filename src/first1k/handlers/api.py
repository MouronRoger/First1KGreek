"""API handler for author works data in First1KGreek Browser.

This module provides API endpoints for retrieving works data for a specific author.
"""

import os
import re
import json
import logging
from pathlib import Path

from ..config import DATA_DIR, USER_PREFS_FILE
from ..utils.path import normalize_path, create_data_path

logger = logging.getLogger(__name__)


def get_author_works_for_api(author_id):
    """
    Get works for an author formatted for the API response.
    
    Args:
        author_id (str): The ID of the author
        
    Returns:
        list: A list of work dictionaries formatted for the API
    """
    works_data = []
    author_dir = os.path.join(DATA_DIR, author_id)
    
    logger.info(f"API - Retrieving works for author: {author_id}")
    logger.info(f"API - Looking in directory: {author_dir}")
    
    if not os.path.exists(author_dir):
        logger.warning(f"API - Author directory not found: {author_dir}")
        return works_data
    
    logger.info(f"API - Successfully found author directory at: {author_dir}")
    
    # Get user preferences for works
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    # Process each work directory
    work_dirs = [d for d in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, d))]
    logger.info(f"API - Found {len(work_dirs)} potential work directories for author {author_id}")
    
    # Log the work directories to help with debugging
    logger.debug(f"API - Work directories: {work_dirs}")
    
    for work_dir_name in work_dirs:
        work_dir_path = os.path.join(author_dir, work_dir_name)
        
        # Create work ID base
        work_id_base = f"{author_id}.{work_dir_name}"
        
        # Get XML files in this directory (excluding __cts__.xml)
        xml_files = [f for f in os.listdir(work_dir_path) if f.endswith('.xml') and f != '__cts__.xml']
        
        # Skip if there are no XML files
        if not xml_files:
            logger.debug(f"API - Skipping {work_dir_name} - no XML files found")
            continue
        
        logger.debug(f"API - Processing work {work_id_base} with {len(xml_files)} XML files")
        
        # Load titles from __cts__.xml if available
        title_map = {}  # Maps language code to title
        work_cts_path = os.path.join(work_dir_path, '__cts__.xml')
        
        if os.path.exists(work_cts_path):
            try:
                with open(work_cts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find edition (Greek) title
                edition_match = re.search(r'<ti:edition[^>]*xml:lang="grc"[^>]*>.*?<ti:label[^>]*>(.*?)</ti:label>', content, re.DOTALL)
                if edition_match:
                    title_map['grc'] = edition_match.group(1).strip()
                
                # Find translation (English) title
                translation_match = re.search(r'<ti:translation[^>]*xml:lang="eng"[^>]*>.*?<ti:label[^>]*>(.*?)</ti:label>', content, re.DOTALL)
                if translation_match:
                    title_map['eng'] = translation_match.group(1).strip()
                
                # If we can't find specific language titles, use the work title as fallback
                if not title_map:
                    work_title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                    if work_title_match:
                        title_map['default'] = work_title_match.group(1).strip()
            
            except Exception as e:
                logger.error(f"API - Error reading work metadata: {str(e)}")
        
        # Process each XML file directly
        for xml_file in xml_files:
            file_path = os.path.join(work_dir_path, xml_file)
            
            # Create a relative path using the path utility
            relative_path = os.path.join("data", str(author_id), str(work_dir_name), str(xml_file))
            
            # Determine language directly from filename
            language = 'grc'  # Default to Greek
            language_for_id = 'grc'
            
            if 'perseus-eng' in xml_file:
                language = 'eng'
                language_for_id = 'eng'
                language_display = "English"
            elif 'perseus-grc' in xml_file:
                language = 'grc'
                language_for_id = 'grc'
                language_display = "Greek"
            else:
                # Try to extract language from file if not obvious from name
                language_display = "Greek"  # Default
            
            # Use appropriate title from the CTS file based on language
            if language in title_map:
                title = title_map[language]
            elif 'default' in title_map:
                title = title_map['default']
            else:
                # Last resort: extract from the XML file itself
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read(10000)
                        title_match = re.search(r'<title[^>]*>(.*?)</title>', file_content)
                        if title_match:
                            title = title_match.group(1).strip()
                        else:
                            title = f"Work {work_dir_name}"
                except Exception as e:
                    logger.error(f"API - Error reading file {file_path}: {str(e)}")
                    title = f"Work {work_dir_name}"
            
            # Create a unique work ID that includes the language
            unique_work_id = f"{work_id_base}.{language_for_id}"
            
            # Create work data
            work_data = {
                "id": unique_work_id,
                "title": title,
                "language": language_display,
                "file_path": relative_path,
                "author_id": author_id,
                "is_favorite": unique_work_id in favorites,
                "is_archived": unique_work_id in archived,
                # Add files array that the frontend expects
                "files": [{
                    "name": xml_file,
                    "type": "xml",
                    "path": relative_path
                }]
            }
            
            works_data.append(work_data)
    
    # Log the final works data structure
    logger.info(f"API - Final works_data has {len(works_data)} items")
    if works_data:
        # Log the structure of the first work to understand its format
        logger.debug(f"API - First work data structure: {list(works_data[0].keys())}")
        logger.debug(f"API - Sample work data: {works_data[0]}")
    
    return works_data


def get_user_preferences():
    """
    Get user preferences from JSON file.
    
    Returns:
        dict: User preferences for favorites and archived items.
    """
    prefs_file = Path(USER_PREFS_FILE)
    if prefs_file.exists():
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading user preferences: {str(e)}")
    
    # Default empty preferences
    return {"favorites": [], "archived": []}


def handle_get_author_works(query_params):
    """
    Handle API request for author works.
    
    Args:
        query_params (dict): Query parameters from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    author_id = query_params.get('author_id')
    
    if not author_id:
        logger.error("Missing author_id parameter in request")
        return 400, 'application/json', json.dumps({"error": "Missing author_id parameter"})
    
    logger.info(f"Handling /get_author_works request for author_id: {author_id}")
    
    try:
        # Check if author directory exists
        author_dir = os.path.join(DATA_DIR, author_id)
        logger.info(f"Looking for author directory at: {author_dir}")
        
        if not os.path.exists(author_dir):
            logger.warning(f"Author directory not found: {author_dir}")
            return 404, 'application/json', json.dumps({"error": f"Author {author_id} not found"})
        
        try:    
            # Get author works
            works = get_author_works_for_api(author_id)
            
            if not works:
                logger.warning(f"No works found for author: {author_id}")
                return 200, 'application/json', json.dumps([])
                
            logger.info(f"Successfully retrieved {len(works)} works for author {author_id}")
            return 200, 'application/json', json.dumps(works)
        except Exception as inner_e:
            logger.error(f"Error in get_author_works_for_api: {str(inner_e)}", exc_info=True)
            return 500, 'application/json', json.dumps({"error": f"Error retrieving works: {str(inner_e)}"})
    except Exception as e:
        logger.error(f"Error retrieving works for {author_id}: {str(e)}", exc_info=True)
        return 500, 'application/json', json.dumps({"error": f"Error retrieving works: {str(e)}"}) 