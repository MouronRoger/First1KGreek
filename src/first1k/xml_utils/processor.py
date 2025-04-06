"""XML processing utilities for First1KGreek Browser."""

import re
import xml.etree.ElementTree as ET
from html import escape


def process_xml_for_reading(xml_content):
    """Process XML content for reader-friendly display using structured XML parsing."""
    try:
        # Clean up XML namespaces for easier parsing
        xml_content = re.sub(r'xmlns="[^"]*"', "", xml_content)
        xml_content = re.sub(r'xmlns:[^=]*="[^"]*"', "", xml_content)

        # Remove XML declaration
        xml_content = re.sub(r"<\?xml[^>]*\?>", "", xml_content)

        # Prefix all tags to create a simplified pseudo-namespace
        xml_content = re.sub(r"<([/]?)([a-zA-Z0-9_\-]+):", r"<\1tei_\2", xml_content)

        # Wrap in a root element if needed
        if not xml_content.strip().startswith("<"):
            xml_content = f"<root>{xml_content}</root>"

        # Parse the XML
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return fallback_xml_rendering(xml_content)

        # Start building the HTML output
        html_output = []

        # Process revision description
        revision_desc = root.find(".//revisionDesc") or root.find(".//tei_revisionDesc")
        if revision_desc is not None:
            html_output.append('<div class="revision-history"><h3>Revision History</h3><ul>')
            changes = revision_desc.findall(".//change") or revision_desc.findall(".//tei_change")
            for change in changes:
                date = change.get("when", "")
                person = change.get("who", "")
                desc = "".join(change.itertext()).strip()
                html_output.append(f"<li><strong>{date}</strong> by <em>{person}</em>: {desc}</li>")
            html_output.append("</ul></div>")

        # Process edition information
        edition_div = root.find('.//div[@type="edition"]') or root.find('.//tei_div[@type="edition"]')
        if edition_div is not None:
            edition_id = edition_div.get("n", "")
            edition_lang = edition_div.get("xml:lang", "") or edition_div.get("lang", "")
            if edition_id:
                html_output.append(f'<div class="edition-info">Edition: {edition_id} (Language: {edition_lang})</div>')

        # Process fragments
        fragments = root.findall('.//div[@type="textpart"][@subtype="fragment"]') or root.findall(
            './/tei_div[@type="textpart"][@subtype="fragment"]'
        )

        if fragments:
            html_output.append('<div class="fragments-container">')
            for fragment in fragments:
                fragment_num = fragment.get("n", "Unknown")
                html_output.append('<div class="fragment">')
                html_output.append(f'<div class="fragment-number">Fragment {fragment_num}</div>')
                html_output.append('<div class="greek-text">')

                # Process paragraphs within the fragment
                paragraphs = fragment.findall(".//p") or fragment.findall(".//tei_p")

                for p in paragraphs:
                    html_output.append('<div class="paragraph">')
                    paragraph_parts = []
                    if p.text:
                        paragraph_parts.append(p.text)

                    for child in p:
                        if child.tag.endswith("name") or child.tag.endswith("placeName"):
                            if child.text:
                                paragraph_parts.append(f'<span class="name">{child.text}</span>')
                        elif child.tag.endswith("foreign"):
                            lang = child.get("xml:lang", "")
                            if child.text:
                                paragraph_parts.append(f'<span class="foreign" lang="{lang}">{child.text}</span>')
                        else:
                            if child.text:
                                paragraph_parts.append(child.text)

                        if child.tail:
                            paragraph_parts.append(child.tail)

                    paragraph_text = " ".join(paragraph_parts).strip()
                    if paragraph_text:
                        html_output.append(paragraph_text)

                    html_output.append("</div>")  # Close paragraph

                html_output.append("</div>")  # Close greek-text
                html_output.append("</div>")  # Close fragment

            html_output.append("</div>")  # Close fragments-container
            return "\n".join(html_output)

        # If no fragments, try to extract the full text
        body = root.find(".//body") or root.find(".//tei_body")
        if body is not None:
            html_output.append('<div class="main-content">')

            # Process all text elements
            text_elements = body.findall(".//*")
            for elem in text_elements:
                tag = elem.tag
                elem_text = elem.text or ""

                if tag.endswith("p") or tag.endswith("tei_p"):
                    html_output.append(f"<p>{elem_text}</p>")
                elif tag.endswith("head") or tag.endswith("tei_head"):
                    html_output.append(f'<h2 class="section-head">{elem_text}</h2>')
                elif tag.endswith("quote") or tag.endswith("tei_quote"):
                    html_output.append(f'<blockquote class="quote">{elem_text}</blockquote>')
                elif tag.endswith("foreign") or tag.endswith("tei_foreign"):
                    lang = elem.get("xml:lang", "")
                    html_output.append(f'<span class="foreign" lang="{lang}">{elem_text}</span>')

            html_output.append("</div>")  # Close main-content

        return "\n".join(html_output)

    except Exception as e:
        import traceback

        print(f"Error processing XML: {str(e)}")
        print(traceback.format_exc())
        return fallback_xml_rendering(xml_content)


def fallback_xml_rendering(xml_content):
    """Fallback rendering when XML parsing fails."""
    clean_content = escape(xml_content)
    html = f"""
    <div class="xml-content">
        <pre style="white-space: pre-wrap; font-family: monospace; line-height: 1.4; padding: 15px; background-color: #2d2d2d; color: #f8f8f8; border: 1px solid #444; border-radius: 5px; overflow-x: auto;">{clean_content}</pre>
    </div>
    """
    return html


def extract_title_from_xml(xml_content):
    """Extract the title from the XML content."""
    try:
        root = ET.fromstring(xml_content)
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
        for elem in root.findall(".//*[@xml:lang]", {"xml": "http://www.w3.org/XML/1998/namespace"}):
            lang = elem.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang:
                return lang
        return "grc"  # Default to Greek for most First1K texts
    except Exception as e:
        print(f"Warning: Could not detect language from XML: {str(e)}")
        return "grc"
