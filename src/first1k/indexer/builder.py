"""Index builder for First1KGreek Browser."""
import os
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Callable

from .models import Index, Author, Work, WorkTitles, TextVersion
from ..utils.file_utils import get_modified_files, update_last_index_time
from ..config import DATA_DIR, INDEX_FILE_PATH


def get_author_name(author_id: str, author_path: str) -> str:
    """Get author name from __cts__.xml or fallback to known mapping.
    
    Args:
        author_id: Author identifier (e.g., 'tlg0032')
        author_path: Path to author directory
        
    Returns:
        Author name or fallback if not found
    """
    # Try to get name from __cts__.xml
    cts_path = os.path.join(author_path, "__cts__.xml")
    if os.path.exists(cts_path):
        try:
            tree = ET.parse(cts_path)
            # Using namespace to find groupname element
            ns = {"ti": "http://chs.harvard.edu/xmlns/cts"}
            name_elem = tree.find(".//ti:groupname", ns)
            if name_elem is not None and name_elem.text:
                return name_elem.text.strip()
        except Exception as e:
            print(f"Error parsing {cts_path}: {str(e)}")
    
    # Fallback to known mapping
    author_map = {
        "tlg0032": "Xenophon",
        "tlg0059": "Plato",
        "tlg0012": "Homer",
        "tlg0031": "New Testament",
        "tlg0007": "Plutarch",
        "tlg0085": "Sophocles",
        "tlg0062": "Lucian",
        # Add more mappings as needed
    }
    return author_map.get(author_id, f"Author {author_id}")


def get_work_titles(author_path: str, work_dir: str) -> WorkTitles:
    """Extract work titles from __cts__.xml file.
    
    Args:
        author_path: Path to author directory
        work_dir: Work directory name
        
    Returns:
        WorkTitles object with available titles
    """
    titles = WorkTitles(
        latin=None,
        english=None,
        greek=None
    )
    
    cts_path = os.path.join(author_path, work_dir, "__cts__.xml")
    if not os.path.exists(cts_path):
        # Fallback title is the work_dir
        titles.english = f"Work {work_dir}"
        return titles
        
    try:
        tree = ET.parse(cts_path)
        ns = {"ti": "http://chs.harvard.edu/xmlns/cts"}
        
        # Try to get English title first
        title_elem = tree.find(".//ti:title[@xml:lang='eng']", ns)
        if title_elem is not None and title_elem.text:
            titles.english = title_elem.text.strip()
            
        # Try to get Latin title
        title_elem = tree.find(".//ti:title[@xml:lang='lat']", ns)
        if title_elem is not None and title_elem.text:
            titles.latin = title_elem.text.strip()
            
        # Try to get Greek title
        title_elem = tree.find(".//ti:title[@xml:lang='grc']", ns)
        if title_elem is not None and title_elem.text:
            titles.greek = title_elem.text.strip()
            
        # If no English title was found but we have another language, use the first available
        if titles.english is None:
            if titles.latin is not None:
                titles.english = titles.latin
            elif titles.greek is not None:
                titles.english = titles.greek
                
        # If still no title, use the work_dir as fallback
        if titles.english is None:
            titles.english = f"Work {work_dir}"
            
    except Exception as e:
        print(f"Error parsing {cts_path}: {str(e)}")
        titles.english = f"Work {work_dir}"
    
    return titles


def detect_language_from_filename(filename: str) -> str:
    """Detect language from filename patterns.
    
    Args:
        filename: Name of the file
        
    Returns:
        Language code (e.g., 'Greek' or 'English')
    """
    if "grc" in filename:
        return "Greek"
    elif "eng" in filename:
        return "English"
    elif "lat" in filename:
        return "Latin"
    else:
        # Default to Greek for First1KGreek corpus
        return "Greek"


def build_index(progress_callback: Optional[Callable[[int, str], None]] = None) -> Index:
    """Build the complete index from the data directory.
    
    Args:
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Complete index of authors and works
    """
    # Initialize with empty authors dictionary
    index_data = {
        "authors": {},
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat()
    }
    
    # Count total authors for progress calculation
    author_dirs = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d)) and 
                  (d.startswith('tlg') or d.startswith('ggm'))]
    total_authors = len(author_dirs)
    
    # Scan for author folders
    for idx, author_dir in enumerate(author_dirs):
        author_path = os.path.join(DATA_DIR, author_dir)
        
        # Update progress if callback provided
        if progress_callback:
            progress_percent = int((idx / total_authors) * 100)
            progress_callback(progress_percent, f"Processing author {author_dir} ({idx+1}/{total_authors})")
            
        # Add author entry
        author_id = author_dir
        author_name = get_author_name(author_id, author_path)
        
        index_data["authors"][author_id] = {
            "id": author_id,
            "name": author_name,
            "century": None,  # Could be extracted from external data source
            "type": None,     # Could be extracted from external data source
            "works": {}
        }
        
        # Scan for work folders
        work_dirs = [d for d in os.listdir(author_path) if os.path.isdir(os.path.join(author_path, d)) and 
                    not d.startswith('__') and not d.startswith('.')]
        
        for work_dir in work_dirs:
            work_path = os.path.join(author_path, work_dir)
                
            # Add work entry with titles
            work_id = work_dir
            work_titles = get_work_titles(author_path, work_dir)
            
            index_data["authors"][author_id]["works"][work_id] = {
                "id": work_id,
                "titles": work_titles.dict(exclude_none=True),
                "texts": []
            }
            
            # Find language versions
            for file_name in os.listdir(work_path):
                if not file_name.endswith('.xml') or file_name == '__cts__.xml':
                    continue
                    
                language = detect_language_from_filename(file_name)
                text_id = file_name.replace(".xml", "")
                
                index_data["authors"][author_id]["works"][work_id]["texts"].append({
                    "id": text_id,
                    "language": language,
                    "path": os.path.join(author_path, work_dir, file_name)
                })
    
    # Create Pydantic model for validation and export
    index = Index.parse_obj(index_data)
    
    # Save index
    with open(INDEX_FILE_PATH, 'w') as f:
        json.dump(index.dict(), f, indent=2)
        
    # Update last index time
    update_last_index_time()
        
    return index


