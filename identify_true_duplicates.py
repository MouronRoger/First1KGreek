#!/usr/bin/env python3
"""
Identify true duplicate XML files based on specific criteria.

This script finds XML files with " 2.xml" or " 3.xml" in their names and checks if they are
true duplicates of corresponding files without the " 2" or " 3" suffix by comparing:
1. File existence in same directory
2. File size
3. File modification date

IMPORTANT: This script will NOT delete any files automatically unless specifically requested.
Repository guidelines indicate that XML files should not be deleted without explicit permission.
"""

import os
import re
import sys
import argparse
from collections import defaultdict
from datetime import datetime


def find_true_duplicates(root_dir, pattern=r'(.*)\s+([23])(\.xml)$'):
    """
    Find true duplicate XML files based on specific criteria.

    Args:
        root_dir: Root directory to search in
        pattern: Regex pattern to match files with " 2.xml" or " 3.xml" suffix

    Returns:
        Dictionary of true duplicates with verification info
    """
    pattern_re = re.compile(pattern)
    true_duplicates = []
    
    print(f"Searching for potential duplicate XML files in {root_dir}...")
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            match = pattern_re.match(filename)
            if match:
                # Extract the base name without " 2" or " 3" suffix
                base_name = match.group(1) + match.group(3)
                duplicate_path = os.path.join(dirpath, filename)
                original_path = os.path.join(dirpath, base_name)
                
                # Check if original file exists
                if os.path.exists(original_path):
                    # Get file stats
                    duplicate_stat = os.stat(duplicate_path)
                    original_stat = os.stat(original_path)
                    
                    # Compare size and modification time
                    same_size = duplicate_stat.st_size == original_stat.st_size
                    same_mtime = abs(duplicate_stat.st_mtime - original_stat.st_mtime) < 1  # Allow 1 second difference
                    
                    # Format modification times
                    dup_mtime = datetime.fromtimestamp(duplicate_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    orig_mtime = datetime.fromtimestamp(original_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Store results
                    true_duplicates.append({
                        'duplicate_path': duplicate_path,
                        'original_path': original_path,
                        'same_size': same_size,
                        'same_mtime': same_mtime,
                        'is_true_duplicate': same_size and same_mtime,
                        'duplicate_size': duplicate_stat.st_size,
                        'original_size': original_stat.st_size,
                        'duplicate_mtime': dup_mtime,
                        'original_mtime': orig_mtime
                    })
    
    return true_duplicates


def print_duplicate_info(duplicates):
    """Print detailed information about found duplicates."""
    true_count = sum(1 for d in duplicates if d['is_true_duplicate'])
    
    print(f"\nFound {len(duplicates)} potential duplicates.")
    print(f"Of these, {true_count} are confirmed true duplicates.")
    
    if not duplicates:
        return
    
    print("\nDetailed duplicate information:")
    print("-" * 80)
    
    for i, dup in enumerate(duplicates, 1):
        status = "TRUE DUPLICATE" if dup['is_true_duplicate'] else "NOT A TRUE DUPLICATE"
        print(f"Duplicate #{i}: {status}")
        print(f"  Original: {dup['original_path']}")
        print(f"  Duplicate: {dup['duplicate_path']}")
        print(f"  Same size: {dup['same_size']} ({dup['original_size']} bytes)")
        print(f"  Same modification time: {dup['same_mtime']}")
        print(f"    Original: {dup['original_mtime']}")
        print(f"    Duplicate: {dup['duplicate_mtime']}")
        print("-" * 80)


def remove_duplicates(duplicates, dry_run=True):
    """
    Remove confirmed duplicate files.
    
    Args:
        duplicates: List of duplicate info dictionaries
        dry_run: If True, only print actions without removing files
        
    Returns:
        Count of files removed
    """
    removed_count = 0
    true_duplicates = [d for d in duplicates if d['is_true_duplicate']]
    
    if not true_duplicates:
        print("No true duplicates found to remove.")
        return 0
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Removing {len(true_duplicates)} true duplicate files:")
    
    for dup in true_duplicates:
        if dry_run:
            print(f"Would remove: {dup['duplicate_path']}")
        else:
            try:
                os.remove(dup['duplicate_path'])
                print(f"Removed: {dup['duplicate_path']}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {dup['duplicate_path']}: {e}")
    
    return removed_count


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description='Identify and manage true duplicate XML files.'
    )
    parser.add_argument(
        'root_dir',
        help='Root directory to search in'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Only print what would be done without actual deletion'
    )
    parser.add_argument(
        '--remove', 
        action='store_true',
        help='Remove confirmed true duplicates (requires explicit permission)'
    )
    parser.add_argument(
        '--pattern', 
        default=r'(.*)\s+([23])(\.xml)$',
        help='Regex pattern to match duplicate files'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.root_dir):
        print(f"Error: {args.root_dir} is not a valid directory")
        sys.exit(1)
    
    duplicates = find_true_duplicates(args.root_dir, args.pattern)
    print_duplicate_info(duplicates)
    
    if args.remove:
        if not args.dry_run:
            confirm = input("Are you sure you want to remove these duplicate files? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("Aborting operation.")
                sys.exit(0)
        
        removed = remove_duplicates(duplicates, args.dry_run)
        
        if args.dry_run:
            print(f"\nDry run completed. {removed} files would be removed.")
            print("Run without --dry-run and with --remove to perform actual deletion.")
        else:
            print(f"\nOperation completed. {removed} duplicate files were removed.")
    else:
        print("\nNo files were removed. Use --remove to delete true duplicates.")
        print("REMINDER: Repository guidelines require explicit permission to delete XML files.")
    
    # Summary
    true_count = sum(1 for d in duplicates if d['is_true_duplicate'])
    print(f"\nSummary:")
    print(f"- Total potential duplicates: {len(duplicates)}")
    print(f"- Confirmed true duplicates: {true_count}")
    if args.remove and not args.dry_run:
        print(f"- Files removed: {true_count}")
    
    print("\nNOTE: This script identifies duplicates based on specific criteria.")
    print("True duplicates have identical size and modification time.")


if __name__ == "__main__":
    main() 