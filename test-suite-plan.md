# First1KGreek Test Suite Implementation Plan

## 1. Test Environment Setup

```python
# test_environment.py
import unittest
import os
import sys
import tempfile
import shutil
from http.server import HTTPServer
from threading import Thread

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import main application components
# Note: Paths may need adjustment based on actual project structure
from browse_texts_fixed import CustomHTTPRequestHandler, run_server

class TestEnvironment:
    """Base class for setting up test environment"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment including temporary directories and test server"""
        # Create temporary directory for test data
        cls.test_dir = tempfile.mkdtemp()
        cls.test_data_dir = os.path.join(cls.test_dir, 'data')
        os.mkdir(cls.test_data_dir)

        # Copy minimal sample data for testing
        cls.setup_sample_data()

        # Start test server in a separate thread
        cls.server_thread = Thread(target=cls.run_test_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(cls.test_dir)

        # Server thread is daemon, so it will terminate with the main thread

    @classmethod
    def setup_sample_data(cls):
        """Set up minimal sample data for testing"""
        # Create sample XML files with minimal structure for testing
        # This will vary based on the actual XML structure used in the project
        pass

    @classmethod
    def run_test_server(cls):
        """Run test server on a different port from the main application"""
        # Set up and run the server for testing
        server_address = ('', 8001)  # Use different port from main app
        httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
        httpd.serve_forever()
```

## 2. Unit Tests

### 2.1 XML Processing Tests

```python
# test_xml_processing.py
import unittest
import xml.etree.ElementTree as ET
from test_environment import TestEnvironment

# Import functions to test
from browse_texts_fixed import process_xml_for_reading  # Adjust import path as needed

class XMLProcessingTests(unittest.TestCase, TestEnvironment):
    """Test XML processing functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        TestEnvironment.setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    def test_process_xml_basic(self):
        """Test basic XML processing"""
        sample_xml = '<TEI><text><body><p>Sample Greek text: <foreign xml:lang="grc">λόγος</foreign></p></body></text></TEI>'
        root = ET.fromstring(sample_xml)
        result = process_xml_for_reading(root)
        self.assertIn('Sample Greek text:', result)
        self.assertIn('λόγος', result)

    def test_process_xml_nested(self):
        """Test processing nested XML elements"""
        sample_xml = '<TEI><text><body><div><p>Outer text <div><p>Inner text <foreign xml:lang="grc">φύσις</foreign></p></div></p></div></body></text></TEI>'
        root = ET.fromstring(sample_xml)
        result = process_xml_for_reading(root)
        self.assertIn('Outer text', result)
        self.assertIn('Inner text', result)
        self.assertIn('φύσις', result)
```

### 2.2 Metadata Extraction Tests

```python
# test_metadata.py
import unittest
import os
import xml.etree.ElementTree as ET
from test_environment import TestEnvironment

# Import functions to test
from browse_texts_fixed import get_author_name_from_files  # Adjust import path as needed

class MetadataTests(unittest.TestCase, TestEnvironment):
    """Test metadata extraction functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        TestEnvironment.setUpClass()

        # Create a test XML file with author metadata
        cls.test_xml_path = os.path.join(cls.test_data_dir, 'test_author.xml')
        with open(cls.test_xml_path, 'w', encoding='utf-8') as f:
            f.write('<TEI><teiHeader><fileDesc><titleStmt><author>Test Author</author></titleStmt></fileDesc></teiHeader></TEI>')

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    def test_get_author_name(self):
        """Test extracting author name from XML file"""
        result = get_author_name_from_files([self.test_xml_path])
        self.assertEqual(result, 'Test Author')

    def test_get_author_name_multiple_files(self):
        """Test extracting author name from multiple XML files (should use first one)"""
        # Create a second test file
        second_xml_path = os.path.join(self.test_data_dir, 'test_author2.xml')
        with open(second_xml_path, 'w', encoding='utf-8') as f:
            f.write('<TEI><teiHeader><fileDesc><titleStmt><author>Another Author</author></titleStmt></fileDesc></teiHeader></TEI>')

        result = get_author_name_from_files([self.test_xml_path, second_xml_path])
        self.assertEqual(result, 'Test Author')
```

### 2.3 Import Functionality Tests

```python
# test_import.py
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from test_environment import TestEnvironment

# Import functions to test
from browse_texts_fixed import import_text_from_scaife  # Adjust import path as needed

class ImportTests(unittest.TestCase, TestEnvironment):
    """Test import functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        TestEnvironment.setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    @patch('browse_texts_fixed.requests.get')
    def test_import_single_text(self, mock_get):
        """Test importing a single text from Scaife/Perseus"""
        # Mock response from Scaife/Perseus
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<TEI><teiHeader><fileDesc><titleStmt><title>Test Work</title><author>Test Author</author></titleStmt></fileDesc></teiHeader><text><body><p>Test content</p></body></text></TEI>'
        mock_get.return_value = mock_response

        # Call import function
        result = import_text_from_scaife('urn:cts:test:test.work', self.test_data_dir)

        # Assert expected behavior
        self.assertTrue(result)  # Import should succeed
        # Check that file was created with correct content
        expected_path = os.path.join(self.test_data_dir, 'test', 'test.work.xml')
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<title>Test Work</title>', content)
            self.assertIn('<author>Test Author</author>', content)
            self.assertIn('<p>Test content</p>', content)
```

## 3. Integration Tests

