#!/usr/bin/env python3
"""Simple performance tests for First1KGreek Browser."""

import unittest
import os
import sys
import time
import tempfile
import xml.etree.ElementTree as ET


def generate_large_xml(file_path, num_divisions=100, num_paragraphs=10):
    """Generate a large XML file for performance testing."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n')
        f.write('  <teiHeader>\n')
        f.write('    <fileDesc>\n')
        f.write('      <titleStmt>\n')
        f.write('        <title>Performance Test</title>\n')
        f.write('        <author>Test Author</author>\n')
        f.write('      </titleStmt>\n')
        f.write('    </fileDesc>\n')
        f.write('  </teiHeader>\n')
        f.write('  <text>\n')
        f.write('    <body>\n')
        
        # Generate specified number of divisions
        for div_num in range(1, num_divisions + 1):
            f.write(f'      <div type="textpart" subtype="book" n="{div_num}">\n')
            for p_num in range(1, num_paragraphs + 1):
                f.write(f'        <p>This is paragraph {p_num} in division {div_num}. ')
                # Add some Greek text
                f.write(f'Here is Greek text: <foreign xml:lang="grc">λόγος καὶ φύσις</foreign>. ')
                # Add notes and other elements
                f.write(f'<note>Note {div_num}.{p_num}</note> ')
                if p_num % 3 == 0:
                    f.write('<quote>Quoted text</quote> ')
                f.write('</p>\n')
            f.write('      </div>\n')
        
        f.write('    </body>\n')
        f.write('  </text>\n')
        f.write('</TEI>')


def process_xml_for_reading(element, processed_text=''):
    """Process XML for reading, simplified version for testing."""
    if element.tag.endswith('}p'):
        processed_text += "".join(element.itertext()) + "\n\n"
    elif element.tag.endswith('}quote'):
        processed_text += "QUOTE: " + "".join(element.itertext()) + "\n\n"
    elif element.tag.endswith('}note'):
        # Skip notes in output
        pass
    
    for child in element:
        processed_text = process_xml_for_reading(child, processed_text)
        
    return processed_text


class SimplePerformanceTest(unittest.TestCase):
    """Simple performance test case."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create temporary directory
        cls.test_dir = tempfile.mkdtemp()
        
        # Create test files of different sizes
        cls.small_xml = os.path.join(cls.test_dir, 'small.xml')
        cls.medium_xml = os.path.join(cls.test_dir, 'medium.xml')
        cls.large_xml = os.path.join(cls.test_dir, 'large.xml')
        
        generate_large_xml(cls.small_xml, num_divisions=10, num_paragraphs=5)
        generate_large_xml(cls.medium_xml, num_divisions=50, num_paragraphs=10)
        generate_large_xml(cls.large_xml, num_divisions=100, num_paragraphs=20)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(cls.test_dir)
    
    def test_parse_small_xml(self):
        """Test parsing performance for small XML file."""
        start_time = time.time()
        tree = ET.parse(self.small_xml)
        root = tree.getroot()
        parse_time = time.time() - start_time
        
        print(f"Small XML parse time: {parse_time:.3f} seconds")
        self.assertLess(parse_time, 1.0)  # Should parse in less than 1 second
    
    def test_parse_medium_xml(self):
        """Test parsing performance for medium XML file."""
        start_time = time.time()
        tree = ET.parse(self.medium_xml)
        root = tree.getroot()
        parse_time = time.time() - start_time
        
        print(f"Medium XML parse time: {parse_time:.3f} seconds")
        self.assertLess(parse_time, 2.0)  # Should parse in less than 2 seconds
    
    def test_parse_large_xml(self):
        """Test parsing performance for large XML file."""
        start_time = time.time()
        tree = ET.parse(self.large_xml)
        root = tree.getroot()
        parse_time = time.time() - start_time
        
        print(f"Large XML parse time: {parse_time:.3f} seconds")
        self.assertLess(parse_time, 5.0)  # Should parse in less than 5 seconds
    
    def test_process_large_xml(self):
        """Test processing performance for large XML file."""
        tree = ET.parse(self.large_xml)
        root = tree.getroot()
        
        start_time = time.time()
        result = process_xml_for_reading(root)
        process_time = time.time() - start_time
        
        print(f"Large XML processing time: {process_time:.3f} seconds")
        print(f"Processed text length: {len(result)} characters")
        self.assertLess(process_time, 5.0)  # Should process in less than 5 seconds


if __name__ == '__main__':
    unittest.main(verbosity=2) 