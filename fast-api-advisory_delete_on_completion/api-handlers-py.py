"""API handlers for First1KGreek FastAPI implementation.

This module provides handler functions for API endpoints, adapting the
existing functionality to work with FastAPI.
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from .. import config

logger = logging.getLogger(__name__)

def get_authors_list(search: Optional[str] = None, century: Optional[int] = None, 
                     type: Optional[str] = None, page: int = 1, limit: int = 25) -> List[Dict]:
    """Get list of authors with optional filtering"""
    authors_file = Path("authors_data.json")
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading authors data: {str(e)}")
        return []
    
    # Convert to list format
    authors_list = []
    for author_id, data in authors_data.items():
        authors_list.append({
            "id": author_id,
            "name": data.get("name", author_id),
            "century": data.get("century", 0),
            "type": data.get("type", "Unknown"),
            "works_count": get_author_works_count(author_id)
        })
    
    # Apply filters
    if search:
        search = search.lower()
        authors_list = [a for a in authors_list if search in a["name"].lower()]
    
    if century:
        authors_list = [a for a in authors_list if a["century"] == century]
    
    if type and type != "all":
        authors_list = [a for a in authors_list if a["type"] == type]
    
    # Apply preferences
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    for author in authors_list:
        author["is_favorite"] = author["id"] in favorites
        author["is_archived"] = author["id"] in archived
    
    # Paginate
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    return authors_list[start_idx:end_idx]

def get_author_details(author_id: str) -> Optional[Dict]:
    """Get details for a specific author"""
    authors_file = Path("authors_data.json")
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading authors data: {str(e)}")
        return None
    
    if author_id not in authors_data:
        return None
    
    author_data = authors_data[author_id]
    
    # Apply preferences
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    return {
        "id": author_id,
        "name": author_data.get("name", author_id),
        "century": author_data.get("century", 0),
        "type": author_data.get("type", "Unknown"),
        "works_count": get_author_works_count(author_id),
        "is_favorite": author_id in favorites,
        "is_archived": author_id in archived
    }

def author_exists(author_id: str) -> bool:
    """Check if an author exists"""
    author_dir = os.path.join('data', author_id)
    return os.path.exists(author_dir)

def get_author_works_count(author_id: str) -> int:
    """Count the number of works for an author"""
    works_count = 0
    author_dir = os.path.join('data', author_id)
    
    if not os.path.exists(author_dir):
        return works_count
    
    # Count each work directory that contains XML files
    for work_dir_name in os.listdir(author_dir):
        work_dir_path = os.path.join(author_dir, work_dir_name)
        if not os.path.isdir(work_dir_path):
            continue
            
        # Skip if there are no XML files
        xml_files = [f for f in os.listdir(work_dir_path) if f.endswith('.xml') and f != '__cts__.xml']
        if xml_files:
            works_count += 1
    
    return works_count

def get_author_works_for_api(author_id: str) -> List[Dict]:
    """Get works for an author formatted for the API response"""
    works_data = []
    author_dir = os.path.join('data', author_id)
    
    if not os.path.exists(author_dir):
        logger.warning(f"Author directory not found: {author_dir}")
        return works_data
    
    # Get user preferences for works
    user_prefs = get_user_preferences()
    favorites = user_prefs.get("favorites", [])
    archived = user_prefs.get("archived", [])
    
    # Process each work directory
    work_dirs = [d for d in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, d))]
    logger.info(f"Found {len(work_dirs)} potential work directories for author {author_id}")
    
    for work_dir_name in work_dirs:
        work_dir_path = os.path.join(author_dir, work_dir_name)
        
        # Create work ID base
        work_id_base = f"{author_id}.{work_dir_name}"
        
        # Get XML files in this directory (excluding __cts__.xml)
        xml_files = [f for f in os.listdir(work_dir_path) if f.endswith('.xml') and f != '__cts__.xml']
        
        # Skip if there are no XML files
        if not xml_files:
            logger.debug(f"Skipping {work_dir_name} - no XML files found")
            continue
        
        logger.debug(f"Processing work {work_id_base} with {len(xml_files)} XML files")
        
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
                logger.error(f"Error reading work metadata: {str(e)}")
        
        # Process each XML file directly
        for xml_file in xml_files:
            file_path = os.path.join(work_dir_path, xml_file)
            
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
                    logger.error(f"Error reading file {file_path}: {str(e)}")
                    title = f"Work {work_dir_name}"
            
            # Create a unique work ID that includes the language
            unique_work_id = f"{work_id_base}.{language_for_id}"
            
            # Create work data
            work_data = {
                "id": unique_work_id,
                "title": title,
                "language": language_display,
                "file_path": file_path,
                "is_favorite": unique_work_id in favorites,
                "is_archived": unique_work_id in archived
            }
            
            works_data.append(work_data)
    
    logger.info(f"Found {len(works_data)} works for author {author_id}")
    return works_data

def get_user_preferences() -> Dict:
    """Get user preferences from JSON file"""
    prefs_file = Path("user_preferences.json")
    if prefs_file.exists():
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading user preferences: {str(e)}")
    
    # Default empty preferences
    return {"favorites": [], "archived": []}

def update_user_preferences(prefs: Dict) -> None:
    """Update user preferences file"""
    prefs_file = Path("user_preferences.json")
    try:
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2)
        logger.info("User preferences updated successfully")
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")

def update_work_preference(data: Dict) -> Dict:
    """Update preference for a specific work"""
    try:
        work_id = data.get('work_id')
        preference_type = data.get('type')  # 'favorite', 'archive', or 'delete'
        action = data.get('action')  # 'add' or 'remove'
        
        if not work_id or not preference_type or not action:
            return {
                "status": "error",
                "message": "Missing required parameters: work_id, type, and action"
            }
        
        # Load existing preferences
        user_prefs = get_user_preferences()
        
        # Update preferences based on type and action
        if preference_type == 'favorite':
            preference_list = user_prefs.get('favorites', [])
            if action == 'add' and work_id not in preference_list:
                preference_list.append(work_id)
            elif action == 'remove' and work_id in preference_list:
                preference_list.remove(work_id)
            user_prefs['favorites'] = preference_list
            
        elif preference_type == 'archive':
            preference_list = user_prefs.get('archived', [])
            if action == 'add' and work_id not in preference_list:
                preference_list.append(work_id)
            elif action == 'remove' and work_id in preference_list:
                preference_list.remove(work_id)
            user_prefs['archived'] = preference_list
            
        elif preference_type == 'delete':
            # For delete, add to archived list (same as archive)
            preference_list = user_prefs.get('archived', [])
            if work_id not in preference_list:
                preference_list.append(work_id)
            user_prefs['archived'] = preference_list
        
        # Save updated preferences
        update_user_preferences(user_prefs)
        
        return {
            "status": "success",
            "message": f"Updated {preference_type} preference for {work_id}"
        }
        
    except Exception as e:
        logger.error(f"Error updating work preference: {str(e)}")
        return {
            "status": "error",
            "message": f"Error updating preference: {str(e)}"
        }

def update_bulk_preferences(preferences_data: Dict) -> Dict:
    """Bulk update preferences"""
    try:
        # Load existing preferences
        user_prefs = get_user_preferences()
        
        # Update with new preferences
        if 'favorites' in preferences_data:
            user_prefs['favorites'] = preferences_data['favorites']
        
        if 'archived' in preferences_data:
            user_prefs['archived'] = preferences_data['archived']
        
        # Save updated preferences
        update_user_preferences(user_prefs)
        
        return {
            "status": "success",
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return {
            "status": "error",
            "message": f"Error updating preferences: {str(e)}"
        }

def search_corpus(search_term: str) -> List[Dict]:
    """Search for the given term in all XML files"""
    results = []
    
    # Normalize search term
    search_term = search_term.strip().lower()
    if not search_term:
        return results
        
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.xml') and not file == '__cts__.xml':
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find all occurrences (case-insensitive)
                    positions = []
                    lower_content = content.lower()
                    pos = lower_content.find(search_term)
                    
                    while pos >= 0:
                        positions.append(pos)
                        pos = lower_content.find(search_term, pos + 1)
                        
                    if positions:
                        # Extract author information
                        author_name = "Unknown"
                        author_matches = re.findall(r'<author.*?>(.*?)</author>', content)
                        if author_matches and len(author_matches[0].strip()) > 0:
                            author_name = author_matches[0]
                            
                        # Extract title information
                        work_title = "Unknown"
                        title_matches = re.findall(r'<title.*?>(.*?)</title>', content)
                        if title_matches:
                            work_title = title_matches[0]
                        else:
                            # Try to find a title in TEI header
                            title_start = content.find('<title')
                            if title_start > 0:
                                title_end = content.find('</title>', title_start)
                                if title_end > 0:
                                    tag_end = content.find(">", title_start)
                                    work_title = content[tag_end+1:title_end].strip()
                        
                        # Extract editor information
                        editor_name = "Unknown"
                        editor_matches = re.findall(r'<editor>(.*?)</editor>', content)
                        if editor_matches and len(editor_matches[0].strip()) > 0:
                            editor_name = editor_matches[0]
                        
                        # Get context for the first occurrence
                        pos = positions[0]
                        start_context = max(0, pos - 100)
                        end_context = min(len(content), pos + len(search_term) + 100)
                        context = content[start_context:end_context]
                        
                        # Highlight search term in context
                        search_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                        context = search_pattern.sub(f'<span class="highlight">{search_term}</span>', context)
                        
                        # Clean up context by removing partial tags at edges
                        if start_context > 0:
                            tag_start = context.find("<", 0, 50)
                            if tag_start > 0:
                                context = context[tag_start:]
                        
                        if end_context < len(content):
                            last_close_tag = context.rfind(">", len(context) - 50)
                            if last_close_tag > 0:
                                context = context[:last_close_tag + 1]
                        
                        # Add to results
                        results.append({
                            "file_path": file_path,
                            "author": author_name,
                            "title": work_title,
                            "editor": editor_name,
                            "context": context,
                            "occurrence_count": len(positions)
                        })
                except Exception as e:
                    logger.error(f"Error searching {file_path}: {str(e)}")
    
    # Sort results by number of occurrences
    results.sort(key=lambda x: x["occurrence_count"], reverse=True)
    
    return results

def get_xml_content(file_path: str) -> Optional[Dict]:
    """Get XML content from a file"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        author_name = "Unknown"
        author_matches = re.findall(r'<author.*?>(.*?)</author>', content)
        if author_matches and len(author_matches[0].strip()) > 0:
            author_name = author_matches[0]
            
        work_title = "Unknown"
        title_matches = re.findall(r'<title.*?>(.*?)</title>', content)
        if title_matches:
            work_title = title_matches[0]
            
        # Determine language from filename for Perseus texts
        language = "Greek"  # Default
        if 'perseus-eng' in file_path:
            language = "English"
        elif 'perseus-grc' in file_path:
            language = "Greek"
            
        return {
            "content": content,
            "author": author_name,
            "title": work_title,
            "language": language,
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def get_reader_content(file_path: str) -> Optional[Dict]:
    """Get reader-friendly content from a file"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Extract metadata
        author_name = "Unknown"
        author_matches = re.findall(r'<author.*?>(.*?)</author>', xml_content)
        if author_matches and len(author_matches[0].strip()) > 0:
            author_name = author_matches[0]
            
        work_title = "Unknown"
        title_matches = re.findall(r'<title.*?>(.*?)</title>', xml_content)
        if title_matches:
            work_title = title_matches[0]
            
        # Determine language from filename for Perseus texts
        language = "Greek"  # Default
        if 'perseus-eng' in file_path:
            language = "English"
        elif 'perseus-grc' in file_path:
            language = "Greek"
            
        # Extract text content - Remove XML tags but preserve line breaks
        text_content = re.sub(r'<[^>]+>', '', xml_content)
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = text_content.strip()
        
        return {
            "content": text_content,
            "author": author_name,
            "title": work_title,
            "language": language,
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None
