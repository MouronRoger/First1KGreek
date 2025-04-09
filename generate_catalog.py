#!/usr/bin/env python3
"""
Generate a catalog of XML documents in the First1KGreek repository.

This script scans all XML files in the data and split directories and extracts metadata
to create a comprehensive catalog in CSV format.
"""

import os
import sys
import csv
import xml.etree.ElementTree as ET
import re
from pathlib import Path


# Register the TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def extract_language_from_filename(filename):
    """
    Extract language code from filename.
    
    Examples:
    - tlg0057.tlg001.1st1K-grc1.xml -> 'Greek'
    - tlg0527.tlg048.opp-eng2.xml -> 'English'
    """
    lang_match = re.search(r'-(grc|eng|lat|ger)(\d+)?\.xml$', filename)
    if lang_match:
        lang_code = lang_match.group(1)
        lang_map = {
            'grc': 'Greek',
            'eng': 'English',
            'lat': 'Latin',
            'ger': 'German'
        }
        return lang_map.get(lang_code, lang_code)
    return "Unknown"


def extract_language_from_xml(root):
    """Extract language from XML content."""
    # Try to get the language from the profileDesc/langUsage/language element
    lang_element = root.find('.//tei:profileDesc//tei:language', NS)
    if lang_element is not None:
        lang_ident = lang_element.get('ident')
        if lang_ident:
            lang_map = {
                'grc': 'Greek',
                'eng': 'English',
                'lat': 'Latin',
                'ger': 'German'
            }
            return lang_map.get(lang_ident, lang_ident)
            
    # Try to get the language from the div element's xml:lang attribute
    div_element = root.find('.//tei:div[@type="edition"]', NS)
    if div_element is not None:
        lang = div_element.get('{http://www.w3.org/XML/1998/namespace}lang')
        if lang:
            lang_map = {
                'grc': 'Greek',
                'eng': 'English',
                'lat': 'Latin',
                'ger': 'German'
            }
            return lang_map.get(lang, lang)
    
    return "Unknown"


def extract_metadata(xml_path, source_dir):
    """
    Extract metadata from an XML file.
    
    Args:
        xml_path: Path to the XML file
        source_dir: Source directory (data or split)
        
    Returns:
        dict: Dictionary with metadata fields
    """
    filename = os.path.basename(xml_path)
    file_size = os.path.getsize(xml_path)
    location = os.path.dirname(xml_path)
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Extract URN
        urn = ""
        div_element = root.find('.//tei:div[@type="edition"]', NS)
        if div_element is not None:
            urn = div_element.get('n', "")
        
        # Extract title
        title = ""
        title_element = root.find('.//tei:titleStmt/tei:title', NS)
        if title_element is not None:
            title = title_element.text
        
        # Extract author
        author = ""
        author_element = root.find('.//tei:titleStmt/tei:author', NS)
        if author_element is not None:
            author = author_element.text
        
        # Extract editor
        editor = ""
        editor_element = root.find('.//tei:titleStmt/tei:editor', NS)
        if editor_element is not None:
            editor = editor_element.text
        
        # Extract publisher
        publisher = ""
        publisher_element = root.find('.//tei:sourceDesc//tei:publisher', NS)
        if publisher_element is not None:
            publisher = publisher_element.text
        
        # Extract publication year
        pub_year = ""
        date_element = root.find('.//tei:sourceDesc//tei:date', NS)
        if date_element is not None:
            pub_year = date_element.text
        
        # Extract language
        language = extract_language_from_xml(root)
        if language == "Unknown":
            language = extract_language_from_filename(filename)
        
        return {
            "Filename": filename,
            "URN": urn,
            "Title": title,
            "Author": author,
            "Editor": editor,
            "Publisher": publisher,
            "Publication Year": pub_year,
            "Language": language,
            "Size": file_size,
            "Location": location,
            "Source": source_dir
        }
    
    except Exception as e:
        print(f"Error processing {xml_path}: {e}", file=sys.stderr)
        return {
            "Filename": filename,
            "URN": "",
            "Title": "",
            "Author": "",
            "Editor": "",
            "Publisher": "",
            "Publication Year": "",
            "Language": extract_language_from_filename(filename),
            "Size": file_size,
            "Location": location,
            "Source": source_dir
        }


def find_xml_files(base_dir):
    """
    Find all XML files in the given directory recursively.
    
    Args:
        base_dir: Base directory to search
        
    Returns:
        list: List of full paths to XML files
    """
    xml_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.xml') and not file == '__cts__.xml':
                xml_files.append(os.path.join(root, file))
    return xml_files


def main():
    """Generate a catalog of XML files in the repository."""
    data_dirs = ["data", "split"]
    output_file = "catalog.csv"
    
    all_xml_files = []
    
    # Find all XML files in both directories
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            print(f"Scanning for XML files in {data_dir}...")
            xml_files = find_xml_files(data_dir)
            print(f"Found {len(xml_files)} XML files in {data_dir}")
            all_xml_files.extend([(xml_file, data_dir) for xml_file in xml_files])
        else:
            print(f"Directory {data_dir} not found, skipping...")
    
    # Process each file
    print("Extracting metadata...")
    metadata_list = []
    for xml_file, source_dir in all_xml_files:
        metadata = extract_metadata(xml_file, source_dir)
        metadata_list.append(metadata)
    
    # Write to CSV
    print(f"Writing data to {output_file}...")
    fieldnames = [
        "Filename", "URN", "Title", "Author", "Editor", 
        "Publisher", "Publication Year", "Language", "Size", "Location", "Source"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)
    
    print(f"Catalog generation complete: {len(metadata_list)} entries written to {output_file}")


if __name__ == "__main__":
    main() 