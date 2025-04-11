"""
Configuration settings for the First1KGreek Browser.

This module contains constants and configuration settings used throughout the application.
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CSS_DIR = os.path.join(STATIC_DIR, "css")
JS_DIR = os.path.join(STATIC_DIR, "js")

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
AUTHORS_DATA_FILE = os.path.join(BASE_DIR, "authors_data.json")
USER_PREFS_FILE = os.path.join(BASE_DIR, "user_preferences.json")
LOG_FILE = "server.log"

# Data directories
BACKUP_DIR = "backup"

# File paths
CATALOG_PATH = 'catalog.json'
BACKUP_FILE = 'browse_texts_fixed.py.bak'

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True) 