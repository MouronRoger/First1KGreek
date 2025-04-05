#!/usr/bin/env python3
"""
First1KGreek Critical Issue Fixer

This script identifies and optionally fixes critical issues in individual files.
It works on one file at a time to minimize risk of breaking functionality.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def get_critical_issues(file_path):
    """Get critical issues in the file using pylint."""
    process = subprocess.run(
        ['pylint', '--disable=all', '--enable=syntax-error,undefined-variable,unused-import', 
         '--output-format=json', file_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    try:
        if process.stdout.strip():
            issues = json.loads(process.stdout)
            return issues
        return []
    except json.JSONDecodeError:
        print(f"Error parsing pylint output: {process.stdout}")
        return []

def check_syntax(file_path):
    """Check Python syntax without executing the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        compile(source, file_path, 'exec')
        return None
    except SyntaxError as e:
        return e

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    return backup_path

def fix_unused_imports(file_path):
    """Fix unused imports in the file."""
    print(f"Checking for unused imports in {file_path}")
    
    process = subprocess.run(
        ['autoflake', '--remove-all-unused-imports', '--in-place', file_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    if process.stderr:
        print(f"Error while fixing unused imports: {process.stderr}")
        return False
    
    return True

def process_file(file_path, fix=False):
    """Process a single file to identify and optionally fix issues."""
    print_section(f"Processing {file_path}")
    
    # Check syntax first
    syntax_error = check_syntax(file_path)
    if syntax_error:
        print(f"Syntax error: {syntax_error}")
        print("Cannot safely fix this file automatically")
        return False
    
    # Get critical issues
    issues = get_critical_issues(file_path)
    
    if not issues:
        print("No critical issues found")
        return True
    
    print(f"Found {len(issues)} critical issues:")
    for issue in issues:
        print(f"Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
    
    if not fix:
        print("\nRun with --fix to attempt automatic fixes")
        return False
    
    # Create backup
    backup_path = backup_file(file_path)
    print(f"Created backup at {backup_path}")
    
    # Apply fixes
    fixed = True
    
    # Check for unused imports
    if any('unused-import' in issue.get('message', '') for issue in issues):
        if not fix_unused_imports(file_path):
            fixed = False
    
    # Re-check issues after fixes
    remaining_issues = get_critical_issues(file_path)
    
    if remaining_issues:
        print(f"\nStill have {len(remaining_issues)} issues after automatic fixes:")
        for issue in remaining_issues:
            print(f"Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
        print("\nManual intervention required")
        fixed = False
    else:
        print("\nAll critical issues fixed successfully")
    
    return fixed

def main():
    """Process files to identify and fix critical issues."""
    parser = argparse.ArgumentParser(description='Find and fix critical issues in Python files.')
    parser.add_argument('file', nargs='+', help='Python file(s) to process')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    args = parser.parse_args()
    
    # Ensure autoflake is installed
    try:
        subprocess.run(['autoflake', '--version'], capture_output=True, check=False)
    except FileNotFoundError:
        print("Installing autoflake...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'autoflake'], check=True)
    
    # Process each file
    success = True
    for file_path in args.file:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            success = False
            continue
            
        if not file_path.endswith('.py'):
            print(f"Warning: {file_path} does not appear to be a Python file, skipping")
            continue
            
        if not process_file(file_path, args.fix):
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 