#!/usr/bin/env python3
"""
First1KGreek Browser - Fixed Version
Version: 1.2.0 (with cache-busting and dark theme)
Last updated: 2025-03-07
"""

import os
import sys
import http.server
import socketserver
import json
import shutil
from html import escape
import webbrowser
from urllib.parse import parse_qs, urlparse, quote
import re
import threading
import time
import socket
import xml.etree.ElementTree as ET

# Create a backup of the file if it doesn't exist already
if not os.path.exists('browse_texts.py.bak'):
    shutil.copy('browse_texts.py', 'browse_texts.py.bak')

# Print version info when starting
print("Starting First1KGreek Browser - Fixed Version 1.2.0")
print("With dark theme and improved editor detection")

PORT = 8000

# Global reference to the server
server_instance = None

# Reader mode stylesheet
READER_STYLESHEET = """
body { 
    font-family: 'New Athena Unicode', 'GFS Artemisia', 'Arial Unicode MS', 'Lucida Sans Unicode', 'Cardo', serif; 
    margin: 0; 
    padding: 0;
    line-height: 1.8; 
    background-color: #f9f9f9; 
    color: #000000; 
}
h1, h2, h3 { 
    color: #333;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }
.container { 
    max-width: 800px; 
    margin: 0 auto; 
    padding: 20px;
    background-color: #ffffff;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    min-height: 100vh;
}
