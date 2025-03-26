"""Import handlers for First1KGreek Browser."""

import os
import re
import xml.etree.ElementTree as ET
import urllib.request
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from ..config import MAIN_STYLESHEET

def import_text_from_scaife(scaife_url, provided_author_name='', provided_work_title=''):
    """Import text from Scaife URL and save to the corpus."""
    print(f"Importing from URL: {scaife_url}")
    
    # Extract URN from URL
    urn_match = re.search(r'urn:cts:greekLit:([^:]+)\.([^:]+)\.([^:/]+)', scaife_url)
    if not urn_match:
        raise ValueError("Invalid Scaife URL format - could not extract URN")
    
    author_id = urn_match.group(1)  # e.g., tlg0007
    work_id = urn_match.group(2)    # e.g., tlg136
    edition_id = urn_match.group(3) # e.g., perseus-grc2
    
    # Create full id for file
    full_id = f"{author_id}.{work_id}.{edition_id}"
    
    # Create directory structure
    author_dir = os.path.join('data', author_id)
    work_dir = os.path.join(author_dir, work_id)
    
    os.makedirs(work_dir, exist_ok=True)
    
    # Fetch XML content from Scaife
    try:
        response = urllib.request.urlopen(scaife_url)
        xml_content = response.read().decode('utf-8')
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
                existing_cts_path = os.path.join(work_dir, '__cts__.xml')
                if os.path.exists(existing_cts_path):
                    tree = ET.parse(existing_cts_path)
                    title_elem = tree.find('.//{*}title')
                    if title_elem is not None and title_elem.text:
                        work_title = title_elem.text
            except:
                pass
    
    if not work_title:
        work_title = f"Work {work_id}"
    
    # Create author metadata file if it doesn't exist
    author_cts_path = os.path.join(author_dir, '__cts__.xml')
    if not os.path.exists(author_cts_path):
        author_cts_content = f"""<ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:greekLit:{author_id}">
    <ti:groupname xml:lang="eng">{author_name}</ti:groupname>
</ti:textgroup>"""
        with open(author_cts_path, 'w', encoding='utf-8') as f:
            f.write(author_cts_content)
        print(f"Created author metadata: {author_cts_path}")
    
    # Create work metadata file if it doesn't exist
    work_cts_path = os.path.join(work_dir, '__cts__.xml')
    if not os.path.exists(work_cts_path):
        language = detect_language_from_xml(xml_content) or "grc"
        work_cts_content = f"""<ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" groupUrn="urn:cts:greekLit:{author_id}" xml:lang="{language}" urn="urn:cts:greekLit:{author_id}.{work_id}">
    <ti:title xml:lang="eng">{work_title}</ti:title>
    <ti:edition urn="urn:cts:greekLit:{full_id}" workUrn="urn:cts:greekLit:{author_id}.{work_id}" xml:lang="{language}">
        <ti:label xml:lang="eng">{work_title}</ti:label>
        <ti:description xml:lang="eng">Imported from Scaife/Perseus</ti:description>
    </ti:edition>
</ti:work>"""
        with open(work_cts_path, 'w', encoding='utf-8') as f:
            f.write(work_cts_content)
        print(f"Created work metadata: {work_cts_path}")
    
    # Save the XML content to file
    text_file_path = os.path.join(work_dir, f"{full_id}.xml")
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"Saved text file: {text_file_path}")
    
    return f"Imported {work_title} by {author_name} ({full_id})"

