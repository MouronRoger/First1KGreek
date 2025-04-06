"""Import handlers for First1KGreek Browser."""

import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.error import HTTPError, URLError

from ..config import MAIN_STYLESHEET


def import_text_from_scaife(scaife_url, provided_author_name="", provided_work_title=""):
    """Import text from Scaife URL and save to the corpus."""
    print(f"Importing from URL: {scaife_url}")

    # Extract URN from URL
    urn_match = re.search(r"urn:cts:greekLit:([^:]+)\.([^:]+)\.([^:/]+)", scaife_url)
    if not urn_match:
        raise ValueError("Invalid Scaife URL format - could not extract URN")

    author_id = urn_match.group(1)  # e.g., tlg0007
    work_id = urn_match.group(2)  # e.g., tlg136
    edition_id = urn_match.group(3)  # e.g., perseus-grc2

    # Create full id for file
    full_id = f"{author_id}.{work_id}.{edition_id}"

    # Create directory structure
    author_dir = os.path.join("data", author_id)
    work_dir = os.path.join(author_dir, work_id)

    os.makedirs(work_dir, exist_ok=True)

    # Fetch XML content from Scaife
    try:
        response = urllib.request.urlopen(scaife_url)
        xml_content = response.read().decode("utf-8")
    except (URLError, HTTPError) as e:
        raise Exception(f"Failed to fetch content: {str(e)}")

    # Determine author name and work title
    author_name = provided_author_name
    if not author_name:
        # Try to get from existing files
        try:
            author_name = get_author_name_from_files(author_id)
        except Exception:
            # Try author map
            author_name = get_author_name_from_id(author_id)

    if not author_name:
        author_name = f"Author {author_id}"

    # Get work title
    work_title = provided_work_title
    if not work_title:
        # Try to extract from XML
        extracted_title = extract_title_from_xml(xml_content)
        if extracted_title:
            work_title = extracted_title
        else:
            # Check if work already exists and has a title
            try:
                existing_cts_path = os.path.join(work_dir, "__cts__.xml")
                if os.path.exists(existing_cts_path):
                    tree = ET.parse(existing_cts_path)
                    title_elem = tree.find(".//{*}title")
                    if title_elem is not None and title_elem.text:
                        work_title = title_elem.text
            except Exception:
                pass

    if not work_title:
        work_title = f"Work {work_id}"

    # Create author metadata file if it doesn't exist
    author_cts_path = os.path.join(author_dir, "__cts__.xml")
    if not os.path.exists(author_cts_path):
        author_cts_content = f"""<ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:greekLit:{author_id}">
    <ti:groupname xml:lang="eng">{author_name}</ti:groupname>
</ti:textgroup>"""
        with open(author_cts_path, "w", encoding="utf-8") as f:
            f.write(author_cts_content)
        print(f"Created author metadata: {author_cts_path}")

    # Create work metadata file if it doesn't exist
    work_cts_path = os.path.join(work_dir, "__cts__.xml")
    if not os.path.exists(work_cts_path):
        language = detect_language_from_xml(xml_content) or "grc"
        work_cts_content = f"""<ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" groupUrn="urn:cts:greekLit:{author_id}" xml:lang="{language}" urn="urn:cts:greekLit:{author_id}.{work_id}">
    <ti:title xml:lang="eng">{work_title}</ti:title>
    <ti:edition urn="urn:cts:greekLit:{full_id}" workUrn="urn:cts:greekLit:{author_id}.{work_id}" xml:lang="{language}">
        <ti:label xml:lang="eng">{work_title}</ti:label>
        <ti:description xml:lang="eng">Imported from Scaife/Perseus</ti:description>
    </ti:edition>
</ti:work>"""
        with open(work_cts_path, "w", encoding="utf-8") as f:
            f.write(work_cts_content)
        print(f"Created work metadata: {work_cts_path}")

    # Save the XML content to file
    text_file_path = os.path.join(work_dir, f"{full_id}.xml")
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"Saved text file: {text_file_path}")

    return f"Imported {work_title} by {author_name} ({full_id})"


