"""Scaife import/export functionality for First1KGreek Browser."""

import json
import os
import re
import traceback
import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError

from ..xml_utils.processor import detect_language_from_xml, extract_title_from_xml


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
        except:
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
            except:
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

    # Update the catalog.json (if it exists)
    try:
        update_catalog(author_id, work_id, edition_id, author_name, work_title)
    except Exception as e:
        print(f"Warning: Could not update catalog.json: {str(e)}")

    return f"Imported {work_title} by {author_name} ({full_id})"


def update_catalog(author_id, work_id, edition_id, author_name, work_title):
    """Update the catalog.json file with the new text."""
    catalog_path = "catalog.json"
    if not os.path.exists(catalog_path):
        return  # Skip if catalog doesn't exist

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_data = f.read()
            catalog = json.loads(catalog_data)

        # Check if entry already exists
        full_id = f"{author_id}.{work_id}.{edition_id}"
        urn = f"urn:cts:greekLit:{full_id}"

        # Check if the entry already exists
        for entry in catalog:
            if isinstance(entry, dict) and entry.get("urn") == urn:
                return  # Already exists

        # Add new entry
        new_entry = {
            "urn": urn,
            "group_name": author_name,
            "work_name": work_title,
            "language": "grc",  # Default
            "scaife": f"https://scaife.perseus.org/reader/{urn}:1",
        }

        catalog.append(new_entry)

        # Save updated catalog
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2)

        print(f"Updated catalog.json with {full_id}")
    except Exception as e:
        print(f"Error updating catalog: {str(e)}")
        traceback.print_exc()
        raise


def get_author_name_from_files(author_id):
    """Get author name from existing files."""
    author_path = os.path.join("data", author_id)
    if not os.path.exists(author_path):
        return None

    # Check a few files to find the author name
    for work_dir in os.listdir(author_path):
        work_path = os.path.join(author_path, work_dir)
        if os.path.isdir(work_path):
            for file in os.listdir(work_path):
                if file.endswith(".xml") and not file == "__cts__.xml":
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(10000)  # Just read the beginning where metadata usually is

                        # Look for author tag with reasonable content
                        author_matches = re.findall(r"<author[^>]*>(.*?)</author>", content)
                        if author_matches and len(author_matches[0].strip()) > 0:
                            return author_matches[0].strip()

                    except Exception as e:
                        pass

    return None


def get_author_name_from_id(author_id):
    """Get author name from ID using various methods."""
    # Try to get from existing files
    try:
        return get_author_name_from_files(author_id)
    except:
        # Map common author IDs to names
        author_map = {
            "tlg0001": "Thucydides",
            "tlg0003": "Herodotus",
            "tlg0004": "Diogenes Laertius",
            "tlg0007": "Plutarch",
            "tlg0012": "Homer",
            "tlg0059": "Plato",
            "tlg0086": "Aristotle",
            # Add more as needed
        }
        return author_map.get(author_id)
