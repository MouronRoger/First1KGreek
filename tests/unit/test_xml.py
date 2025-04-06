#!/usr/bin/env python3
"""Simple XML parsing tests for First1KGreek Browser."""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET


class SimpleXMLTest(unittest.TestCase):
    """Simple test case for XML parsing."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create a test XML file
        self.test_xml = os.path.join(self.test_dir, "test.xml")
        with open(self.test_xml, "w", encoding="utf-8") as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Test Title</title>
        <author>Test Author</author>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <div type="textpart" subtype="chapter" n="1">
        <p>This is test content with Greek: <foreign xml:lang="grc">δοκιμή</foreign></p>
      </div>
    </body>
  </text>
</TEI>"""
            )

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_parse_xml(self):
        """Test basic XML parsing."""
        tree = ET.parse(self.test_xml)
        root = tree.getroot()

        # Check the root element
        self.assertEqual(root.tag, "{http://www.tei-c.org/ns/1.0}TEI")

        # Get all text content
        text_content = "".join(root.itertext())

        # Check that content includes expected text
        self.assertIn("Test Title", text_content)
        self.assertIn("Test Author", text_content)
        self.assertIn("This is test content with Greek", text_content)
        self.assertIn("δοκιμή", text_content)

    def test_extract_elements(self):
        """Test extracting specific elements."""
        tree = ET.parse(self.test_xml)
        root = tree.getroot()

        # Define namespace mapping
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Find title
        title = root.find(".//tei:title", ns)
        self.assertIsNotNone(title)
        self.assertEqual(title.text, "Test Title")

        # Find author
        author = root.find(".//tei:author", ns)
        self.assertIsNotNone(author)
        self.assertEqual(author.text, "Test Author")

        # Find paragraph
        p = root.find(".//tei:p", ns)
        self.assertIsNotNone(p)
        self.assertIn("This is test content with Greek", p.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