```python
# test_integration.py
import unittest
import requests
import time
from test_environment import TestEnvironment

class IntegrationTests(unittest.TestCase, TestEnvironment):
    """Integration tests for the application"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment including test server"""
        TestEnvironment.setUpClass()
        # Give the server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    def test_home_page(self):
        """Test that home page loads successfully"""
        response = requests.get('http://localhost:8001/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('First1KGreek Browser', response.text)

    def test_authors_page(self):
        """Test that authors page loads successfully"""
        response = requests.get('http://localhost:8001/authors')
        self.assertEqual(response.status_code, 200)
        # Additional assertions based on expected content

    def test_works_page(self):
        """Test that works page loads for a sample author"""
        # This will need to be adjusted based on how author IDs are structured
        response = requests.get('http://localhost:8001/works?author=test_author')
        self.assertEqual(response.status_code, 200)
        # Additional assertions based on expected content
```

## 4. End-to-End Tests

```python
# test_e2e.py
import unittest
import requests
import time
from test_environment import TestEnvironment

class EndToEndTests(unittest.TestCase, TestEnvironment):
    """End-to-end tests for complete workflows"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment including test server"""
        TestEnvironment.setUpClass()
        # Give the server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    def test_browse_and_read(self):
        """Test complete workflow: browse authors, select work, view text"""
        # Step 1: Get authors list
        response = requests.get('http://localhost:8001/authors')
        self.assertEqual(response.status_code, 200)

        # Step 2: Select an author (will need to extract author ID from response)
        # For test purposes, we'll use a hardcoded author ID
        author_id = 'test_author'
        response = requests.get(f'http://localhost:8001/works?author={author_id}')
        self.assertEqual(response.status_code, 200)

        # Step 3: Select a work (will need to extract work ID from response)
        # For test purposes, we'll use a hardcoded work ID
        work_id = 'test_work'
        response = requests.get(f'http://localhost:8001/read?author={author_id}&work={work_id}')
        self.assertEqual(response.status_code, 200)
        # Check for expected content in reader
        self.assertIn('Test content', response.text)

    def test_import_and_read(self):
        """Test complete workflow: import text, browse to it, view it"""
        # Step 1: Import a text
        urn = 'urn:cts:test:test.import_work'
        response = requests.post('http://localhost:8001/import', data={'urn': urn})
        self.assertEqual(response.status_code, 200)

        # Step 2: Browse to imported text
        author_id = 'test'  # Based on URN
        response = requests.get(f'http://localhost:8001/works?author={author_id}')
        self.assertEqual(response.status_code, 200)

        # Step 3: View imported text
        work_id = 'test.import_work'  # Based on URN
        response = requests.get(f'http://localhost:8001/read?author={author_id}&work={work_id}')
        self.assertEqual(response.status_code, 200)
        # Additional assertions based on expected content
```

## 5. Performance Tests

```python
# test_performance.py
import unittest
import time
import requests
from test_environment import TestEnvironment

class PerformanceTests(unittest.TestCase, TestEnvironment):
    """Performance tests for the application"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment including test server"""
        TestEnvironment.setUpClass()
        # Give the server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        TestEnvironment.tearDownClass()

    def test_home_page_load_time(self):
        """Test home page load time"""
        start_time = time.time()
        response = requests.get('http://localhost:8001/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        print(f"Home page load time: {load_time:.2f} seconds")
        # Threshold depends on what's reasonable for your application
        self.assertLess(load_time, 1.0)  # Should load in less than 1 second

    def test_xml_processing_time(self):
        """Test XML processing time for a large document"""
        # This would require setting up a large test document
        # and measuring the time to process it
        pass
```

## 6. Test Runner

```python
# run_tests.py
import unittest
import sys

# Import test modules
from test_xml_processing import XMLProcessingTests
from test_metadata import MetadataTests
from test_import import ImportTests
from test_integration import IntegrationTests
from test_e2e import EndToEndTests
from test_performance import PerformanceTests

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(XMLProcessingTests))
    test_suite.addTest(unittest.makeSuite(MetadataTests))
    test_suite.addTest(unittest.makeSuite(ImportTests))
    test_suite.addTest(unittest.makeSuite(IntegrationTests))
    test_suite.addTest(unittest.makeSuite(EndToEndTests))
    test_suite.addTest(unittest.makeSuite(PerformanceTests))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
```

## 7. Setup File for Test Suite

```python
# setup.py for test suite
from setuptools import setup, find_packages

setup(
    name="first1kgreek-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",  # For making HTTP requests in integration tests
        "coverage",  # For measuring test coverage
    ],
    entry_points={
        'console_scripts': [
            'run-tests=run_tests:run_tests',
        ],
    },
)
```

## 8. Test Coverage Configuration

```ini
# .coveragerc
[run]
source = browse_texts_fixed.py
omit = test_*.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

## Implementation Approach

1. Start with the test environment setup to provide a foundation for all tests
2. Implement unit tests for core functionality (XML processing, metadata extraction)
3. Add integration tests to verify component interaction
4. Create end-to-end tests for complete workflows
5. Add performance tests to identify bottlenecks
6. Use coverage reports to identify untested code paths

The implementation should proceed iteratively:
1. Set up basic test infrastructure
2. Write tests for a small part of the functionality
3. Run tests and fix any issues
4. Expand test coverage to include more functionality
5. Repeat until comprehensive coverage is achieved

This approach allows immediate feedback on the health of the codebase while building toward comprehensive test coverage.
