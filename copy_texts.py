#!/usr/bin/env python3
import os
import shutil
import sys

def copy_directory_structure(source_dir, dest_dir):
    """
    Copy all TLG files from source_dir to dest_dir, preserving the directory structure.
    """
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")

    # Count variables for reporting
    total_files = 0
    total_copied = 0
    errors = []

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        # Create relative path to maintain structure
        rel_path = os.path.relpath(root, source_dir)
        if rel_path == '.':
            rel_path = ''
            
        # Create corresponding directory in destination
        dest_path = os.path.join(dest_dir, rel_path)
        if not os.path.exists(dest_path) and rel_path:
            os.makedirs(dest_path)
            print(f"Created directory: {dest_path}")
            
        # Copy each file
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            
            total_files += 1
            
            # Skip if destination file exists (optional - remove if you want to overwrite)
            if os.path.exists(dest_file):
                print(f"Skipping (already exists): {dest_file}")
                continue
                
            try:
                shutil.copy2(source_file, dest_file)
                print(f"Copied: {source_file} -> {dest_file}")
                total_copied += 1
            except Exception as e:
                error_msg = f"Error copying {source_file}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
    
    # Print summary
    print("\n--- Summary ---")
    print(f"Total files: {total_files}")
    print(f"Files copied: {total_copied}")
    print(f"Files skipped or errors: {total_files - total_copied}")
    
    if errors:
        print("\n--- Errors ---")
        for error in errors:
            print(error)


if __name__ == "__main__":
    # Paths
    source_dir = "/Users/james/Documents/GitHub/First1KGreek/data_copy"
    dest_dir = "/Users/james/Documents/GitHub/First1KGreek/data"
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist!")
        sys.exit(1)
        
    # Confirm with user
    print(f"This will copy files from '{source_dir}' to '{dest_dir}'")
    confirm = input("Continue? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
        
    # Perform the copy
    copy_directory_structure(source_dir, dest_dir)
    print("\nCopy operation completed!")
    print("You can now run browse_texts.py to view the newly added texts.") 