#!/usr/bin/env python3
"""
Batch format Python files using Black.

This script reads the linting progress report and formats files that need Black formatting
in batches. It can be configured to process a specific number of files per batch.
"""

import os
import json
import argparse
import subprocess
from pathlib import Path


def load_progress_report(report_path):
    """
    Load the linting progress report.
    
    Args:
        report_path: Path to the progress report JSON file
        
    Returns:
        Dictionary containing the progress report data
    """
    with open(report_path) as f:
        return json.load(f)


def get_files_needing_black(progress_data):
    """
    Get list of files that need Black formatting.
    
    Args:
        progress_data: Progress report data dictionary
        
    Returns:
        List of file paths that need Black formatting
    """
    return [
        file_path
        for file_path, issues in progress_data["non_compliant_files"].items()
        if issues["black"]
    ]


def format_files(files, dry_run=False):
    """
    Apply Black formatting to the specified files.
    
    Args:
        files: List of files to format
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        Dictionary with results of formatting attempts
    """
    results = {
        "success": [],
        "failed": []
    }
    
    for file_path in files:
        print(f"\nFormatting {file_path}...")
        cmd = ["black"]
        if dry_run:
            cmd.append("--check")
        cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                results["success"].append(file_path)
                print("✓ Successfully formatted")
            else:
                results["failed"].append((file_path, result.stderr))
                print(f"✗ Failed to format: {result.stderr}")
        except Exception as e:
            results["failed"].append((file_path, str(e)))
            print(f"✗ Error: {e}")
    
    return results


def main():
    """Run the batch formatter."""
    parser = argparse.ArgumentParser(description="Batch format Python files using Black")
    parser.add_argument("--report", default="lint_reports/progress.json",
                       help="Path to the linting progress report")
    parser.add_argument("--batch-size", type=int, default=5,
                       help="Number of files to format in one batch")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    args = parser.parse_args()
    
    # Load progress report
    progress_data = load_progress_report(args.report)
    
    # Get files needing formatting
    files = get_files_needing_black(progress_data)
    total_files = len(files)
    
    if total_files == 0:
        print("No files need Black formatting!")
        return
    
    print(f"Found {total_files} files needing Black formatting")
    
    # Process files in batches
    for i in range(0, total_files, args.batch_size):
        batch = files[i:i + args.batch_size]
        print(f"\nProcessing batch {(i // args.batch_size) + 1}...")
        
        results = format_files(batch, args.dry_run)
        
        # Print batch summary
        print("\nBatch Summary:")
        print(f"Successfully formatted: {len(results['success'])} files")
        if results['failed']:
            print(f"Failed to format: {len(results['failed'])} files")
            for file_path, error in results['failed']:
                print(f"  - {file_path}: {error}")


if __name__ == "__main__":
    main() 