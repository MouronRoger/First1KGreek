#!/usr/bin/env python3
"""
Safely clean up duplicate directories and non-XML files.

IMPORTANT: This script will NOT delete any XML files, as per repository guidelines.
It only removes empty directories matching the pattern and non-XML duplicate files.
"""

import os
import re
import sys
import argparse
import shutil
from collections import defaultdict


def find_duplicates(root_dir, pattern=r'.*\s+\d+.*'):
    """
    Find files and directories matching the pattern.

    Args:
        root_dir: Root directory to search in
        pattern: Regex pattern to match against filenames/dirnames

    Returns:
        Dictionary with duplicate counts by type
    """
    pattern_re = re.compile(pattern)
    duplicates = defaultdict(list)
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Check directory names
        for dirname in dirnames:
            if pattern_re.match(dirname):
                full_path = os.path.join(dirpath, dirname)
                duplicates['directories'].append(full_path)
        
        # Check file names
        for filename in filenames:
            if pattern_re.match(filename):
                full_path = os.path.join(dirpath, filename)
                if filename.endswith('.xml'):
                    duplicates['xml_files'].append(full_path)
                else:
                    duplicates['other_files'].append(full_path)
    
    return duplicates


def is_directory_empty(dir_path):
    """Check if a directory is empty."""
    return len(os.listdir(dir_path)) == 0


def cleanup_duplicates(root_dir, pattern=r'.*\s+\d+.*', dry_run=True):
    """
    Clean up duplicate files and directories.
    
    Args:
        root_dir: Root directory to clean
        pattern: Regex pattern to match against filenames/dirnames
        dry_run: If True, only print what would be done without actual deletion
        
    Returns:
        Dictionary with cleanup statistics
    """
    duplicates = find_duplicates(root_dir, pattern)
    stats = {
        'xml_files_skipped': len(duplicates['xml_files']),
        'other_files_removed': 0,
        'empty_dirs_removed': 0,
        'non_empty_dirs_skipped': 0
    }
    
    # Warn about XML files (we don't delete these)
    if duplicates['xml_files']:
        print(f"Found {len(duplicates['xml_files'])} XML files matching the pattern.")
        print("SKIPPING ALL XML FILES per repository guidelines.")
    
    # Process non-XML files
    for file_path in duplicates['other_files']:
        if dry_run:
            print(f"Would remove file: {file_path}")
        else:
            try:
                os.remove(file_path)
                print(f"Removed file: {file_path}")
                stats['other_files_removed'] += 1
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
    
    # Process directories (only if empty)
    for dir_path in duplicates['directories']:
        if is_directory_empty(dir_path):
            if dry_run:
                print(f"Would remove empty directory: {dir_path}")
            else:
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                    stats['empty_dirs_removed'] += 1
                except Exception as e:
                    print(f"Error removing {dir_path}: {e}")
        else:
            print(f"Skipping non-empty directory: {dir_path}")
            stats['non_empty_dirs_skipped'] += 1
    
    return stats


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description='Clean up duplicate files and directories with space-number pattern.'
    )
    parser.add_argument(
        'root_dir',
        help='Root directory to clean'
    )
    parser.add_argument(
        '--pattern', 
        default=r'.*\s+\d+.*', 
        help='Regex pattern to match against filenames/dirnames'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Only print what would be done without actual deletion'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.root_dir):
        print(f"Error: {args.root_dir} is not a valid directory")
        sys.exit(1)
    
    print(f"{'DRY RUN: ' if args.dry_run else ''}Cleaning up duplicates in {args.root_dir}...")
    print("IMPORTANT: XML files will NOT be deleted per repository guidelines.")
    
    stats = cleanup_duplicates(args.root_dir, args.pattern, args.dry_run)
    
    print("\nCleanup Summary:")
    print(f"- XML files skipped: {stats['xml_files_skipped']}")
    print(f"- Other files {'would be' if args.dry_run else ''} removed: {stats['other_files_removed']}")
    print(f"- Empty directories {'would be' if args.dry_run else ''} removed: {stats['empty_dirs_removed']}")
    print(f"- Non-empty directories skipped: {stats['non_empty_dirs_skipped']}")
    
    if not args.dry_run:
        print("\nCleanup completed successfully.")
    else:
        print("\nThis was a dry run. No files were actually deleted.")
        print("Run without --dry-run to perform the actual cleanup.")
    
    print("\nNOTE: XML files were preserved according to repository guidelines.")


if __name__ == "__main__":
    main() 