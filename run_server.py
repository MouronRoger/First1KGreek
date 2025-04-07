#!/usr/bin/env python3
"""
Simple script to run the First1KGreek Browser server.
This directly uses the modular structure in src/first1k.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the server module from src.first1k
try:
    from src.first1k.server.server import run_server
    print("Starting First1KGreek Browser...")
    run_server()
except ImportError as e:
    print(f"Error importing server module: {e}")
    print("Try running with: PYTHONPATH=. python run_server.py")
    sys.exit(1)
except Exception as e:
    print(f"Error running server: {e}")
    sys.exit(1) 