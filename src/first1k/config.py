"""
Configuration settings for the First1KGreek Browser.

This module contains constants and configuration settings used throughout the application.
"""

import os

# Server configuration
PORT = 8000  # Default port
HOST = "localhost"
SHUTDOWN_PATH = "/shutdown"
DEBUG = False  # Default debug flag

# Version information
VERSION = "1.2.0"
VERSION_NAME = "Fixed Version"
LAST_UPDATED = "2025-03-07"
FEATURES = "with dark theme and improved editor detection"

# Paths
AUTHORS_DATA_FILE = "authors_data.json"
USER_PREFS_FILE = "user_preferences.json"
LOG_FILE = "server.log"
DATA_DIR = "data"
STATIC_DIR = "static"
CSS_DIR = f"{STATIC_DIR}/css"
JS_DIR = f"{STATIC_DIR}/js"

# Data directories
BACKUP_DIR = "backup"

# File paths
CATALOG_PATH = 'catalog.json'
BACKUP_FILE = 'browse_texts_fixed.py.bak'

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True) 