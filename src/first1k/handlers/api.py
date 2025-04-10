"""API handler for author works data in First1KGreek Browser.

This module provides API endpoints for retrieving works data for a specific author.
"""

import os
import re
import json
import logging
from pathlib import Path

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
    author_dir = os.path.join('data', author_id)
    
    if not os.path.exists(author_dir):
        logger.warning(f"Author directory not found: {author_dir}")
        return works_data
    
    logger.info(f"Retrieving works for author: {author_id}")
    
    # Get user preferences for works
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    # Process each work directory
    work_dirs = [d for d in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, d))]
    logger.info(f"Found {len(work_dirs)} potential work directories for author {author_id}")
    
    for work_dir_name in work_dirs:
        work_dir_path = os.path.join(author_dir, work_dir_name)
        
        # Create work ID
        work_id = f"{author_id}.{work_dir_name}"
        
        # Get XML files in this directory
        xml_files = [f for f in os.listdir(work_dir_path) if f.endswith('.xml') and f != '__cts__.xml']
        
        # Skip if there are no XML files
        if not xml_files:
            logger.debug(f"Skipping {work_dir_name} - no XML files found")
            continue
        
        logger.debug(f"Processing work {work_id} with {len(xml_files)} XML files")
        
        # Get work metadata
        work_title = None
        work_language = None
        
        # Try to get metadata from work's __cts__.xml
        work_cts_path = os.path.join(work_dir_path, '__cts__.xml')
        if os.path.exists(work_cts_path):
            try:
                with open(work_cts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find all editions and translations
                    editions = re.findall(r'<ti:edition[^>]*>(.*?)</ti:edition>', content, re.DOTALL)
                    translations = re.findall(r'<ti:translation[^>]*>(.*?)</ti:translation>', content, re.DOTALL)
                    
                    # Process all versions (editions and translations)
                    versions = editions + translations
                    
                    if versions:
                        # Use first version's details as fallback for files without specific language matches
                        first_version = versions[0]
                        
                        # First priority: Look for language identifier in the URN (perseus-grc, perseus-eng)
                        urn_match = re.search(r'urn="([^"]+)"', first_version)
                        if urn_match:
                            urn = urn_match.group(1)
                            if 'perseus-grc' in urn:
                                work_language = 'grc'
                            elif 'perseus-eng' in urn:
                                work_language = 'eng'
                        
                        # Second priority: Extract language from the edition/translation tag
                        if not work_language:
                            lang_match = re.search(r'xml:lang="([^"]+)"', first_version)
                            if lang_match:
                                work_language = lang_match.group(1)
                        
                        # Extract label (title) from the label tag
                        label_match = re.search(r'<ti:label[^>]*>(.*?)</ti:label>', first_version)
                        if label_match:
                            work_title = label_match.group(1).strip()
                    
                    # Fallback to work-level title if no versions found
                    if not work_title:
                        title_match = re.search(r'<ti:title[^>]*>(.*?)</ti:title>', content)
                        if title_match:
                            work_title = title_match.group(1).strip()
                        
                        # Also get language from work level as fallback
                        if not work_language:
                            lang_match = re.search(r'xml:lang="([^"]+)"', content)
                            if lang_match:
                                work_language = lang_match.group(1)
            except Exception as e:
                logger.error(f"Error reading work metadata for {work_id}: {str(e)}")
        
        # Process each XML file
        for xml_file in xml_files:
            file_path = os.path.join(work_dir_path, xml_file)
            
            try:
                # Extract information from file if not found in metadata
                if not work_title or not work_language:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(10000)  # Read beginning where metadata usually is
                        
                    # Get title if not found in metadata
                    if not work_title:
                        title_matches = re.findall(r'<title[^>]*>(.*?)</title>', content)
                        if title_matches:
                            work_title = title_matches[0].strip()
                    
                    # Always determine language from filename for Perseus texts
                    # This takes precedence over metadata since the pattern is universal
                    if 'perseus-eng' in xml_file:
                        work_language = 'eng'
                    elif 'perseus-grc' in xml_file:
                        work_language = 'grc'
                    # Check if the filename contains a language identifier in any other form
                    else:
                        file_lang_match = re.search(r'\.([a-z]{3})\d*\.', xml_file)
                        if file_lang_match and file_lang_match.group(1) in ['eng', 'grc', 'lat']:
                            work_language = file_lang_match.group(1)
                        # Only use metadata or default if not a recognized pattern
                        elif not work_language:
                            # Default to Greek if no other language info available
                            work_language = 'grc'
                
                # Format language for display
                language_display = "English" if work_language == "eng" else "Greek"
                
                # Create work data object
                work_data = {
                    "id": work_id,
                    "title": work_title or f"Work {work_dir_name}",
                    "language": language_display,
                    "file_path": file_path,
                    "is_favorite": work_id in favorites,
                    "is_archived": work_id in archived
                }
                
                works_data.append(work_data)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
    
    logger.info(f"Found {len(works_data)} works for author {author_id}")
    return works_data


def get_user_preferences():
    """
    Get user preferences from JSON file.
    
    Returns:
        dict: User preferences for favorites and archived items.
    """
    prefs_file = Path("user_preferences.json")
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
    author_id = query_params.get('author_id', [''])[0]
    
    if not author_id:
        logger.error("Missing author_id parameter in request")
        return 400, 'application/json', json.dumps({"error": "Missing author_id parameter"})
    
    logger.info(f"Handling /get_author_works request for author_id: {author_id}")
    
    try:
        # Check if author directory exists
        author_dir = os.path.join('data', author_id)
        if not os.path.exists(author_dir):
            logger.warning(f"Author directory not found: {author_dir}")
            return 404, 'application/json', json.dumps({"error": f"Author {author_id} not found"})
            
        # Get author works
        works = get_author_works_for_api(author_id)
        
        if not works:
            logger.warning(f"No works found for author: {author_id}")
            return 200, 'application/json', json.dumps([])
            
        logger.info(f"Successfully retrieved {len(works)} works for author {author_id}")
        return 200, 'application/json', json.dumps(works)
    except Exception as e:
        logger.error(f"Error retrieving works for {author_id}: {str(e)}", exc_info=True)
        return 500, 'application/json', json.dumps({"error": f"Error retrieving works: {str(e)}"}) 