#!/usr/bin/env python3
"""
First1KGreek Common Flake8 Issues Fixer

This script automatically fixes common Flake8 issues across files:
- W293: Blank line contains whitespace
- W291: Trailing whitespace
- E302: Expected 2 blank lines before function/class
"""

import os
import sys
import re
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


def fix_blank_line_issues(content):
    """Fix W293: Blank line contains whitespace."""
    lines = content.split('\n')
    for i in range(len(lines)):
        if lines[i].strip() == '':
            lines[i] = ''
    return '\n'.join(lines)


def fix_trailing_whitespace(content):
    """Fix W291: Trailing whitespace."""
    lines = content.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    return '\n'.join(lines)


def fix_spacing_errors(content):
    """Fix E302: Expected 2 blank lines before function/class."""
    # Pattern for function or class definition
    pattern = r'(\n[^\n]+)\n([^\n]*)(def|class)\s+'
    # Replace with 2 blank lines before function/class
    return re.sub(pattern, r'\1\n\n\n\3 ', content)


def fix_file(file_path, dry_run=False):
    """Fix common issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_blank_line_issues(content)
        content = fix_trailing_whitespace(content)
        content = fix_spacing_errors(content)
        
        # Only write if content has changed
        if content != original_content:
            if dry_run:
                print(f"Would fix issues in {file_path}")
                return True
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed issues in {file_path}")
                return True
        else:
            print(f"No issues found in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False


def main():
    """Process all Python files in the specified directories."""
    parser = argparse.ArgumentParser(description='Fix common Flake8 issues in Python files.')
    parser.add_argument('directories', nargs='+', help='Directories to process')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    args = parser.parse_args()
    
    print_section("Fixing common Flake8 issues")
    if args.dry_run:
        print("Dry run - no changes will be made")
    
    fixed_files = 0
    total_files = 0
    
    for directory in args.directories:
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a valid directory")
            continue
        
        files = get_python_files(directory)
        total_files += len(files)
        print(f"Found {len(files)} Python files in {directory}")
        
        for file_path in files:
            if fix_file(file_path, args.dry_run):
                fixed_files += 1
    
    print_section("Summary")
    print(f"Total files processed: {total_files}")
    print(f"Files fixed: {fixed_files}")
    
    if fixed_files > 0:
        print("✓ Successfully fixed common Flake8 issues")
    else:
        print("No files needed fixing")


if __name__ == "__main__":
    main() 