#!/usr/bin/env python3
"""Advisory linting tool for First1KGreek repository.

This script runs pylint in advisory mode on specific files without making
automated changes. It is designed to gradually improve code quality while
ensuring that existing functionality is not broken.
"""

import os
import sys
import argparse
import subprocess
import datetime
from collections import defaultdict


def run_pylint(target_files, error_only=False, summary=False):
    """
    Run pylint on target files in advisory mode.

    Args:
        target_files: List of files to lint
        error_only: If True, only show errors (not warnings)
        summary: If True, only show summary statistics

    Returns:
        Dictionary with lint results by file
    """
    results = defaultdict(list)
    
    for file_path in target_files:
        # Skip XML files with a special warning
        if file_path.lower().endswith('.xml'):
            print(f"⚠️  WARNING: XML file detected: {file_path}")
            print("    XML files must NEVER be linted or modified by automated tools.")
            print("    These files contain critical data and must maintain exact formatting.")
            continue
            
        # Skip non-Python files
        if not file_path.endswith('.py'):
            print(f"Skipping non-Python file: {file_path}")
            continue

        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            continue
            
        cmd = ["pylint"]
        
        # Configure command based on options
        if error_only:
            cmd.extend(["--disable=all", "--enable=F,E"])
        
        # Add the file to check
        cmd.append(file_path)
        
        try:
            # Run pylint and capture output
            output = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=False
            )
            
            # Store results
            results[file_path] = output.stdout.splitlines()
            
            # Print results if not summary-only mode
            if not summary:
                print(f"\n=== Linting: {file_path} ===")
                print(output.stdout)
        except subprocess.SubprocessError as e:
            print(f"Error running pylint on {file_path}: {e}")
    
    return results


def generate_summary(results):
    """
    Generate a summary of lint results.

    Args:
        results: Dictionary with lint results by file

    Returns:
        None, prints summary to stdout
    """
    print("\n=== LINT SUMMARY ===")
    
    total_issues = 0
    files_with_issues = 0
    
    for file_path, lines in results.items():
        # Count non-empty lines that don't contain the rating
        issues = [l for l in lines if l.strip() and "rated at" not in l]
        issue_count = len(issues)
        
        if issue_count > 0:
            files_with_issues += 1
            total_issues += issue_count
            print(f"{file_path}: {issue_count} issues")
    
    print(f"\nTotal: {total_issues} issues in {files_with_issues} files")
    print("\nNOTE: These are advisory warnings only. Fix issues incrementally")
    print("and ensure that each change doesn't break existing functionality.")


def update_quality_tracker(results, output_file="code_quality.md"):
    """
    Update the code quality tracking markdown file with lint results.

    Args:
        results: Dictionary with lint results by file
        output_file: Path to the code quality markdown file

    Returns:
        None, updates the quality tracking file
    """
    if not os.path.exists(output_file):
        print(f"Error: Quality tracking file {output_file} does not exist")
        return
    
    # Read the current content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Find the Python Files section
    try:
        python_files_start = next(i for i, line in enumerate(content) if "## Python Files" in line)
        next_section_start = next(i for i, line in enumerate(content[python_files_start:], python_files_start) 
                               if line.startswith("## ") and "Python Files" not in line)
    except StopIteration:
        print("Error: Could not find Python Files section or next section in quality tracker")
        return
    
    # Extract existing files data
    files_section = content[python_files_start:next_section_start]
    
    # Look for table header
    try:
        table_start = next(i for i, line in enumerate(files_section) if "|---" in line)
        files_table = files_section[table_start - 1:]  # Include header
    except StopIteration:
        print("Error: Could not find files table in quality tracker")
        return
    
    # Parse existing files data
    file_data = {}
    for line in files_table[2:]:  # Skip header and separator
        if '|' not in line or not line.strip():
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5:  # Should have 5 parts including empty parts at start/end
            file_path = parts[1]
            file_data[file_path] = {
                'status': parts[2],
                'last_reviewed': parts[3],
                'notes': parts[4]
            }
    
    # Update file data with new results
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    for file_path, lines in results.items():
        # Get the simple filename
        filename = os.path.basename(file_path)
        
        # Check if there are issues
        issues = [l for l in lines if l.strip() and "rated at" not in l]
        issue_count = len(issues)
        
        # Determine rating
        if issue_count == 0:
            status = "✅"
            notes = "Fully compliant"
        else:
            # Check if there are errors (E:) vs just warnings/conventions
            has_errors = any("E:" in line for line in issues)
            if has_errors:
                status = "⚠️"
                notes = f"Contains {issue_count} issues including errors"
            else:
                status = "🔄"
                notes = f"Contains {issue_count} style/warning issues"
        
        # Update or add file entry
        if filename in file_data:
            # Update existing entry
            file_data[filename].update({
                'status': status,
                'last_reviewed': today,
                'notes': notes
            })
        else:
            # Add new entry
            file_data[filename] = {
                'status': status,
                'last_reviewed': today,
                'notes': notes
            }
    
    # Generate updated table
    updated_table = [files_table[0], files_table[1]]  # Header and separator
    for filename, data in sorted(file_data.items()):
        updated_table.append(f"| {filename} | {data['status']} | {data['last_reviewed']} | {data['notes']} |\n")
    
    # Construct updated content
    updated_content = (
        content[:python_files_start + 1] +  # Everything before the Python Files section + the section header
        ["\n"] +  # Add a newline after the section header
        updated_table +  # The updated table
        ["\n"] +  # Add a newline after the table
        content[next_section_start:]  # Everything after the Python Files section
    )
    
    # Write updated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_content)
    
    print(f"\nUpdated quality tracking file: {output_file}")


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description='Run pylint in advisory mode for First1KGreek repository.'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Files to lint (only Python .py files will be processed)'
    )
    parser.add_argument(
        '--error-only',
        action='store_true',
        help='Only show errors (E) and fatal errors (F), not warnings'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Only show summary of lint results'
    )
    parser.add_argument(
        '--update-tracker',
        action='store_true',
        help='Update the code quality tracking file with results'
    )
    parser.add_argument(
        '--tracker-file',
        default='code_quality.md',
        help='Path to code quality tracking file'
    )
    
    args = parser.parse_args()
    
    # Check for XML files first with a special warning
    xml_files = [f for f in args.files if f.lower().endswith('.xml')]
    if xml_files:
        print("\n⚠️  WARNING: XML FILES DETECTED ⚠️")
        print("The following XML files will be skipped and NOT linted:")
        for xml_file in xml_files:
            print(f"  - {xml_file}")
        print("\nXML files contain critical data and must never be processed by linting tools.")
        print("====================================================================\n")
    
    # Filter out non-Python files with a warning
    python_files = []
    for file_path in args.files:
        if file_path.endswith('.py'):
            python_files.append(file_path)
        elif not file_path.lower().endswith('.xml'):  # XML files already warned about
            print(f"Skipping non-Python file: {file_path}")
    
    if not python_files:
        print("No Python files to lint. Exiting.")
        return 0
    
    results = run_pylint(python_files, args.error_only, args.summary)
    
    if args.summary or len(python_files) > 1:
        generate_summary(results)
    
    if args.update_tracker:
        update_quality_tracker(results, args.tracker_file)
    
    # Always exit successfully - never block a commit
    return 0


if __name__ == "__main__":
    sys.exit(main()) 