def get_author_name_from_files(author_id):
    """Attempt to find an author name from XML files."""
    author_path = os.path.join("data", author_id)
    if not os.path.exists(author_path):
        return None

    # Check files to find the author name
    for work_dir in os.listdir(author_path):
        work_path = os.path.join(author_path, work_dir)
        if os.path.isdir(work_path):
            for file in os.listdir(work_path):
                if file.endswith(".xml") and not file == "__cts__.xml":
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(10000)  # Read beginning where metadata usually is

                        # Look for author tag with reasonable content
                        author_matches = re.findall(r"<author[^>]*>(.*?)</author>", content)
                        if author_matches and len(author_matches[0].strip()) > 0:
                            return author_matches[0].strip()

                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")

    return None


def get_author_name_from_id(author_id):
    """Get author name from ID using various methods."""
    author_map = {
        "tlg0001": "Thucydides",
        "tlg0003": "Herodotus",
        "tlg0004": "Diogenes Laertius",
        "tlg0007": "Plutarch",
        "tlg0012": "Homer",
        "tlg0059": "Plato",
        "tlg0086": "Aristotle",
    }
    return author_map.get(author_id)


def extract_title_from_xml(xml_content):
    """Extract the title from the XML content."""
    try:
        root = ET.fromstring(xml_content)
        # Look for title elements
        for title_tag in root.findall(".//{*}title"):
            if title_tag.text and title_tag.text.strip():
                return title_tag.text.strip()
        return None
    except Exception as e:
        print(f"Warning: Could not extract title from XML: {str(e)}")
        return None


def detect_language_from_xml(xml_content):
    """Detect the language from the XML content."""
    try:
        root = ET.fromstring(xml_content)
        # Check for xml:lang attribute
        for elem in root.findall(".//*[@xml:lang]", {"xml": "http://www.w3.org/XML/1998/namespace"}):
            lang = elem.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang:
                return lang
        # Default to Greek for most First1K texts
        return "grc"
    except Exception as e:
        print(f"Warning: Could not detect language from XML: {str(e)}")
        return "grc"


def render_import_page() -> str:
    """Return HTML for the import page."""
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Import Text</h2>
        <div style="margin-bottom: 20px">
            <form action="/import" method="post">
                <div style="margin-bottom: 15px">
                    <label for="author_name" style="display: block; margin-bottom: 5px">Author Name:</label>
                    <input type="text" id="author_name" name="author_name" required
                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px">
                </div>

                <div style="margin-bottom: 15px">
                    <label for="work_title" style="display: block; margin-bottom: 5px">Work Title:</label>
                    <input type="text" id="work_title" name="work_title" required
                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px">
                </div>

                <div style="margin-bottom: 15px">
                    <label for="text_content" style="display: block; margin-bottom: 5px">Text Content (XML):</label>
                    <textarea id="text_content" name="text_content" required
                             style="width: 100%; height: 200px; padding: 8px; border: 1px solid #ddd; border-radius: 4px"></textarea>
                </div>

                <button type="submit"
                        style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer">
                    Import Text
                </button>
            </form>
        </div>

        <div>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """


def render_import_success_page(author_name: str, work_title: str) -> str:
    """Return HTML for the import success page.

    Args:
        author_name: The name of the author whose work was imported
        work_title: The title of the imported work
    """
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Import Successful</h2>
        <div style="margin-bottom: 20px">
            <p>Successfully imported "{work_title}" by {author_name}.</p>
        </div>
        <div>
            <a href="/import" style="color: #4CAF50; text-decoration: none">Import Another Text</a>
            <span style="margin: 0 10px">|</span>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """


def render_import_error_page(error_message: str) -> str:
    """Return HTML for the import error page.

    Args:
        error_message: The error message to display
    """
    return f"""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 5px">
        <h2>Import Error</h2>
        <div style="margin-bottom: 20px">
            <p style="color: #dc3545">{error_message}</p>
        </div>
        <div>
            <a href="/import" style="color: #4CAF50; text-decoration: none">Try Again</a>
            <span style="margin: 0 10px">|</span>
            <a href="/" style="color: #4CAF50; text-decoration: none">Return to Home</a>
        </div>
    </div>
    """
