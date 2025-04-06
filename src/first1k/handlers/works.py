"""Works listing handlers for the First1KGreek Browser."""

import os
import re
from typing import Dict, List, Optional

from ..xml_utils.processor import get_author_metadata, get_editor_metadata


def get_works_by_author(author_id: str) -> List[Dict[str, str]]:
    """Get list of works by a specific author.

    Args:
        author_id: ID of the author to get works for

    Returns:
        List of works, each containing title, language, and editor info
    """
    works = []
    author_dir = os.path.join("data", author_id)

    if not os.path.exists(author_dir):
        return []

    # Get author name from metadata
    author_name = None
    author_cts_path = os.path.join(author_dir, "__cts__.xml")
    if os.path.exists(author_cts_path):
        try:
            with open(author_cts_path, "r", encoding="utf-8") as f:
                content = f.read()
                name_match = re.search(r"<ti:groupname[^>]*>(.*?)</ti:groupname>", content)
                if name_match:
                    author_name = name_match.group(1).strip()
        except Exception as e:
            print(f"Error reading author metadata: {str(e)}")

    # If no name in metadata, try to get from files
    if not author_name:
        for work_dir in os.listdir(author_dir):
            work_path = os.path.join(author_dir, work_dir)
            if os.path.isdir(work_path):
                for file in os.listdir(work_path):
                    if file.endswith(".xml") and not file == "__cts__.xml":
                        file_path = os.path.join(work_path, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read(10000)
                                author_matches = re.findall(r"<author[^>]*>(.*?)</author>", content)
                                if author_matches and len(author_matches[0].strip()) > 0:
                                    author_name = author_matches[0].strip()
                                    break
                        except Exception as e:
                            print(f"Error reading {file_path}: {str(e)}")
                if author_name:
                    break

    if not author_name:
        author_name = f"Author {author_id}"

    # Get works
    for work_dir in os.listdir(author_dir):
        work_path = os.path.join(author_dir, work_dir)
        if os.path.isdir(work_path):
            work_title = None
            work_language = None
            work_editor = None

            # Try to get metadata from work's __cts__.xml
            work_cts_path = os.path.join(work_path, "__cts__.xml")
            if os.path.exists(work_cts_path):
                try:
                    with open(work_cts_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        title_match = re.search(r"<ti:title[^>]*>(.*?)</ti:title>", content)
                        if title_match:
                            work_title = title_match.group(1).strip()
                        lang_match = re.search(r'xml:lang="([^"]+)"', content)
                        if lang_match:
                            work_language = lang_match.group(1)
                except Exception as e:
                    print(f"Error reading work metadata: {str(e)}")

            # Get XML files in work directory
            for file in os.listdir(work_path):
                if file.endswith(".xml") and not file == "__cts__.xml":
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(10000)

                        # Get title if not found in metadata
                        if not work_title:
                            title_matches = re.findall(r"<title[^>]*>(.*?)</title>", content)
                            if title_matches:
                                work_title = title_matches[0].strip()

                        # Get editor
                        editor_matches = re.findall(r"<editor[^>]*>(.*?)</editor>", content)
                        if editor_matches and len(editor_matches[0].strip()) > 0:
                            work_editor = editor_matches[0].strip()

                        works.append(
                            {
                                "id": work_dir,
                                "title": work_title or f"Work {work_dir}",
                                "language": work_language or "grc",
                                "editor": work_editor or "Unknown",
                                "file_path": file_path,
                            }
                        )
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")

    return author_name, works


def get_works_by_editor(editor_name: str) -> List[Dict[str, str]]:
    """Get list of works edited by a specific editor.

    Args:
        editor_name: Name of the editor to get works for

    Returns:
        List of works, each containing title, language, and author info
    """
    works = []

    # Walk through all XML files
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith(".xml") and not file == "__cts__.xml":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read(10000)

                    # Check if this file was edited by our editor
                    editor_matches = re.findall(r"<editor[^>]*>(.*?)</editor>", content)
                    if editor_matches:
                        for match in editor_matches:
                            if editor_name.lower() in match.lower():
                                # Get work details
                                author_name = "Unknown"
                                author_matches = re.findall(r"<author[^>]*>(.*?)</author>", content)
                                if author_matches and len(author_matches[0].strip()) > 0:
                                    author_name = author_matches[0].strip()

                                work_title = "Unknown"
                                title_matches = re.findall(r"<title[^>]*>(.*?)</title>", content)
                                if title_matches:
                                    work_title = title_matches[0].strip()

                                works.append(
                                    {
                                        "author": author_name,
                                        "title": work_title,
                                        "file_path": file_path,
                                    }
                                )
                                break
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")

    return works


def render_works_page(author_id: str, works: Optional[List[Dict[str, str]]] = None) -> str:
    """Return HTML for the works listing page.

    Args:
        author_id: ID of the author whose works to display
        works: Optional list of works to display

    Returns:
        HTML string for the works page
    """
    author_name, works = get_works_by_author(author_id)

    return f"""
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px">
            <h2>Works by {author_name}</h2>
            <div style="margin-top: 20px">
                {render_works_list(works)}
            </div>
            <div style="margin-top: 20px">
                <a href="/" style="background-color: #5bc0de; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px">
                    Return to Home
                </a>
            </div>
        </div>
    """


def render_editor_works_page(editor_name: str, works: Optional[List[Dict[str, str]]] = None) -> str:
    """Return HTML for the editor's works listing page.

    Args:
        editor_name: Name of the editor whose works to display
        works: Optional list of works to display

    Returns:
        HTML string for the editor's works page
    """
    works = get_works_by_editor(editor_name)

    return f"""
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px">
            <h2>Works edited by {editor_name}</h2>
            <div style="margin-top: 20px">
                {render_works_list(works)}
            </div>
            <div style="margin-top: 20px">
                <a href="/" style="background-color: #5bc0de; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px">
                    Return to Home
                </a>
            </div>
        </div>
    """


def render_works_list(works):
    if not works:
        return """
            <div style="color: #666">
                No works found
            </div>
        """

    works_html = []
    for work in works:
        works_html.append(
            f"""
            <div style="margin-top: 10px; padding: 10px; background-color: white; border-radius: 3px">
                <h3>{work['title']}</h3>
                <p style="color: #666">Language: {work['language']}</p>
                <p style="color: #666">Editor: {work['editor']}</p>
                <div style="margin-top: 10px">
                    <a href="/view/{work['file_path']}" style="color: #4CAF50; text-decoration: none">
                        View Text
                    </a>
                </div>
            </div>
        """
        )

    return "\n".join(works_html)
