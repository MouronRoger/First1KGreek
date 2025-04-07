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
:root {
    --background: #2a2a2a;
    --foreground: #f2f2f2;
    --surface: #333;
    --primary: #4299e1;
}

body {
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif;
    margin: 0;
    padding: 0;
    line-height: 1.8;
    background-color: var(--background);
    color: var(--foreground);
}
h1, h2, h3 {
    color: #fff;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--surface);
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
    min-height: 100vh;
}
"""

MAIN_STYLESHEET = """
:root {
    --background: #1a1a1a;
    --foreground: #ffffff;
    --primary: #4299e1;
    --accent: #805ad5;
    --success: #48bb78;
    --warning: #ed8936;
    --error: #f56565;
    --surface: #2d2d2d;
    --surface-light: #333;
    --surface-dark: #222;
    --text-light: #f2f2f2;
    --text-dim: #a0aec0;
    --border: #444;
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    background-color: var(--background);
    color: var(--foreground);
}
h1, h2, h3 {
    color: var(--primary);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--surface);
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
