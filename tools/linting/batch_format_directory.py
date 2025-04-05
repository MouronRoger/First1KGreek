#!/usr/bin/env python3
"""
First1KGreek Batch Directory Formatter

This script formats all Python files in a specified directory,
running tests after each file to ensure functionality is preserved.
"""

import os
import sys
import subprocess
import argparse
import glob
from pathlib import Path


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def get_python_files(directory):
    """Get all Python files in the specified directory."""
    return [f for f in glob.glob(f"{directory}/**/*.py", recursive=True)]


def format_file(file_path, dry_run=False):
    """Format a file using the incremental formatter."""
    print(f"Processing {file_path}...")
    
    cmd = [sys.executable, "tools/linting/format_incremental.py", file_path]
    if dry_run:
        cmd.append("--dry-run")
    
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )
    
    if process.returncode != 0:
        print(f"❌ Formatting failed for {file_path}")
        print(process.stderr)
        return False
    
    print(f"✓ Successfully formatted {file_path}")
    return True


def main():
    """Process all Python files in the specified directory."""
    parser = argparse.ArgumentParser(description='Format all Python files in a directory.')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print_section(f"Formatting Python files in {args.directory}")
    if args.dry_run:
        print("Dry run - no changes will be made")
    
    files = get_python_files(args.directory)
    if not files:
        print(f"No Python files found in {args.directory}")
        sys.exit(0)
    
    print(f"Found {len(files)} Python files to process")
    
    successful = 0
    failed = 0
    
    for file_path in files:
        if args.verbose:
            print(f"\nProcessing {file_path}...")
        
        if format_file(file_path, args.dry_run):
            successful += 1
        else:
            failed += 1
    
    print_section("Summary")
    print(f"Total files: {len(files)}")
    print(f"Successfully formatted: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 