def get_author_name_from_files(author_id):
    """Attempt to find an author name from XML files."""
    author_path = os.path.join('data', author_id)
    if not os.path.exists(author_path):
        return None
        
    # Check files to find the author name
    for work_dir in os.listdir(author_path):
        work_path = os.path.join(author_path, work_dir)
        if os.path.isdir(work_path):
            for file in os.listdir(work_path):
                if file.endswith('.xml') and not file == '__cts__.xml':
                    file_path = os.path.join(work_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(10000)  # Read beginning where metadata usually is
                            
                        # Look for author tag with reasonable content
                        author_matches = re.findall(r'<author[^>]*>(.*?)</author>', content)
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
        for title_tag in root.findall('.//{*}title'):
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
        for elem in root.findall('.//*[@xml:lang]', {'xml': 'http://www.w3.org/XML/1998/namespace'}):
            lang = elem.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang:
                return lang
        # Default to Greek for most First1K texts
        return "grc"
    except Exception as e:
        print(f"Warning: Could not detect language from XML: {str(e)}")
        return "grc"

def render_import_page():
    """Return the import page HTML."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Import Texts from Scaife</title>
    <style>
        {MAIN_STYLESHEET}
        .tabs {{
            display: flex;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            background: #2a4365;
            color: white;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
            margin-right: 2px;
        }}
        .tab.active {{
            background: #3182ce;
        }}
        .tab-content {{
            display: none;
            padding: 20px;
            background: #2a4365;
            border-radius: 0 4px 4px 4px;
        }}
        .tab-content.active {{
            display: block;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        textarea, input[type="text"] {{
            width: 100%;
            padding: 10px;
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #333;
            color: white;
            font-family: monospace;
        }}
        button {{
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background: #3182ce;
        }}
        .info-box {{
            background-color: #2a4365;
            border-left: 5px solid #4299e1;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .metadata-fields {{
            background: #2d3748;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }}
    </style>
    <script>
        function showTab(tabId) {{
            var contents = document.querySelectorAll(".tab-content");
            for (var i = 0; i < contents.length; i++) {{
                contents[i].classList.remove("active");
            }}
            var tabs = document.querySelectorAll(".tab");
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove("active");
            }}
            document.getElementById(tabId + "-tab").classList.add("active");
            var tabs = document.querySelectorAll(".tab");
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].innerText.toLowerCase().indexOf(tabId) !== -1) {{
                    tabs[i].classList.add("active");
                }}
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Import Texts from Scaife/Perseus</h1>
        
        <div class="info-box">
            <p><strong>Instructions:</strong> Enter one or more Scaife API XML URLs to import texts into the First1KGreek corpus.</p>
            <p>Use the format: <code>https://scaife.perseus.org/library/urn:cts:greekLit:tlg0007.tlg136.perseus-grc2:1-47/cts-api-xml/</code></p>
            <p>You can add metadata for each URL to improve import quality.</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('single')">Single URL</div>
            <div class="tab" onclick="showTab('batch')">Batch Import</div>
        </div>
        
        <div id="single-tab" class="tab-content active">
            <form action="/import_text" method="post">
                <div class="form-group">
                    <label>Scaife URL:</label>
                    <input type="text" name="scaife_url" placeholder="https://scaife.perseus.org/library/urn:cts:greekLit:tlg0007.tlg136.perseus-grc2:1-47/cts-api-xml/">
                </div>
                
                <div class="metadata-fields">
                    <h3>Metadata (Optional)</h3>
                    <div class="form-group">
                        <label>Author Name:</label>
                        <input type="text" name="author_name" placeholder="e.g., Plutarch">
                    </div>
                    <div class="form-group">
                        <label>Work Title:</label>
                        <input type="text" name="work_title" placeholder="e.g., De Stoicorum Repugnantiis">
                    </div>
                </div>
                
                <input type="hidden" name="import_type" value="single">
                <button type="submit">Import Text</button>
            </form>
        </div>
        
        <div id="batch-tab" class="tab-content">
            <form action="/import_text" method="post">
                <div class="form-group">
                    <label>Scaife URLs (one per line):</label>
                    <textarea name="scaife_urls" rows="10" placeholder="https://scaife.perseus.org/library/urn:cts:greekLit:tlg0007.tlg136.perseus-grc2:1-47/cts-api-xml/
https://scaife.perseus.org/library/urn:cts:greekLit:tlg0007.tlg137.perseus-grc2:1-6/cts-api-xml/
https://scaife.perseus.org/library/urn:cts:greekLit:tlg0007.tlg138.perseus-grc2:1-50/cts-api-xml/"></textarea>
                </div>
                
                <div class="metadata-fields">
                    <h3>Default Metadata (Optional)</h3>
                    <p>This metadata will be used for all imported texts if their data cannot be detected automatically.</p>
                    <div class="form-group">
                        <label>Default Author Name:</label>
                        <input type="text" name="default_author_name" placeholder="e.g., Plutarch">
                    </div>
                </div>
                
                <input type="hidden" name="import_type" value="batch">
                <button type="submit">Import Texts</button>
            </form>
        </div>
    </div>
</body>
</html>"""
    return html

def render_import_success_page(message):
    """Return the import success page HTML."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Import Success</title>
    <style>
        {MAIN_STYLESHEET}
        .success-box {{
            background-color: #2c4a2c;
            border-left: 5px solid #48bb78;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .nav-links {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #444;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
        }}
        .button:hover {{
            background: #3182ce;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Import Successful</h1>
        
        <div class="success-box">
            <p>{message}</p>
        </div>
        
        <div class="nav-links">
            <a href="/import" class="button">Back to Import</a>
            <a href="/" class="button">Home</a>
        </div>
    </div>
</body>
</html>"""
    return html

def render_import_error_page(error):
    """Return the import error page HTML."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Import Error</title>
    <style>
        {MAIN_STYLESHEET}
        .error-box {{
            background-color: #4a2c2c;
            border-left: 5px solid #f56565;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .nav-links {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #444;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
        }}
        .button:hover {{
            background: #3182ce;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Import Error</h1>
        
        <div class="error-box">
            <p>{error}</p>
        </div>
        
        <div class="nav-links">
            <a href="/import" class="button">Back to Import</a>
            <a href="/" class="button">Home</a>
        </div>
    </div>
</body>
</html>"""
    return html 