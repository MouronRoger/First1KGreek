#!/usr/bin/env python3
"""Find duplicate files following the pattern of a space followed by a number in filename/dirname."""

import os
import re
import sys
import argparse
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
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
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


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description='Find duplicate files with space-number pattern.'
    )
    parser.add_argument(
        'root_dir',
        help='Root directory to search in'
    )
    parser.add_argument(
        '--pattern', 
        default=r'.*\s+\d+.*', 
        help='Regex pattern to match against filenames/dirnames'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Print full paths instead of just summary'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.root_dir):
        print(f"Error: {args.root_dir} is not a valid directory")
        sys.exit(1)
    
    print(f"Searching for duplicates in {args.root_dir}...")
    duplicates = find_duplicates(args.root_dir, args.pattern)
    
    print("\nSummary:")
    print(f"- XML files: {len(duplicates['xml_files'])}")
    print(f"- Other files: {len(duplicates['other_files'])}")
    print(f"- Directories: {len(duplicates['directories'])}")
    print(f"Total: {sum(len(v) for v in duplicates.values())}")
    
    if args.verbose:
        print("\nXML Files:")
        for path in sorted(duplicates['xml_files']):
            print(f"  {path}")
        
        print("\nOther Files:")
        for path in sorted(duplicates['other_files']):
            print(f"  {path}")
        
        print("\nDirectories:")
        for path in sorted(duplicates['directories']):
            print(f"  {path}")
    
    print("\nCAUTION: This script only identifies potential duplicates.")
    print("Review carefully before taking any action.")
    print("IMPORTANT: Repository documentation indicates that XML files")
    print("should not be deleted without explicit permission.")


if __name__ == "__main__":
    main() 