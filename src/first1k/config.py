"""
First1KGreek Browser Configuration
Version: 1.2.0
Last updated: 2025-03-07
"""

import os

# Server configuration
PORT = 8000

# Styling
READER_STYLESHEET = """
body { 
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.8; 
    background-color: #2a2a2a; 
    color: #f2f2f2; 
}
h1, h2, h3 { 
    color: #fff;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #4299e1; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 800px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #333;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    min-height: 100vh;
}
"""

MAIN_STYLESHEET = """
body { 
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.6; 
    background-color: #1a1a1a; 
    color: #ffffff; 
}
h1, h2, h3 { 
    color: #4299e1;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #4299e1; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 1000px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #2d2d2d;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    min-height: 100vh;
}
"""

# Data directories
DATA_DIR = "data"
BACKUP_DIR = "backup"

# File paths
CATALOG_PATH = "catalog.json"
BACKUP_FILE = "browse_texts.py.bak"

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
