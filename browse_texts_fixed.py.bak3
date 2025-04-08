#!/usr/bin/env python3
"""
First1KGreek Browser - Fixed Version

A web-based tool for browsing, searching, and viewing texts from the First 1000 Years of Greek project.
This application provides a clean interface for navigating the corpus, with features for:
- Browsing authors by name, century, and type
- Managing author preferences (favorites, archived)
- Viewing works and their content in both raw and readable formats
- Simple search functionality

Version: 1.2.0 (with cache-busting and dark theme)
Last updated: 2025-03-07

NOTE: This is now a wrapper around the modular implementation.
The actual functionality is in the src/first1k/ package.
"""

import sys
import logging

# Add the current directory to the Python path
sys.path.insert(0, '.')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

try:
    # Import the modular implementation
    from src.first1k.__main__ import main
    logger.info("Successfully imported modular implementation")
except ImportError as e:
    logger.error(f"Error importing modular implementation: {e}")
    logger.error("Please make sure the src/first1k package is installed")
    sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting First1KGreek Browser using modular implementation")
    main() 