def update_index(progress_callback: Optional[Callable[[int, str], None]] = None) -> Index:
    """Update existing index with modified files only.
    
    Args:
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Updated index
    """
    # Load existing index if available
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                existing_index = Index.parse_raw(f.read())
            except:
                # If parsing fails, rebuild from scratch
                if progress_callback:
                    progress_callback(0, "Invalid index file. Rebuilding from scratch.")
                return build_index(progress_callback)
    else:
        # If no index exists, build from scratch
        if progress_callback:
            progress_callback(0, "No index file found. Building from scratch.")
        return build_index(progress_callback)
    
    # Get modified files
    if progress_callback:
        progress_callback(10, "Checking for modified files...")
    
    modified_files = get_modified_files(DATA_DIR)
    
    # If no modifications, return existing index
    if not modified_files:
        if progress_callback:
            progress_callback(100, "No modified files found. Index is up to date.")
        return existing_index
    
    if progress_callback:
        progress_callback(20, f"Found {len(modified_files)} modified files. Updating index...")
    
    # Convert index to dict for easier manipulation
    index_dict = existing_index.dict()
    
    # Process each modified file
    for i, file_path in enumerate(modified_files):
        if progress_callback:
            progress_percent = 20 + int((i / len(modified_files)) * 80)
            progress_callback(progress_percent, f"Processing file {i+1}/{len(modified_files)}")
        
        # Extract author_id, work_id, and filename from path
        # Expected path format: data/tlg0032/tlg008/tlg0032.tlg008.perseus-grc2.xml
        path_parts = file_path.split(os.sep)
        if len(path_parts) < 4:
            continue
            
        author_id = path_parts[-3]
        work_id = path_parts[-2]
        file_name = path_parts[-1]
        
        # Skip __cts__.xml files - they affect metadata which requires rebuilding those entries
        if file_name == "__cts__.xml":
            # If it's an author-level __cts__.xml, update author name
            if work_id == "__cts__.xml":
                author_path = os.path.join(DATA_DIR, author_id)
                if author_id in index_dict["authors"]:
                    index_dict["authors"][author_id]["name"] = get_author_name(author_id, author_path)
            # If it's a work-level __cts__.xml, update work titles
            else:
                author_path = os.path.join(DATA_DIR, author_id)
                if author_id in index_dict["authors"] and work_id in index_dict["authors"][author_id]["works"]:
                    work_titles = get_work_titles(author_path, work_id)
                    index_dict["authors"][author_id]["works"][work_id]["titles"] = work_titles.dict(exclude_none=True)
            continue
        
        # Skip non-XML files
        if not file_name.endswith('.xml'):
            continue
            
        # Check if author exists in index
        if author_id not in index_dict["authors"]:
            # If not, we need to add the author
            author_path = os.path.join(DATA_DIR, author_id)
            author_name = get_author_name(author_id, author_path)
            
            index_dict["authors"][author_id] = {
                "id": author_id,
                "name": author_name,
                "century": None,
                "type": None,
                "works": {}
            }
        
        # Check if work exists for this author
        if work_id not in index_dict["authors"][author_id]["works"]:
            # If not, we need to add the work
            author_path = os.path.join(DATA_DIR, author_id)
            work_titles = get_work_titles(author_path, work_id)
            
            index_dict["authors"][author_id]["works"][work_id] = {
                "id": work_id,
                "titles": work_titles.dict(exclude_none=True),
                "texts": []
            }
        
        # Check if this text version already exists
        text_id = file_name.replace(".xml", "")
        language = detect_language_from_filename(file_name)
        
        # Look for this text version in the existing texts
        text_found = False
        for i, text in enumerate(index_dict["authors"][author_id]["works"][work_id]["texts"]):
            if text["id"] == text_id:
                # Update the existing text entry
                index_dict["authors"][author_id]["works"][work_id]["texts"][i] = {
                    "id": text_id,
                    "language": language,
                    "path": file_path
                }
                text_found = True
                break
                
        # If text not found, add it
        if not text_found:
            index_dict["authors"][author_id]["works"][work_id]["texts"].append({
                "id": text_id,
                "language": language,
                "path": file_path
            })
    
    # Update timestamp
    index_dict["generated_at"] = datetime.now().isoformat()
    
    # Create Pydantic model for validation and export
    updated_index = Index.parse_obj(index_dict)
    
    # Save updated index
    with open(INDEX_FILE_PATH, 'w') as f:
        json.dump(updated_index.dict(), f, indent=2)
        
    # Update last index time
    update_last_index_time()
        
    return updated_index 