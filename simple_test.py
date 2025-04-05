#!/usr/bin/env python3
"""Simple test to verify unittest functionality."""

import os
import unittest


class SimpleTest(unittest.TestCase):
    """A simple test case to verify unittest functionality."""

    def test_basic_assert(self):
        """Test that basic assertions work."""
        self.assertEqual(1, 1)
        self.assertTrue(True)
        self.assertFalse(False)

    def test_file_existence(self):
        """Test that we can verify file existence."""
        self.assertTrue(os.path.exists("browse_texts_fixed.py"))


if __name__ == "__main__":
    unittest.main()
