"""Browse handlers for the First1K Greek Browser."""

from typing import Dict, List, Optional, Tuple

from ..xml_utils.processor import (
    get_author_metadata,
    get_editor_metadata,
    get_work_metadata
)

def render_browse_page() -> str:
    """Return HTML for the browse page."""
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Browse First1K Greek Texts</h2>
        <div style="margin-bottom: 20px">
            <h3>Browse by Author</h3>
            <form action="/browse/authors" method="get">
                <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer">
                    View All Authors
                </button>
            </form>
        </div>
        
        <div style="margin-bottom: 20px">
            <h3>Browse by Editor</h3>
            <form action="/browse/editors" method="get">
                <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer">
                    View All Editors
                </button>
            </form>
        </div>
        
        <div>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """

def render_authors_page(authors: List[Tuple[str, str]]) -> str:
    """Return HTML for the authors listing page.
    
    Args:
        authors: List of (author_id, author_name) tuples
    """
    authors_html = ""
    for author_id, author_name in authors:
        authors_html += f"""
        <div style="margin-bottom: 10px">
            <a href="/browse/author/{author_id}" style="color: #4CAF50; text-decoration: none">
                {author_name}
            </a>
        </div>
        """

    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Browse Authors</h2>
        <div style="margin-bottom: 20px">
            {authors_html}
        </div>
        <div>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """

def render_editors_page(editors: List[str]) -> str:
    """Return HTML for the editors listing page.
    
    Args:
        editors: List of editor names
    """
    editors_html = ""
    for editor in editors:
        editors_html += f"""
        <div style="margin-bottom: 10px">
            <a href="/browse/editor/{editor}" style="color: #4CAF50; text-decoration: none">
                {editor}
            </a>
        </div>
        """

    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Browse Editors</h2>
        <div style="margin-bottom: 20px">
            {editors_html}
        </div>
        <div>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """

def render_works_list(works: List[Dict[str, str]]) -> str:
    """Return HTML for a list of works.
    
    Args:
        works: List of work metadata dictionaries
    """
    works_html = ""
    for work in works:
        works_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; background-color: white; border-radius: 4px">
            <h3>{work.get('title', 'Untitled')}</h3>
            <p>Language: {work.get('language', 'Unknown')}</p>
            <p>Editor: {work.get('editor', 'Unknown')}</p>
            <a href="/view/{work.get('file_path', '')}" style="color: #4CAF50; text-decoration: none">
                View Text
            </a>
        </div>
        """
    return works_html

def render_author_works_page(author_id: str, works: Optional[List[Dict[str, str]]] = None) -> str:
    """Return HTML for an author's works page.
    
    Args:
        author_id: The ID of the author
        works: Optional list of work metadata dictionaries
    """
    if works is None:
        works = []
        
    author_metadata = get_author_metadata(author_id)
    author_name = author_metadata.get('name', 'Unknown Author')
    
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Works by {author_name}</h2>
        <div style="margin-bottom: 20px">
            {render_works_list(works)}
        </div>
        <div>
            <a href="/browse/authors" style="color: #4CAF50; text-decoration: none">Back to Authors</a>
            <span style="margin: 0 10px">|</span>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """

def render_editor_works_page(editor_name: str, works: Optional[List[Dict[str, str]]] = None) -> str:
    """Return HTML for an editor's works page.
    
    Args:
        editor_name: The name of the editor
        works: Optional list of work metadata dictionaries
    """
    if works is None:
        works = []
        
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Works edited by {editor_name}</h2>
        <div style="margin-bottom: 20px">
            {render_works_list(works)}
        </div>
        <div>
            <a href="/browse/editors" style="color: #4CAF50; text-decoration: none">Back to Editors</a>
            <span style="margin: 0 10px">|</span>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """
